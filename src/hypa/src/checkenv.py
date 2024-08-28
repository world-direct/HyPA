from stable_baselines3.common.env_checker import check_env

from logger import get_module_logger
from train_environment.environment import HyPAEnv

logger = get_module_logger(__name__, log_to_console=True)

env = HyPAEnv()
check_env(env)

episodes = 5

for episode in range(episodes):
    terminated = False
    obs = env.reset()

    while not terminated:
        random_action = env.action_space.sample()
        logger.info(f"Action: {random_action}")

        obs, reward, terminated, truncated, info = env.step(random_action)
        logger.info(f"Reward: {reward}")
