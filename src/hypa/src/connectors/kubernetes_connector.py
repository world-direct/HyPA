import datetime
import os
import time

import numpy as np
import urllib3
from kubernetes import client, config
from timeout_function_decorator import timeout

import values
from logger import get_module_logger

logger = get_module_logger(__name__)

urllib3.disable_warnings()


class KubernetesConnector:
    """Kubernetes connector to access Kubernetes APIs"""

    def __init__(self, namespace, service_name):
        config.load_kube_config()

        self.apps_v1_api = client.AppsV1Api()
        self.custom_object_api = client.CustomObjectsApi()

        self.namespace = namespace
        self.service_name = service_name

    def get_current_resource_configuration(
        self
    ) -> tuple[int | None, int | None, int | None, int | None, int | None]:
        try:
            stateful_set = self.apps_v1_api.read_namespaced_stateful_set(
                name=self.service_name, namespace=self.namespace)

            cpu_request = None
            cpu_limit = None
            memory_request = None
            memory_limit = None

            for container in stateful_set.spec.template.spec.containers:
                if container.name != self.service_name:
                    continue

                resources = container.resources

                if resources and resources.requests:
                    cpu_request = resources.requests.get('cpu', None)
                    memory_request = resources.requests.get('memory', None)
                if resources and resources.limits:
                    cpu_limit = resources.limits.get('cpu', None)
                    memory_limit = resources.limits.get('memory', None)

            replicas = stateful_set.spec.replicas

            return int(cpu_request[:-1]), int(cpu_limit[:-1]), int(
                memory_request[:-2]), int(memory_limit[:-2]), int(replicas)
        except client.rest.ApiException as e:
            logger.error(
                f"An error occured while reading resource configuration: {e}")
            return None, None, None, None, None

    def get_current_cpu_and_memory_utilization(
            self) -> tuple[float | None, float | None]:
        try:
            pod_list = self.custom_object_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=self.namespace,
                plural="pods")

            cpu_usage_millicores: float = 0.0
            memory_usage_megabytes: float = 0.0

            for item in pod_list["items"]:
                if self.service_name in item["metadata"]["name"]:
                    for container in item["containers"]:
                        cpu_usage_nanocores: str = container["usage"]["cpu"]
                        cpu_usage_millicores += float(
                            cpu_usage_nanocores[:-1]) / 1000000

                        memory_usage_kilobytes: str = container["usage"][
                            "memory"]

                        memory_usage_megabytes += float(
                            memory_usage_kilobytes[:-2]) / 1000

            if cpu_usage_millicores == 0.0 and memory_usage_megabytes == 0.0:
                return None, None

            return np.ceil(cpu_usage_millicores), np.ceil(
                memory_usage_megabytes)
        except client.rest.ApiException as e:
            logger.error(
                f"An error occured while reading CPU utilization: {e}")
            return None, None

    def try_scale_deployment(self,
                             replicas: int = 1,
                             cpu_request: int = 128,
                             cpu_limit: int = 256,
                             memory_request: int = 256,
                             memory_limit: int = 512) -> bool:
        try:
            stateful_set = self.apps_v1_api.read_namespaced_stateful_set(
                self.service_name, self.namespace)

            if replicas is not None:
                # Horizontal scaling
                stateful_set.spec.replicas = replicas

            if cpu_request is not None and cpu_limit is not None:
                # Vertical scaling
                for container in stateful_set.spec.template.spec.containers:
                    if not container.name.startswith(self.service_name):
                        continue

                    container.resources = {
                        'requests': {
                            'cpu': f"{cpu_request}m",
                            'memory': f"{memory_request}Mi"
                        },
                        'limits': {
                            'cpu': f"{cpu_limit}m",
                            'memory': f"{memory_limit}Mi"
                        }
                    }

            self.apps_v1_api.patch_namespaced_stateful_set(
                name=self.service_name,
                namespace=self.namespace,
                body=stateful_set)

            return True
        except client.rest.ApiException as e:
            logger.error(f"Error scaling stateful set: {e}")
            return False

    @timeout(values.KUBERNETES_CONNECTOR_TIMEOUT_THRESHOLD)
    def wait_for_active_service(self) -> None:
        while True:
            try:
                stateful_set = self.apps_v1_api.read_namespaced_stateful_set(
                    name=self.service_name, namespace=self.namespace)

                if stateful_set.status.available_replicas == stateful_set.spec.replicas:
                    logger.info(f"Scale finished")
                    return
            except client.rest.ApiException as e:
                logger.error(
                    f"An error occurred while reading stateful set: {e}")

            time.sleep(3)

    def redeploy_deployment(self) -> None:
        try:
            stateful_set = self.apps_v1_api.read_namespaced_stateful_set(
                name=self.service_name, namespace=self.namespace)

            stateful_set.spec.template.metadata.annotations = {
                "timestamp": str(datetime.datetime.now())
            }

            self.apps_v1_api.patch_namespaced_stateful_set(
                name=self.service_name,
                namespace=self.namespace,
                body=stateful_set)

        except client.rest.ApiException as e:
            logger.error(f"An error occurred while reading stateful set: {e}")

    def force_delete_pods(self) -> None:
        try:
            stateful_set = self.apps_v1_api.read_namespaced_stateful_set(
                name=self.service_name, namespace=self.namespace)

            pods = " ".join(f"{values.SERVICE_NAME}-{i}"
                            for i in range(stateful_set.spec.replicas))

            os.system(
                f"kubectl delete pod --grace-period=0 --force -n {self.namespace} {pods}"
            )
        except client.rest.ApiException as e:
            logger.error(f"An error occurred while reading stateful set: {e}")
