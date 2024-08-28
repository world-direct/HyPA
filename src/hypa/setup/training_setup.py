import values
from connectors.kubernetes_connector import KubernetesConnector

for deployment in values.DEPLOYMENTS.values():
    try:
        print(f"Setup {deployment.namespace}")

        kc = KubernetesConnector(namespace=deployment.namespace,
                                 service_name=values.SERVICE_NAME)

        kc.try_scale_deployment(replicas=deployment.replicas,
                                cpu_request=deployment.cpu_request,
                                cpu_limit=deployment.cpu_limit,
                                memory_request=deployment.memory_request,
                                memory_limit=deployment.memory_limit)
    except:
        print(f"{deployment.namespace}: Failed")

print("Finished setup!")
