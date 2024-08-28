import values
from connectors.cdr_connector import CdrConnector
from connectors.kubernetes_connector import KubernetesConnector

print("\nCheck MySQL CDR connection")

for deployment in values.DEPLOYMENTS.values():
    try:
        cdr: CdrConnector = CdrConnector(namespace=deployment.namespace,
                                         username=deployment.cdr_db_user,
                                         password=deployment.cdr_db_password,
                                         host=values.CDR_HOST,
                                         port=values.CDR_PORT)

        _ = cdr.get_latest_latencies_of_interval(10)

        print(f"{deployment.namespace}: OK")
    except Exception as e:
        print(f"{deployment.namespace}: Failed: {e}")

print("\nCheck Kubernetes connector")

for deployment in values.DEPLOYMENTS.values():
    try:
        kc: KubernetesConnector = KubernetesConnector(
            namespace=values.DEPLOYMENTS[deployment.scale.name].namespace,
            service_name=values.SERVICE_NAME)
        _ = kc.get_current_resource_configuration()

        print(f"{deployment.namespace}: OK")
    except Exception as e:
        print(f"Failed: {e}")
