"""This file serves as a collection of all configurable variables"""

from dataclasses import dataclass
from enum import Enum

# Logger settings
LOG_MAX_FILE_MBYTES: int = 5
LOG_MAX_BACKUPS: int = 50

# Agent settings
ACTION_CPU_STEP_SIZE: int = 256

# Model settings
CPU_LIMIT_MIN: int = 512
CPU_LIMIT_MAX: int = 2048

# CDR connector settings
CDR_HOST: str = "cdrdb.ccint.loc"
CDR_PORT: str = "3306"

# DB connector settings
CFG_USERNAME: str = "root"
CFG_PASSWORD: str = "ewQjE5MJYAMjeY"
CFG_HOST: str = "cfgdb.ccint.loc"
CFG_PORT: str = "3306"
CFG_DB: str = "hypa"

# Prometheus connector settings
URL: str = "http://prometheus.ccint.loc/"

# Timeout and retry settings
CDR_CONNECTOR_TIMEOUT_THRESHOLD: int = 10
PROMETHEUS_CONNECTOR_TIMEOUT_THRESHOLD: int = 10
KUBERNETES_CONNECTOR_TIMEOUT_THRESHOLD: int = 60
CONNECTION_RETRY_TIMER: int = 5

# Kubernetes connector settings
SERVICE_NAME: str = "asterisk"

# RL training settings
LATENCY_INTERVAL: int = 60
LATENCY_NO_CALLS: float = 30.0
FAILED_CALLS_THRESHOLD: float = 0.10

# Reward thresholds
LATENCY_THRESHOLD: float = 2.0
CALL_SUCCESS_RATE_THRESHOLD: float = 0.9
UTILIZATION_LOWER: float = 0.1
UTILIZATION_UPPER: float = 0.9

WEIGHT_LATENCY: float = 0.5
WEIGHT_CALL_SUCCESS_RATE: float = 0.3
WEIGHT_UTILIZATION: float = 0.2


# <Test Client>_<CPU limit>_<replicas>
class Scale(Enum):
    TC_256_1 = 0
    TC_256_2 = 1
    TC_256_3 = 2
    TC_512_1 = 3
    TC_512_2 = 4
    TC_512_3 = 5
    TC_768_1 = 6
    TC_768_2 = 7
    TC_768_3 = 8
    TC_1024_1 = 9
    TC_1024_2 = 10
    TC_1024_3 = 11
    TC_1280_1 = 12
    TC_1280_2 = 13
    TC_1280_3 = 14
    TC_1536_1 = 15
    TC_1536_2 = 16
    TC_1536_3 = 17
    TC_1792_1 = 18
    TC_1792_2 = 19
    TC_1792_3 = 20
    TC_2048_1 = 21
    TC_2048_2 = 22
    TC_2048_3 = 23


@dataclass
class Deployment:
    namespace: str
    scale: Scale
    cpu_request: int
    cpu_limit: int
    memory_request: int
    memory_limit: int
    replicas: int
    cdr_db_user: str
    cdr_db_password: str


