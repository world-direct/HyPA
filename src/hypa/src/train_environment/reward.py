import values

GOOD_REWARD = 1
BAD_REWARD = -1


def _get_utilization_reward(current_utilization: float,
                            active_deployment: values.Deployment,
                            currently_no_calls: bool):
    if current_utilization <= values.UTILIZATION_LOWER:
        if currently_no_calls:
            # If there are no calls and we are at the smallest deployment it is good
            if active_deployment.scale == values.Scale.TC_256_1:
                return GOOD_REWARD

            # The closer we are to the biggest deployment, the closer we are to 1.0
            # The further away we are to the biggest deployment, the closer we are to 0.0
            return -(
                active_deployment.cpu_limit * active_deployment.replicas) / (
                    values.DEPLOYMENTS[values.Scale.TC_2048_3.name].cpu_limit *
                    values.DEPLOYMENTS[values.Scale.TC_2048_3.name].replicas)

    if current_utilization > values.UTILIZATION_LOWER and current_utilization <= values.UTILIZATION_UPPER:
        return GOOD_REWARD

    return BAD_REWARD


def calculate_reward(current_latency: float, current_utilization: float,
                     call_success_rate: float, total_calls: int,
                     active_deployment: values.Deployment) -> float:
    latency_reward: float = 0.0
    call_success_rate_reward: float = 0.0
    utilization_reward: float = 0.0

    # If we have calls, check the latency
    if current_latency > 0.0:
        latency_reward += GOOD_REWARD if current_latency <= values.LATENCY_THRESHOLD else BAD_REWARD
    
    call_success_rate_reward += BAD_REWARD if call_success_rate < values.CALL_SUCCESS_RATE_THRESHOLD else GOOD_REWARD

    currently_no_calls: bool = True if total_calls <= 0 and current_latency < 0.0 else False

    utilization_reward += _get_utilization_reward(
        current_utilization=current_utilization,
        active_deployment=active_deployment,
        currently_no_calls=currently_no_calls)

    return round((values.WEIGHT_LATENCY * latency_reward) +
                 (values.WEIGHT_UTILIZATION * utilization_reward) +
                 (values.WEIGHT_CALL_SUCCESS_RATE * call_success_rate_reward),
                 2)
