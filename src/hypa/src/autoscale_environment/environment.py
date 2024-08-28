import sys
import time

import gymnasium as gym
import numpy as np
from gymnasium import spaces

import values
from connectors.cdr_connector import CdrConnector
from connectors.kubernetes_connector import KubernetesConnector
from logger import get_module_logger

logger = get_module_logger(__name__)


class AutoscaleEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, namespace: str, cdr_db_user: str, cdr_db_password: str):
        super(AutoscaleEnv, self).__init__()

        self.namespace = namespace
        self.cdr_db_user = cdr_db_user
        self.cdr_db_password = cdr_db_password

        self.kubernetes_connector: KubernetesConnector = KubernetesConnector(
            namespace=namespace, service_name=values.SERVICE_NAME)

        self.cdr_connector: CdrConnector = self._init_cdr_connector()

        self.current_cpu_request: int = 64
        self.current_cpu_limit: int = 0
        self.current_replicas: int = 0

        self.previous_replica_action: int = 0
        self.vertical_change: int = 0
        
        self.action_space: spaces.MultiDiscrete = spaces.MultiDiscrete(
            nvec=[3, 3])

        self.observation_space: spaces.Dict = spaces.Dict({
            'cpuUtilization':
            spaces.Box(low=0.0, high=1.0, dtype=np.float32),
            'averageLatency':
            spaces.Box(low=0.0, high=120.0, dtype=np.float32),
            'callSuccessRate':
            spaces.Box(low=0.0, high=1.0, dtype=np.float32),
            'numberOfCalls':
            spaces.Discrete(n=1000),
            'replicas':
            spaces.Discrete(n=3)
        })

    def step(self, action):
        logger.info(f"Action: {action}")

        step_action: int = -1
        replica_action: int = 1

        match action[0]:
            case 0:
                step_action = -values.ACTION_CPU_STEP_SIZE
            case 1:
                step_action = 0
            case 2:
                step_action = values.ACTION_CPU_STEP_SIZE

        replica_action += action[1]

        logger.info(
            f"Choosen action:\tstep: {step_action}\treplicas: {replica_action}"
        )
        
        self.previous_replica_action = replica_action
        self.vertical_change += step_action
        
        scale_service: bool = False
        scaling_delay: float = 0.0
        
        # Converged at a new scaling configuration
        if step_action == 0 and replica_action == self.previous_replica_action:
            scale_service = True
        
        if scale_service and (self.vertical_change != 0 or replica_action != self.current_replicas):        
            logger.info(
                f"Previous scale:\tCPU limit: {self.current_cpu_limit}\treplicas: {self.current_replicas}"
            )

            self.current_cpu_limit += self.vertical_change

            # Cap CPU request between a minimum of CPU_LIMIT_MIN and a maximum of CPU_LIMIT_MAX
            if self.current_cpu_limit < values.CPU_LIMIT_MIN:
                logger.info(
                    f"Suggested scale is below minimum configuration => limit to {values.CPU_LIMIT_MIN}"
                )
                self.current_cpu_limit = values.CPU_LIMIT_MIN

            if self.current_cpu_limit > values.CPU_LIMIT_MAX:
                logger.info(
                    f"Suggested scale is exceeds maximum configuration => limit to {values.CPU_LIMIT_MAX}"
                )
                self.current_cpu_limit = values.CPU_LIMIT_MAX

            self.current_replicas = replica_action

            logger.info(
                f"Scale to:\tCPU limit: {self.current_cpu_limit}\treplicas: {self.current_replicas}"
            )

            scaling_delay = self._try_scale()

            logger.info(f"Scaling finished in {scaling_delay}s")
        else:
            logger.info("No configuration change detected => no scaling")

        # Evaluate the current scale
        total_calls: int = self._try_get_total_calls()
        logger.debug(f"Total calls: {total_calls}")

        failed_calls: int = self._try_get_failed_calls()
        logger.debug(f"Failed calls: {failed_calls}")

        latencies: list[float] = self._try_get_call_latencies()
        logger.debug(f"Latencies: {latencies}")

        call_success_rate: float = 1.0

        if total_calls > 0:
            call_success_rate = float(len(latencies)) / float(total_calls)

            if call_success_rate > 1.0:
                call_success_rate = 1.0

        logger.debug(f"Call success rate: {call_success_rate}")

        current_latency: float = round(np.mean(latencies),
                                       2) if latencies else -1.0
        logger.debug(f"Average latency [s]: {current_latency}")

        current_utilization: float = self._try_get_current_cpu_metric()
        logger.debug(f"Queried CPU utilization: {current_utilization}")

        logger.debug(
            f"Latency:{current_latency}, CPU utilization: {current_utilization}"
        )

        observation = {
            'cpuUtilization': np.array([current_utilization],
                                       dtype=np.float32),
            'averageLatency': np.array([current_latency], dtype=np.float32),
            'callSuccessRate': np.array([call_success_rate], dtype=np.float32),
            'numberOfCalls': len(latencies),
            'replicas': self.current_replicas - 1
        }

        reward = 0.0
        terminated = False
        truncated = False
        info = {}

        return observation, reward, terminated, truncated, info

    def reset(self, seed=None, _=None):
        super().reset(seed=seed)

        logger.debug("Reset environment")

        self.current_cpu_request = 64
        self.current_cpu_limit = values.CPU_LIMIT_MIN
        self.current_replicas = 1

        self.kubernetes_connector.try_scale_deployment(
            cpu_request=self.current_cpu_request,
            cpu_limit=self.current_cpu_limit,
            memory_request=256,
            memory_limit=512,
            replicas=self.current_replicas)

        time.sleep(3)
        self.kubernetes_connector.wait_for_active_service()

        total_calls: int = self._try_get_total_calls()
        logger.debug(f"Total calls: {total_calls}")

        failed_calls: int = self._try_get_failed_calls()
        logger.debug(f"Failed calls: {failed_calls}")

        latencies: list[float] = self._try_get_call_latencies()
        logger.debug(f"Latencies: {latencies}")

        call_success_rate: float = 1.0

        if total_calls > 0:
            call_success_rate = float(len(latencies)) / float(total_calls)

            if call_success_rate > 1.0:
                call_success_rate = 1.0

        logger.debug(f"Call success rate: {call_success_rate}")

        current_latency: float = round(np.mean(latencies),
                                       2) if latencies else -1.0
        logger.debug(f"Average latency [s]: {current_latency}")

        current_utilization: float = self._try_get_current_cpu_metric()
        logger.debug(f"Queried CPU utilization: {current_utilization}")

        observation = {
            'cpuUtilization': np.array([current_utilization],
                                       dtype=np.float32),
            'averageLatency': np.array([current_latency], dtype=np.float32),
            'callSuccessRate': np.array([call_success_rate], dtype=np.float32),
            'numberOfCalls': len(latencies),
            'replicas': self.current_replicas - 1
        }

        info = {}

        return observation, info

    def _init_cdr_connector(self) -> CdrConnector:
        while True:
            try:
                return CdrConnector(namespace=self.namespace,
                                    username=self.cdr_db_user,
                                    password=self.cdr_db_password,
                                    host=values.CDR_HOST,
                                    port=values.CDR_PORT)
            except Exception as e:
                logger.error(
                    f"Error during CDR connector initialization => Wait {values.CONNECTION_RETRY_TIMER}s and try again\n{e}"
                )
                time.sleep(values.CONNECTION_RETRY_TIMER)

    def _try_get_total_calls(self) -> int:
        logger.debug(f"Check for failed calls of namespace: {self.namespace}")

        while True:
            try:
                total_calls: int = self.cdr_connector.get_total_calls(
                    interval=values.LATENCY_INTERVAL, unit="SECOND")

                logger.debug(f"Query returned: {total_calls}")

                return total_calls
            except TimeoutError:
                logger.error(f"Timeout during latency query")
                self.cdr_connector: CdrConnector = self._init_cdr_connector()
            except:
                logger.error(f"Unexpected error: {sys.exc_info()[0]}")
                self.cdr_connector: CdrConnector = self._init_cdr_connector()

    def _try_get_failed_calls(self) -> int:
        logger.debug(f"Check for failed calls of namespace: {self.namespace}")

        while True:
            try:
                failed_calls: int = self.cdr_connector.get_failed_calls_of_interval(
                    interval=values.LATENCY_INTERVAL, unit="SECOND")

                logger.debug(f"Query returned: {failed_calls}")

                if failed_calls == -1:
                    continue

                return failed_calls
            except TimeoutError:
                logger.error(f"Timeout during latency query")
                self.cdr_connector: CdrConnector = self._init_cdr_connector()
            except:
                logger.error(f"Unexpected error: {sys.exc_info()[0]}")
                self.cdr_connector: CdrConnector = self._init_cdr_connector()

    def _try_get_call_latencies(self) -> list[float]:
        logger.debug(f"Get latencies of namespace: {self.namespace}")

        while True:
            try:
                result = self.cdr_connector.get_latest_latencies_of_interval(
                    interval=values.LATENCY_INTERVAL, unit="SECOND")

                return result
            except TimeoutError:
                logger.error(f"Timeout during latency query")
                self.cdr_connector: CdrConnector = self._init_cdr_connector()
            except:
                logger.error(f"Unexpected error: {sys.exc_info()[0]}")
                self.cdr_connector: CdrConnector = self._init_cdr_connector()

    def _try_get_current_cpu_metric(self) -> float | None:
        while True:
            try:
                cpu_usage = self.kubernetes_connector.get_current_cpu_and_memory_utilization(
                )[0]

                if not cpu_usage:
                    continue

                return round(
                    cpu_usage /
                    (self.current_cpu_limit * self.current_replicas), 2)
            except TimeoutError:
                logger.error(f"Timeout during CPU utilization query")
            except:
                logger.error(f"Unexpected error: {sys.exc_info()[0]}")

            logger.warning(f"Wait {values.CONNECTION_RETRY_TIMER}s")

            time.sleep(values.CONNECTION_RETRY_TIMER)

    def _try_scale(self) -> float:
        scale_start: float = time.time()

        while True:
            try:
                self.kubernetes_connector.try_scale_deployment(
                    replicas=int(self.current_replicas),
                    cpu_request=int(self.current_cpu_request),
                    cpu_limit=int(self.current_cpu_limit),
                    memory_request=256,
                    memory_limit=512)

                break
            except Exception as e:
                logger.error(f"Error patching set: {e}")
                time.sleep(5)

        time.sleep(5)

        while True:
            try:
                self.kubernetes_connector.wait_for_active_service()
                time.sleep(2)
                self.kubernetes_connector.wait_for_active_service()
                break
            except TimeoutError:
                logger.error(
                    f"Scaling to the new deployment exceeded {values.KUBERNETES_CONNECTOR_TIMEOUT_THRESHOLD}s => Redeploy it"
                )

                scale_start = time.time()
                self.kubernetes_connector.force_delete_pods()
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error waiting for set to be active: {e}")
                time.sleep(5)

        return round(time.time() - scale_start, 2)
