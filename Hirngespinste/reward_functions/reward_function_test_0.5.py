import math

previous_progress = 0.0

def reward_function(params):
    global previous_progress

    progress = params["progress"]       
    is_offtrack = params["is_offtrack"]  

    if is_offtrack:
        previous_progress = 0.0
        return 1e-3

    diff = progress - previous_progress

    if diff <= 0:
        reward = 1e-3
    else:
        reward = diff ** 1.5

    previous_progress = progress

    return float(reward)
