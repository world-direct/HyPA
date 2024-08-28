import sys

from stable_baselines3 import PPO

import values
from autoscale_environment.environment import AutoscaleEnv
from logger import get_module_logger

logger = get_module_logger(__name__)


def start(model_path: str):
    hypa: values.EvaluationDeployment = values.EVALUTAION_DEPLOYMENTS[
        values.Competitors.HYPA.name]

    logger.info(
        f"Start evaluation with parameters:\tmodel: {model_path}\tnamespace: {hypa.namespace}"
    )

    env: AutoscaleEnv = AutoscaleEnv(namespace=hypa.namespace,
                                     cdr_db_user=hypa.cdr_db_user,
                                     cdr_db_password=hypa.cdr_db_password)
    model: PPO = PPO.load(model_path, env=env)

    obs = env.reset()[0]

    while True:
        action = model.predict(observation=obs)
        obs, _, _, _, _ = env.step(action[0])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.error(
            f'Invalid number of arguments => make train ARGS="<log_directory> <model_path> <namespace> <cdr_db_user> <cdr_db_password> <csv_file_name>"'
        )
        sys.exit(1)

    if not sys.argv[1]:
        logger.error(f"No log_directory value specified")
        sys.exit(1)

    if not sys.argv[2]:
        logger.error(f"No model path specified")
        sys.exit(1)

    start(model_path=sys.argv[2])
