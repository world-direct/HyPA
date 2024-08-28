import values
from connectors.kubernetes_connector import KubernetesConnector

deployments: list[values.Deployment] = [
    values.Deployment(
        values.EVALUTAION_DEPLOYMENTS[values.Competitors.HPA.name].namespace,
        values.Scale.TC_256_1, 64, 512, 256, 512, 1,
        values.EVALUTAION_DEPLOYMENTS[values.Competitors.HPA.name].cdr_db_user,
        values.EVALUTAION_DEPLOYMENTS[
            values.Competitors.HPA.name].cdr_db_password),
    values.Deployment(
        values.EVALUTAION_DEPLOYMENTS[values.Competitors.MOHA.name].namespace,
        values.Scale.TC_256_1, 64, 512, 256, 512, 1,
        values.EVALUTAION_DEPLOYMENTS[
            values.Competitors.MOHA.name].cdr_db_user,
        values.EVALUTAION_DEPLOYMENTS[
            values.Competitors.MOHA.name].cdr_db_password),
    values.Deployment(
        values.EVALUTAION_DEPLOYMENTS[values.Competitors.HYPA.name].namespace,
        values.Scale.TC_256_1, 64, 512, 256, 512, 1,
        values.EVALUTAION_DEPLOYMENTS[
            values.Competitors.HYPA.name].cdr_db_user,
        values.EVALUTAION_DEPLOYMENTS[
            values.Competitors.HYPA.name].cdr_db_password)
]

for deployment in deployments:
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
