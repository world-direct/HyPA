import concurrent.futures
import csv
import os.path
import sys
import time
from datetime import datetime

from apscheduler.schedulers.background import BlockingScheduler

import values
from connectors.cdr_connector import CdrConnector
from connectors.kubernetes_connector import KubernetesConnector
from logger import get_module_logger

logger = get_module_logger(__name__)


def write_to_csv(file_path: str, timestamp: int, cpu_request_value: int | None,
                 cpu_limit_value: int | None, replicas_value: int | None,
                 latency_values: list[float],
                 cpu_utilization_values: list[float | None],
                 replica_poll_values: list[float | None]):
    with open(file_path, 'a+', newline='') as csvfile:
        spamwriter = csv.writer(csvfile,
                                delimiter=';',
                                quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([
            timestamp, cpu_request_value, cpu_limit_value, replicas_value,
            latency_values, cpu_utilization_values, replica_poll_values
        ])


class Eval:

    def __init__(self, log_directory: str, poll_interval: int,
                 log_interval: float):
        super(Eval, self).__init__()

        self.kubernetes_connectors: dict[str, KubernetesConnector] = {
            values.Competitors.HPA.name:
            KubernetesConnector(namespace=values.EVALUTAION_DEPLOYMENTS[
                values.Competitors.HPA.name].namespace,
                                service_name=values.SERVICE_NAME),
            values.Competitors.MOHA.name:
            KubernetesConnector(namespace=values.EVALUTAION_DEPLOYMENTS[
                values.Competitors.MOHA.name].namespace,
                                service_name=values.SERVICE_NAME),
            values.Competitors.HYPA.name:
            KubernetesConnector(namespace=values.EVALUTAION_DEPLOYMENTS[
                values.Competitors.HYPA.name].namespace,
                                service_name=values.SERVICE_NAME),
        }

        self.cdr_connector: dict[str, CdrConnector] = {
            values.Competitors.HPA.name:
            self._init_cdr_connector(values.Competitors.HPA.name),
            values.Competitors.MOHA.name:
            self._init_cdr_connector(values.Competitors.MOHA.name),
            values.Competitors.HYPA.name:
            self._init_cdr_connector(values.Competitors.HYPA.name)
        }

        self.cpu_metrics: dict[str, list[float | None]] = {
            values.Competitors.HPA.name: [],
            values.Competitors.MOHA.name: [],
            values.Competitors.HYPA.name: []
        }

        self.replica_poll_values: dict[str, list[float | None]] = {
            values.Competitors.HPA.name: [],
            values.Competitors.MOHA.name: [],
            values.Competitors.HYPA.name: []
        }

        self.poll_interval = poll_interval
        self.log_interval = log_interval
        self.log_directory = log_directory
        self.number_poll_before_write = int(log_interval / poll_interval)

        self.file_paths: dict[str, str] = {
            values.Competitors.HPA.name:
            self._generate_csv_file_path(values.Competitors.HPA.name),
            values.Competitors.MOHA.name:
            self._generate_csv_file_path(values.Competitors.MOHA.name),
            values.Competitors.HYPA.name:
            self._generate_csv_file_path(values.Competitors.HYPA.name),
        }

    def poll_metrics(self):
        cpu_polls = 0
        with (concurrent.futures.ThreadPoolExecutor(max_workers=3) as
              executor):
            results = [
                executor.submit(self._check_cpu_for_method, competitor.name)
                for competitor in list(values.Competitors)
            ]

            for result in concurrent.futures.as_completed(results):
                cpu_polls = result.result()

            if cpu_polls == self.number_poll_before_write:
                self.log_metrics()

    def log_metrics(self):
        timestamp = int(time.time())
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            results = [
                executor.submit(self._log_values_for_method, competitor.name,
                                timestamp)
                for competitor in list(values.Competitors)
            ]

            for result in concurrent.futures.as_completed(results):
                pass

    def start_evaluation(self):
        blocking_scheduler = BlockingScheduler()

        blocking_scheduler.add_job(self.poll_metrics,
                                   'interval',
                                   seconds=self.poll_interval)

        blocking_scheduler.start()

    def _check_cpu_for_method(self, method: str) -> int:
        asterisk_config = self.kubernetes_connectors[
            method].get_current_resource_configuration()
        current_replica = asterisk_config[4]
        cpu_metric = self._try_get_current_cpu_metric(method,
                                                      asterisk_config[1],
                                                      current_replica)

        cpu_metric = min(cpu_metric,
                         1.0) if cpu_metric is not None else cpu_metric
        logger.debug(f"{method} - Cpu utilization: {cpu_metric}")
        self.cpu_metrics[method].append(cpu_metric)
        self.replica_poll_values[method].append(current_replica)
        return len(self.cpu_metrics[method])

    def _log_values_for_method(self, method: str, timestamp: int):
        logger.debug(f"{method} - Write metrics to csv")
        asterisk_config = self.kubernetes_connectors[
            method].get_current_resource_configuration()
        current_replica = asterisk_config[4]
        current_request = asterisk_config[0]
        current_limit = asterisk_config[1]

        latencies = self._try_get_call_latencies(method)
        logger.debug(f"{method} - Latencies: {latencies}")

        write_cpu_metrics = self.cpu_metrics[method][:]
        self.cpu_metrics[method].clear()

        write_replica_poll_values = self.replica_poll_values[method][:]
        self.replica_poll_values[method].clear()

        logger.debug(
            f"{method} - Got {len(write_cpu_metrics)} cpu vales: {write_cpu_metrics}"
        )

        write_to_csv(file_path=self.file_paths[method],
                     timestamp=timestamp,
                     cpu_request_value=current_request,
                     cpu_limit_value=current_limit,
                     replicas_value=current_replica,
                     latency_values=latencies,
                     cpu_utilization_values=write_cpu_metrics,
                     replica_poll_values=write_replica_poll_values)

    def _init_cdr_connector(self, method: str) -> CdrConnector:
        deployment = values.EVALUTAION_DEPLOYMENTS[method]
        while True:
            try:
                return CdrConnector(namespace=deployment.namespace,
                                    username=deployment.cdr_db_user,
                                    password=deployment.cdr_db_password,
                                    host=values.CDR_HOST,
                                    port=values.CDR_PORT)
            except Exception as e:
                logger.error(
                    f"Error during CDR connector initialization => Wait {values.CONNECTION_RETRY_TIMER}s and try again\n{e}"
                )
                time.sleep(values.CONNECTION_RETRY_TIMER)

    def _generate_csv_file_path(self, method):
        file_name = f"{method}_{datetime.today().strftime('%d-%m-%Y')}_{self.poll_interval}_{self.log_interval}.csv"
        return os.path.join(self.log_directory, file_name)

    def _try_get_call_latencies(self, method: str) -> list[float]:
        logger.debug(f"Get latencies of namespace: {method}")

        while True:
            try:
                result = self.cdr_connector[
                    method].get_latest_latencies_of_interval(interval=int(
                        self.log_interval),
                                                             unit="SECOND")

                return result
            except TimeoutError:
                logger.error(f"{method} - Timeout during latency query")
                self.cdr_connector[method] = self._init_cdr_connector(
                    method=method)
            except:
                logger.error(
                    f"{method} - Unexpected error: {sys.exc_info()[0]}")
                self.cdr_connector[method] = self._init_cdr_connector(
                    method=method)

    def _try_get_current_cpu_metric(self, method: str,
                                    current_cpu_limit: float,
                                    current_replica) -> float | None:
        try:
            cpu_usage = self.kubernetes_connectors[
                method].get_current_cpu_and_memory_utilization()[0]

            return round(cpu_usage / (current_cpu_limit * current_replica),
                         2) if cpu_usage is not None else cpu_usage
        except TimeoutError:
            logger.error(f"{method} - Timeout during CPU utilization query")
        except:
            logger.error(f"{method} - Unexpected error: {sys.exc_info()[0]}")
