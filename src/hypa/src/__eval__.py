import sys

from evaluation.evaluation import Eval
from logger import get_module_logger

logger = get_module_logger(__name__)


def start(log_directory: str, pull_interval: int, log_interval: float):
    logger.info(
        f"Start evaluation for all evaluation namespaces, polling values every {pull_interval} seconds and logging every {log_interval} seconds"
    )

    env: Eval = Eval(log_directory=log_directory,
                     poll_interval=pull_interval,
                     log_interval=log_interval)

    while True:
        env.start_evaluation()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        logger.error(
            f'Invalid number of arguments => ARGS="<log_directory> <pull_interval_sec> <log_interval_sec>'
        )
        sys.exit(1)

    if not sys.argv[1]:
        logger.error(f"No log_directory value specified")
        sys.exit(1)

    if not sys.argv[2]:
        logger.error(f"No pull interval name specified")
        sys.exit(1)

    if not sys.argv[3]:
        logger.error(f"No log interval name specified")
        sys.exit(1)

    start(log_directory=sys.argv[1],
          pull_interval=int(sys.argv[2]),
          log_interval=float(sys.argv[3]))
