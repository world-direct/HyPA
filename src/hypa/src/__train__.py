import os
import sys
import time

from gymnasium import wrappers
from stable_baselines3 import PPO

from logger import get_module_logger
from train_environment.environment import HyPAEnv

logger = get_module_logger(__name__)


def start(log_dir: str, total_timesteps: int, max_episode_steps: int,
          total_runs: int):
    logger.info(
        f"Start run with parameters:\tlog_directory: {log_dir}\ttotal_timesteps: {total_timesteps}\tmax_episode_steps: {max_episode_steps}\ttotal_runs: {total_runs}"
    )

    models_directory = f"models/PPO-{int(time.time())}"
    log_directory = f"{log_dir}/agent/PPO-{int(time.time())}"

    if not os.path.exists(models_directory):
        os.makedirs(models_directory)

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    env = HyPAEnv()
    env = wrappers.TimeLimit(env=env, max_episode_steps=max_episode_steps)

    env.reset()

    model = PPO("MultiInputPolicy",
                env,
                verbose=1,
                tensorboard_log=log_directory)

    for i in range(total_runs):
        logger.info(f"{i}. Run:\n")

        model.learn(total_timesteps=total_timesteps,
                    reset_num_timesteps=False,
                    tb_log_name="PPO")
        model.save(f"{models_directory}/{total_timesteps * i}")

    env.close()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        logger.error(
            f'Invalid number of arguments => make train ARGS="<log_directory> <total_timesteps> <max_episode_steps> <total_runs>"'
        )
        sys.exit(1)

    if not sys.argv[1]:
        logger.error(f"No log_directory value specified")
        sys.exit(1)

    if not sys.argv[2]:
        logger.error(f"No total_timesteps value specified")
        sys.exit(1)

    if not sys.argv[3]:
        logger.error(f"No max_episode_steps value specified")
        sys.exit(1)

    if not sys.argv[4]:
        logger.error(f"No total_runs value specified")
        sys.exit(1)

    start(log_dir=sys.argv[1],
          total_timesteps=int(sys.argv[2]),
          max_episode_steps=int(sys.argv[3]),
          total_runs=int(sys.argv[4]))