DEPLOYMENTS: dict[str, Deployment] = {
    Scale.TC_256_1.name:
    Deployment("tc01-5959d217", Scale.TC_256_1, 64, 256, 256, 512, 1,
               "tc01-5959d217-cdrdb", "179a15560c4c4d66b085c1359efbc913"),
    Scale.TC_256_2.name:
    Deployment("tc02-1e6c9387", Scale.TC_256_2, 64, 256, 256, 512, 2,
               "tc02-1e6c9387-cdrdb", "db906c5c93b546c4b2eab4e2c20e50bd"),
    Scale.TC_256_3.name:
    Deployment("tc03-86837bc3", Scale.TC_256_3, 64, 256, 256, 512, 3,
               "tc03-86837bc3-cdrdb", "b66b8abbf68e47628f41a86ac5e74f21"),
    Scale.TC_512_1.name:
    Deployment("tc04-ace2c6af", Scale.TC_512_1, 64, 512, 256, 512, 1,
               "tc04-ace2c6af-cdrdb", "011a270cd753424584c29cfb0e9f145f"),
    Scale.TC_512_2.name:
    Deployment("tc05-79568703", Scale.TC_512_2, 64, 512, 256, 512, 2,
               "tc05-79568703-cdrdb", "6ec14ccc9549402d9dbf9c71832aea04"),
    Scale.TC_512_3.name:
    Deployment("tc06-1f101c13", Scale.TC_512_3, 64, 512, 256, 512, 3,
               "tc06-1f101c13-cdrdb", "87ab402bd8ec45f09e62810ce90e1aab"),
    Scale.TC_768_1.name:
    Deployment("tc07-d06fe44c", Scale.TC_768_1, 64, 768, 256, 512, 1,
               "tc07-d06fe44c-cdrdb", "6da601afa37640f3ae6e1ee551529128"),
    Scale.TC_768_2.name:
    Deployment("tc08-94a5e86e", Scale.TC_768_2, 64, 768, 256, 512, 2,
               "tc08-94a5e86e-cdrdb", "538fd6e5255a468b833a59bcefca2e8d"),
    Scale.TC_768_3.name:
    Deployment("tc09-35a03f20", Scale.TC_768_3, 64, 768, 256, 512, 3,
               "tc09-35a03f20-cdrdb", "c6986cd96a504202a8503506b836eeb7"),
    Scale.TC_1024_1.name:
    Deployment("tc10-253c743d", Scale.TC_1024_1, 64, 1024, 256, 512, 1,
               "tc10-253c743d-cdrdb", "ffa6fb9d11e94b8c971100c4862d6d05"),
    Scale.TC_1024_2.name:
    Deployment("tc11-4a4776f3", Scale.TC_1024_2, 64, 1024, 256, 512, 2,
               "tc11-4a4776f3-cdrdb", "d166988e888e4e088be6b87e3a2a5bf4"),
    Scale.TC_1024_3.name:
    Deployment("tc12-7738e12d", Scale.TC_1024_3, 64, 1024, 256, 512, 3,
               "tc12-7738e12d-cdrdb", "fe0dd9eb4883435a81f4f35359517737"),
    Scale.TC_1280_1.name:
    Deployment("tc13-9ec6ce86", Scale.TC_1280_1, 64, 1280, 256, 512, 1,
               "tc13-9ec6ce86-cdrdb", "2ba1657db99b40d1bc896e0d2f68edc8"),
    Scale.TC_1280_2.name:
    Deployment("tc14-22548719", Scale.TC_1280_2, 64, 1280, 256, 512, 2,
               "tc14-22548719-cdrdb", "f0d07b6f97fa40ada23f01314444e5f4"),
    Scale.TC_1280_3.name:
    Deployment("tc15-61c3ade5", Scale.TC_1280_3, 64, 1280, 256, 512, 3,
               "tc15-61c3ade5-cdrdb", "af263725735d414f92b8f32438c3188b"),
    Scale.TC_1536_1.name:
    Deployment("tc16-d5a9d99f", Scale.TC_1536_1, 64, 1536, 256, 512, 1,
               "tc16-d5a9d99f-cdrdb", "6dd01c9ca954468eafa69ef6164434a7"),
    Scale.TC_1536_2.name:
    Deployment("tc17-30d4741a", Scale.TC_1536_2, 64, 1536, 256, 512, 2,
               "tc17-30d4741a-cdrdb", "3ddcd2b049f0451d82fc7f42b1fa938d"),
    Scale.TC_1536_3.name:
    Deployment("tc18-babab238", Scale.TC_1536_3, 64, 1536, 256, 512, 3,
               "tc18-babab238-cdrdb", "f75ee7b06de3477b9f77095ee7a084bb"),
    Scale.TC_1792_1.name:
    Deployment("tc19-36f90673", Scale.TC_1792_1, 64, 1792, 256, 512, 1,
               "tc19-36f90673-cdrdb", "d672df5a1b8b48d7ab7f0656113aa83d"),
    Scale.TC_1792_2.name:
    Deployment("tc20-b8127a65", Scale.TC_1792_2, 64, 1792, 256, 512, 2,
               "tc20-b8127a65-cdrdb", "2d24ffdfb02740e0943bea7774d12d50"),
    Scale.TC_1792_3.name:
    Deployment("tc21-deb5adf0", Scale.TC_1792_3, 64, 1792, 256, 512, 3,
               "tc21-deb5adf0-cdrdb", "f910e8427e0b4d46aace043bf6ce388b"),
    Scale.TC_2048_1.name:
    Deployment("tc22-0482a6cf", Scale.TC_2048_1, 64, 2048, 256, 512, 1,
               "tc22-0482a6cf-cdrdb", "69197c860d084170a1ea76fa65c993d9"),
    Scale.TC_2048_2.name:
    Deployment("tc23-80b322e6", Scale.TC_2048_2, 64, 2048, 256, 512, 2,
               "tc23-80b322e6-cdrdb", "0961053fce914ea996f393bd482c37ac"),
    Scale.TC_2048_3.name:
    Deployment("tc24-d63b1596", Scale.TC_2048_3, 64, 2048, 256, 512, 3,
               "tc24-d63b1596-cdrdb", "2b1fbb4d25df4c79be1ee68cf045c576")
}

# Evaluation
class Competitors(Enum):
    HPA = 0
    MOHA = 1
    HYPA = 2


@dataclass
class EvaluationDeployment:
    namespace: str
    cdr_db_user: str
    cdr_db_password: str


EVALUTAION_DEPLOYMENTS: dict[str, EvaluationDeployment] = {
    Competitors.HPA.name:
    EvaluationDeployment(namespace="lithuania-b643844a",
                         cdr_db_user="lithuania-b643844a-cdrdb",
                         cdr_db_password="47c942a6a20c48deb92b6491751130e3"),
    Competitors.MOHA.name:
    EvaluationDeployment(namespace="luxembourg-85ecb8e5",
                         cdr_db_user="luxembourg-85ecb8e5-cdrdb",
                         cdr_db_password="50fd46624f954c59bdf7b9ba3266995d"),
    Competitors.HYPA.name:
    EvaluationDeployment(namespace="slovakia-f02486c2",
                         cdr_db_user="slovakia-f02486c2-cdrdb",
                         cdr_db_password="18fee37d6f9744b2a6c998fec3ea67ef")
}
