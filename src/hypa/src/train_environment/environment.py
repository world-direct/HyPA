import sys
import time

import gymnasium as gym
import numpy as np
from gymnasium import spaces

import values
from connectors.cdr_connector import CdrConnector
from connectors.kubernetes_connector import KubernetesConnector
from logger import get_module_logger
from train_environment.reward import calculate_reward

logger = get_module_logger(__name__)


class HyPAEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self):
        super(HyPAEnv, self).__init__()

        self.active_deployment: values.Deployment = None
        self.previous_deployment: values.Deployment = None

        self.cdr_connectors: dict[str, CdrConnector] = {
            values.Scale.TC_256_1.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_256_1.name]),
            values.Scale.TC_256_2.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_256_2.name]),
            values.Scale.TC_256_3.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_256_3.name]),
            values.Scale.TC_512_1.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_512_1.name]),
            values.Scale.TC_512_2.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_512_2.name]),
            values.Scale.TC_512_3.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_512_3.name]),
            values.Scale.TC_768_1.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_768_1.name]),
            values.Scale.TC_768_2.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_768_2.name]),
            values.Scale.TC_768_3.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_768_3.name]),
            values.Scale.TC_1024_1.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1024_1.name]),
            values.Scale.TC_1024_2.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1024_2.name]),
            values.Scale.TC_1024_3.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1024_3.name]),
            values.Scale.TC_1280_1.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1280_1.name]),
            values.Scale.TC_1280_2.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1280_2.name]),
            values.Scale.TC_1280_3.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1280_3.name]),
            values.Scale.TC_1536_1.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1536_1.name]),
            values.Scale.TC_1536_2.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1536_2.name]),
            values.Scale.TC_1536_3.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1536_3.name]),
            values.Scale.TC_1792_1.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1792_1.name]),
            values.Scale.TC_1792_2.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1792_2.name]),
            values.Scale.TC_1792_3.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_1792_3.name]),
            values.Scale.TC_2048_1.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_2048_1.name]),
            values.Scale.TC_2048_2.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_2048_2.name]),
            values.Scale.TC_2048_3.name:
            self._init_cdr_connector(
                deployment=values.DEPLOYMENTS[values.Scale.TC_2048_3.name])
        }

        # position 0:
        #   0 => scale down
        #   1 => no action
        #   2 => scale up
        # position 1:
        #   0 => 1 replicas
        #   1 => 2 replicas
        #   2 => 3 replicas
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
        step_action: int = -1
        instance_action: int = 1

        match action[0]:
            case 0:
                step_action = -values.ACTION_CPU_STEP_SIZE
            case 1:
                step_action = 0
            case 2:
                step_action = values.ACTION_CPU_STEP_SIZE

        instance_action += action[1]

        logger.info(
            f"Choosen action:\tstep: {step_action}\treplicas: {instance_action}"
        )

        self.previous_deployment = self.active_deployment
        new_deployment_name: str = f"TC_{self.previous_deployment.cpu_limit + step_action}_{instance_action}"

        if new_deployment_name in values.DEPLOYMENTS.keys():
            self.active_deployment = values.DEPLOYMENTS[new_deployment_name]

        logger.info(
            f"Current deployment: {self.active_deployment.scale.name}\tPrevious deployment: {self.previous_deployment.scale.name}"
        )

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
            f"Reward parameters: Latency={current_latency}\tCPU utilization={current_utilization}\tCall success rate={call_success_rate}\tTotal calls={total_calls}"
        )

        reward = calculate_reward(current_latency=current_latency,
                                  call_success_rate=call_success_rate,
                                  total_calls=total_calls,
                                  current_utilization=current_utilization,
                                  active_deployment=self.active_deployment)
        logger.info(f"Reward: {reward}")

        observation = {
            'cpuUtilization': np.array([current_utilization],
                                       dtype=np.float32),
            'averageLatency': np.array([current_latency], dtype=np.float32),
            'callSuccessRate': np.array([call_success_rate], dtype=np.float32),
            'numberOfCalls': total_calls,
            'replicas': self.active_deployment.replicas - 1
        }

        terminated = False
        truncated = False
        info = {}

        return observation, reward, terminated, truncated, info

    def reset(self, seed=None, _=None):
        super().reset(seed=seed)

        logger.debug("Reset environment")

        random_scale_set: int = self.np_random.integers(low=0,
                                                        high=len(values.Scale),
                                                        size=2,
                                                        dtype=int)

        self.active_deployment: values.Deployment = values.DEPLOYMENTS[
            f"{values.Scale(random_scale_set[0]).name}"]
        self.previous_deployment: values.Deployment = values.DEPLOYMENTS[
            f"{values.Scale(random_scale_set[1]).name}"]

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
            'numberOfCalls': total_calls,
            'replicas': self.active_deployment.replicas - 1
        }

        info = {}

        return observation, info

    def _init_cdr_connector(self,
                            deployment: values.Deployment) -> CdrConnector:
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

    def _try_get_total_calls(self) -> int:
        logger.debug(
            f"Check for failed calls of namespace: {self.active_deployment.scale.name} | {self.active_deployment.namespace}"
        )

        while True:
            try:
                connector: CdrConnector = self.cdr_connectors[
                    values.Scale.TC_2048_3.name]

                total_calls: int = connector.get_total_calls(
                    interval=values.LATENCY_INTERVAL, unit="SECOND")

                logger.debug(f"Query returned: {total_calls}")

                return total_calls
            except TimeoutError:
                logger.error(f"Timeout during latency query")
                self.cdr_connectors[
                    values.Scale.TC_2048_3.name] = self._init_cdr_connector(
                        deployment=values.DEPLOYMENTS[
                            values.Scale.TC_2048_3.name])
            except:
                logger.error(f"Unexpected error: {sys.exc_info()[0]}")
                self.cdr_connectors[
                    values.Scale.TC_2048_3.name] = self._init_cdr_connector(
                        deployment=values.DEPLOYMENTS[
                            values.Scale.TC_2048_3.name])

    def _try_get_failed_calls(self) -> int:
        logger.debug(
            f"Check for failed calls of namespace: {self.active_deployment.namespace}"
        )

        while True:
            try:
                connector: CdrConnector = self.cdr_connectors[
                    self.active_deployment.scale.name]

                failed_calls: int = connector.get_failed_calls_of_interval(
                    interval=values.LATENCY_INTERVAL, unit="SECOND")

                logger.debug(f"Query returned: {failed_calls}")

                return failed_calls
            except TimeoutError:
                logger.error(f"Timeout during latency query")
                self.cdr_connectors[self.active_deployment.scale.
                                    name] = self._init_cdr_connector(
                                        deployment=self.active_deployment)
            except:
                logger.error(f"Unexpected error: {sys.exc_info()[0]}")
                self.cdr_connectors[self.active_deployment.scale.
                                    name] = self._init_cdr_connector(
                                        deployment=self.active_deployment)

    def _try_get_call_latencies(self) -> list[float]:
        logger.debug(
            f"Get latencies of namespace: {self.active_deployment.scale.name} | {self.active_deployment.namespace}"
        )

        while True:
            try:
                connector: CdrConnector = self.cdr_connectors[
                    self.active_deployment.scale.name]

                latencies: list[
                    float] = connector.get_latest_latencies_of_interval(
                        interval=values.LATENCY_INTERVAL, unit="SECOND")

                logger.debug(f"Query returned: {latencies}")

                return latencies
            except TimeoutError:
                logger.error(f"Timeout during latency query")
                self.cdr_connectors[self.active_deployment.scale.
                                    name] = self._init_cdr_connector(
                                        deployment=self.active_deployment)
            except:
                logger.error(f"Unexpected error: {sys.exc_info()[0]}")
                self.cdr_connectors[self.active_deployment.scale.
                                    name] = self._init_cdr_connector(
                                        deployment=self.active_deployment)

    def _try_get_current_cpu_metric(self) -> float:
        kubernetes_connector: KubernetesConnector = KubernetesConnector(
            namespace=self.active_deployment.namespace,
            service_name=values.SERVICE_NAME)

        while True:
            try:
                cpu_usage = kubernetes_connector.get_current_cpu_and_memory_utilization(
                )[0]

                if not cpu_usage:
                    continue

                return round(
                    cpu_usage / (self.active_deployment.cpu_limit *
                                 self.active_deployment.replicas), 2)
            except TimeoutError:
                logger.error(f"Timeout during CPU utilization query")
            except:
                logger.error(f"Unexpected error: {sys.exc_info()[0]}")

            logger.warning(f"Wait {values.CONNECTION_RETRY_TIMER}s")

            time.sleep(values.CONNECTION_RETRY_TIMER)
