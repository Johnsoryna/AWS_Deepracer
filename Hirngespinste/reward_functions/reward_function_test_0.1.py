import math


class Reward:
    def __init__(self, verbose=False):
        self.first_racingpoint_index = None
        self.verbose = verbose

    def reward_function(self, params):

        def dist_2_points(x1, x2, y1, y2):
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        def closest_2_racing_points_index(racing_coords, car_coords):
            distances = [dist_2_points(x, car_coords[0], y, car_coords[1]) for x, y in racing_coords]
            closest_index = distances.index(min(distances))
            distances_no_closest = distances.copy()
            distances_no_closest[closest_index] = float('inf')
            second_closest_index = distances_no_closest.index(min(distances_no_closest))
            return [closest_index, second_closest_index]

        def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):
            a = dist_2_points(*closest_coords, *second_closest_coords)
            b = dist_2_points(car_coords[0], closest_coords[0], car_coords[1], closest_coords[1])
            c = dist_2_points(car_coords[0], second_closest_coords[0], car_coords[1], second_closest_coords[1])
            if a == 0:
                return b
            return abs(-(a**4) + 2*(a**2)*(b**2) + 2*(a**2)*(c**2) - (b**4) + 2*(b**2)*(c**2) - (c**4))**0.5 / (2*a)

        racing_track = [
            [2.88738855, 0.72646774], [3.16759122, 0.70478649], [3.45517317, 0.69217863],
            [3.75325158, 0.68581005], [4.07281434, 0.68360819], [4.50000223, 0.68376092],
            [4.54999507, 0.68377879], [5.11738115, 0.69080411], [5.44798256, 0.7112322 ],
            [5.71126558, 0.7422347 ], [5.94137211, 0.78496462], [6.1491271 , 0.84078035],
            [6.33675893, 0.91066736], [6.50351669, 0.99483994], [6.64762588, 1.09336367]
        ]

        all_wheels_on_track = params['all_wheels_on_track']
        x, y = params['x'], params['y']
        track_width = params['track_width']
        steps = params['steps']
        progress = params['progress']
        is_offtrack = params['is_offtrack']
        speed = params['speed']
        heading = params['heading']

        closest_index, second_closest_index = closest_2_racing_points_index(racing_track, [x, y])
        optimals, optimals_second = racing_track[closest_index], racing_track[second_closest_index]

        if steps == 1:
            self.first_racingpoint_index = closest_index

        reward = 1
        dist = dist_to_racing_line(optimals, optimals_second, [x, y])
        distance_reward = max(1e-3, 1 - (dist / (track_width * 0.5)))
        reward += distance_reward

        MIN_SPEED = 2.0
        MAX_SPEED = 4.0
        optimal_speed = MAX_SPEED
        sigma_speed = abs(MAX_SPEED - MIN_SPEED) / 6.0
        speed_reward = math.exp(-0.5 * abs(speed - optimal_speed) ** 2 / sigma_speed ** 2)
        reward += speed_reward * 10

        route_direction = math.atan2(optimals_second[1] - y, optimals_second[0] - x)
        route_direction = math.degrees(route_direction)
        direction_diff = abs(route_direction - heading)
        heading_reward = math.cos(direction_diff * (math.pi / 180)) ** 10
        if direction_diff <= 20:
            heading_reward = math.cos(direction_diff * (math.pi / 180)) ** 4
        reward += heading_reward * 5

        progress_reward = 10 * progress / steps
        if steps <= 5:
            progress_reward = 1 
        reward += progress_reward

        if not all_wheels_on_track or is_offtrack:
            reward = 1e-3

        return float(reward)


reward_object = Reward()

def reward_function(params):
    return reward_object.reward_function(params)
