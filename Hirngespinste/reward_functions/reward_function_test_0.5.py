import math

def reward_function(params):
    """
    Reward-Funktion mit:
      - Vollständiger racing_track-Datenliste (x, y, speed, acc, heading)
      - Heading-Strafe nur, wenn man sich weiter von der Ideallinie entfernt
      - Speed-Betrachtung inkl. Vorausschau auf nächste Wegpunkte
      - Additiver Belohnungsansatz (statt rein multiplikativ)

    Parameter 'params' enthält u.a.:
      - track_width, x, y, speed, heading, all_wheels_on_track, is_offtrack
    """

    # ========== Hilfsfunktionen ==========

    def dist_2_points(x1, y1, x2, y2):
        """Euklidischer Abstand zwischen zwei Punkten."""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def closest_2_racing_points_index(racing_coords, car_coords):
        """
        Findet die Indizes des nächstgelegenen und zweitnächsten
        Wegpunkts in racing_coords zur aktuellen Auto-Position car_coords.
        """
        distances = [
            dist_2_points(x, y, car_coords[0], car_coords[1])
            for (x, y, _, _, _) in racing_coords
        ]
        closest_idx = distances.index(min(distances))

        distances_no_closest = distances.copy()
        distances_no_closest[closest_idx] = float('inf')
        second_closest_idx = distances_no_closest.index(min(distances_no_closest))

        return closest_idx, second_closest_idx

    def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):
        """
        Senkrechter Abstand vom Auto zur Linie zwischen
        'closest_coords' und 'second_closest_coords'.
        """
        x1, y1 = closest_coords[0], closest_coords[1]
        x2, y2 = second_closest_coords[0], second_closest_coords[1]
        x, y   = car_coords[0], car_coords[1]

        numerator = abs((y2 - y1)*x - (x2 - x1)*y + (x2*y1 - x1*y2))
        denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)

        return numerator / denominator if denominator != 0 else 0.0

    def is_car_left_of_line(closest_coords, second_closest_coords, car_coords):
        """
        Kreuzprodukt, um festzustellen, ob das Auto links (>0) oder rechts (<0)
        vom Richtungsvektor (closest_coords -> second_closest_coords) ist.
        """
        x1, y1 = closest_coords[0], closest_coords[1]
        x2, y2 = second_closest_coords[0], second_closest_coords[1]
        x, y   = car_coords[0], car_coords[1]

        line_x = x2 - x1
        line_y = y2 - y1
        car_x  = x  - x1
        car_y  = y  - y1

        # Kreuzprodukt: (line_x, line_y) x (car_x, car_y)
        return line_x * car_y - line_y * car_x

    def get_future_optimal_speed(racing_coords, current_index, lookahead=2):
        """
        Betrachtet die nächsten 'lookahead' Wegpunkte und nimmt das Minimum
        deren optimaler Geschwindigkeiten. Dadurch kann das Auto z.B. früh
        für eine kommende Kurve bremsen.
        """
        end_index = min(current_index + lookahead, len(racing_coords) - 1)
        future_speeds = [racing_coords[i][2] for i in range(current_index, end_index + 1)]
        return min(future_speeds)  # alternativ: sum(...) / len(...)

    # ========== Einlesen der relevanten Parameter aus 'params' ==========
    track_width = params['track_width']
    x = params['x']
    y = params['y']
    speed = params['speed']
    heading = params['heading']
    all_wheels_on_track = params['all_wheels_on_track']
    is_offtrack = params['is_offtrack']

    racing_track = [
        [3.2137, 0.6936, 4.0, 0.7136, -1.6529],
        [3.3617, 0.6893, 4.0, 0.5646, -1.0523],
        [3.5103, 0.6866, 4.0, 0.4928, -0.5341],
        [3.6594, 0.6852, 4.0, 0.4503, -0.0729],
        [3.8087, 0.6850, 4.0, 0.4385, 0.3614],
        [3.9577, 0.6859, 4.0, 0.4463, 0.7981],
        [4.1063, 0.6880, 4.0, 0.4610, 1.2457],
        [4.2544, 0.6912, 4.0, 0.4903, 1.7084],
        [4.4019, 0.6956, 4.0, 0.5293, 2.2105],
        [4.5488, 0.7013, 4.0, 0.5757, 2.7457],
        [4.6950, 0.7083, 4.0, 0.6301, 3.3339],
        [4.8404, 0.7168, 4.0, 0.6830, 3.9693],
        [4.9849, 0.7268, 4.0, 0.7450, 4.6534],
        [5.1285, 0.7385, 4.0, 0.8254, 5.4005],
        [5.2711, 0.7520, 3.9116, 0.9492, 6.2295],
        [5.4126, 0.7674, 3.5969, 1.1225, 7.2010],
        [5.5526, 0.7851, 3.3352, 1.3056, 8.3425],
        [5.6912, 0.8054, 3.0484, 1.5626, 9.6376],
        [5.8278, 0.8286, 2.7247, 1.9557, 11.2304],
        [5.9622, 0.8553, 2.4361, 2.4459, 13.2107],
        [6.0938, 0.8862, 2.1776, 3.0601, 15.6389],
        [6.2219, 0.9221, 1.9313, 3.8881, 18.6403],
        [6.3457, 0.9638, 1.6957, 5.0385, 22.4147],
        [6.4639, 1.0126, 1.4930, 6.4882, 27.2447],
        [6.5748, 1.0697, 1.3080, 8.4280, 33.2524],
        [6.6765, 1.1364, 1.1372, 11.0909, 41.0034],
        [6.7659, 1.2141, 1.1140, 11.5445, 50.9679],
        [6.8384, 1.3035, 1.1909, 10.1340, 59.0519],
        [6.8965, 1.4004, 1.1590, 10.6872, 66.4409],
        [6.9411, 1.5027, 1.0459, 13.0478, 75.1603],
        [6.9695, 1.6097, 1.0313, 13.4049, 86.0383],
        [6.9771, 1.7195, 1.1068, 11.6907, 95.2559],
        [6.9670, 1.8287, 1.1626, 10.6231, 103.4294],
        [6.9415, 1.9356, 1.1653, 10.5750, 111.0438],
        [6.9018, 2.0389, 1.1073, 11.6821, 119.2453],
        [6.8470, 2.1367, 1.1284, 11.2598, 128.7873],
        [6.7753, 2.2259, 1.2573, 9.1109, 136.6961],
        [6.6901, 2.3062, 1.4094, 7.2727, 143.1588],
        [6.5941, 2.3782, 1.5897, 5.7285, 148.4075],
        [6.4894, 2.4426, 1.8235, 4.3598, 152.5881],
        [6.3776, 2.5005, 2.1307, 3.1960, 155.7366],
        [6.2606, 2.5533, 2.5516, 2.2298, 158.0616],
        [6.1396, 2.6020, 3.3178, 1.3192, 159.6137],
        [6.0158, 2.6480, 4.0, 0.3801, 160.3801],
        [5.8908, 2.6926, 4.0, 0.1552, 160.2924],
        [5.7607, 2.7392, 4.0, 0.2683, 160.0969],
        [5.6306, 2.7863, 4.0, 0.3868, 159.7974],
        [5.5006, 2.8341, 4.0, 0.5116, 159.3825],
        [5.3708, 2.8830, 4.0, 0.6502, 158.8514],
        [5.2413, 2.9330, 4.0, 0.8218, 158.1787],
        [5.1122, 2.9847, 3.7198, 1.0496, 157.3279],
        [4.9838, 3.0384, 3.2949, 1.3376, 156.2309],
        [4.8564, 3.0945, 2.9079, 1.7172, 154.8437],
        [4.7302, 3.1537, 2.9968, 1.6169, 153.0398],
        [4.6060, 3.2170, 3.5096, 1.1791, 151.8369],
        [4.4830, 3.2828, 3.8543, 0.9776, 150.8461],
        [4.3610, 3.3508, 4.0, 0.8192, 150.0170],
        [4.2401, 3.4206, 4.0, 0.6997, 149.3203],
        [4.1199, 3.4919, 4.0, 0.6073, 148.7135],
        [4.0005, 3.5645, 4.0, 0.5253, 148.1890],
        [3.8818, 3.6381, 4.0, 0.4584, 147.7357],
        [3.7640, 3.7125, 4.0, 0.0151, 147.3380],
        [3.6472, 3.7873, 4.0, 0.6237, 147.7078],
        [3.5310, 3.8607, 3.5649, 1.1428, 148.4829],
        [3.4142, 3.9324, 2.8778, 1.7532, 149.7958],
        [3.2962, 4.0010, 2.4476, 2.4230, 151.6732],
        [3.1768, 4.0654, 2.0979, 3.2965, 154.1818],
        [3.0554, 4.1242, 1.8038, 4.4551, 157.6038],
        [2.9317, 4.1752, 1.7760, 4.5947, 162.1417],
        [2.8055, 4.2158, 1.9170, 3.9462, 165.7527],
        [2.6778, 4.2482, 1.9819, 3.6925, 169.0849],
        [2.5493, 4.2730, 2.0319, 3.5136, 172.2101],
        [2.4202, 4.2907, 2.0506, 3.4500, 175.1982],
        [2.2909, 4.3015, 2.0352, 3.5023, 178.1865],
        [2.1618, 4.3056, 1.9980, 3.6335, -178.7583],
        [2.0330, 4.3028, 1.9290, 3.8973, -175.5674],
        [1.9052, 4.2929, 1.8406, 4.2791, -172.0858],
        [1.7788, 4.2754, 1.7087, 4.9623, -168.2746],
        [1.6546, 4.2496, 1.5551, 5.9845, -163.6752],
        [1.5338, 4.2142, 1.4040, 7.3281, -158.1969],
        [1.4180, 4.1679, 1.2442, 9.2999, -151.4322],
        [1.3097, 4.1089, 1.1253, 11.3207, -142.7919],
        [1.2129, 4.0354, 1.1008, 11.8163, -132.8088],
        [1.1309, 3.9469, 1.1745, 10.4124, -123.4376],
        [1.0643, 3.8461, 1.2983, 8.5525, -115.7725],
        [1.0112, 3.7360, 1.4235, 7.1303, -109.3557],
        [0.9700, 3.6187, 1.5535, 5.9962, -103.8655],
        [0.9396, 3.4954, 1.6956, 5.0387, -99.1560],
        [0.9189, 3.3673, 1.8414, 4.2755, -95.1205],
        [0.9071, 3.2353, 1.9956, 3.6422, -91.5858],
        [0.9033, 3.1002, 2.1445, 3.1550, -88.5521],
        [0.9068, 2.9629, 2.2586, 2.8450, -85.8067],
        [0.9170, 2.8242, 2.3530, 2.6216, -83.2761],
        [0.9334, 2.6848, 2.4386, 2.4409, -80.9023],
        [0.9557, 2.5456, 2.5031, 2.3169, -78.6869],
        [0.9834, 2.4071, 2.5413, 2.2478, -76.5390],
        [1.0163, 2.2699, 2.5571, 2.2202, -74.4589],
        [1.0539, 2.1344, 2.5397, 2.2506, -72.3777],
        [1.0962, 2.0012, 2.4549, 2.4087, -70.2634],
        [1.1431, 1.8706, 2.3294, 2.6749, -67.9194],
        [1.1948, 1.7431, 2.1920, 3.0202, -65.3554],
        [1.2516, 1.6194, 2.0206, 3.5530, -62.4347],
        [1.3138, 1.5002, 1.8398, 4.2831, -58.9777],
        [1.3822, 1.3864, 1.6628, 5.2384, -54.8430],
        [1.4576, 1.2794, 1.4866, 6.5437, -49.8089],
        [1.5410, 1.1807, 1.3099, 8.4037, -43.5101],
        [1.6339, 1.0925, 1.3287, 8.1708, -35.3261],
        [1.7384, 1.0184, 1.5240, 6.2286, -29.4017],
        [1.8510, 0.9550, 1.6718, 5.1825, -24.5320],
        [1.9700, 0.9007, 1.8104, 4.4226, -20.3243],
        [2.0946, 0.8545, 1.9597, 3.7766, -16.6777],
        [2.2239, 0.8158, 2.1222, 3.2215, -13.5146],
        [2.3573, 0.7837, 2.3030, 2.7365, -10.7778],
        [2.4942, 0.7577, 2.5150, 2.2950, -8.4264],
        [2.6341, 0.7370, 2.7651, 1.8990, -6.4497],
        [2.7764, 0.7209, 3.0682, 1.5425, -4.7994],
        [2.9207, 0.7087, 3.4781, 1.2005, -3.4712],
        [3.0666, 0.6999, 3.9590, 0.9266, -2.4605],
        [3.2137, 0.6936, 4.0, 0.7136, -1.6529],
        # Letzter Eintrag aus dem Original (dupliziert)
        [3.2137, 0.6936, 4.0, 0.7136, -1.6529]
    ]

    # ========== Indizes für näheste Wegpunkte berechnen ==========
    closest_idx, second_closest_idx = closest_2_racing_points_index(racing_track, [x, y])
    closest_coords = racing_track[closest_idx]
    second_closest_coords = racing_track[second_closest_idx]

    # ========== 1) Distance-Faktor ========== 
    dist_line = dist_to_racing_line(closest_coords, second_closest_coords, [x, y])
    # Exponentielle Abnahme mit wachsendem Abstand
    distance_factor = math.exp(-2.0 * (dist_line / (0.3 * track_width)))

    # ========== 2) Speed-Faktor (inkl. Vorausschau) ========== 
    future_opt_speed = get_future_optimal_speed(racing_track, closest_idx, lookahead=2)
    speed_ratio = speed / (future_opt_speed + 1e-9)
    speed_ratio = min(speed_ratio, 1.0)  # nicht über 1.0 klemmen
    speed_factor = speed_ratio**2        # Quadratische Skala

    # ========== 3) Heading-Faktor (Strafe nur wenn "falsche" Richtung) ==========
    optimal_heading = closest_coords[4]
    heading_diff = abs(optimal_heading - heading)
    # Normalisieren auf max 180 Grad
    if heading_diff > 180:
        heading_diff = 360 - heading_diff

    # Prüfen, ob Fahrzeug links (> 0) oder rechts (< 0) der Ideallinie steht
    position_sign = is_car_left_of_line(closest_coords, second_closest_coords, [x, y])

    # Basis-Strafterm je nach Abweichung
    heading_base = math.exp(-0.1 * (heading_diff**2))

    # Kleiner Zusatzabzug, falls es sich noch weiter "rausdreht"
    extra_penalty = 1.0
    if position_sign > 0 and heading > optimal_heading:
        # Links der Linie, aber heading "zu groß" => dreht weiter weg
        extra_penalty = 0.7
    elif position_sign < 0 and heading < optimal_heading:
        # Rechts der Linie, heading "zu klein" => dreht weiter weg
        extra_penalty = 0.7

    heading_factor = heading_base * extra_penalty

    # ========== Additiver Reward (statt Multiplikation) ========== 
    raw_reward = distance_factor + speed_factor + heading_factor
    reward = raw_reward / 3.0  # Normierung, max ~1.0 wenn alles perfekt

    # ========== Harte Strafe, wenn komplett Offtrack ========== 
    if not all_wheels_on_track or is_offtrack:
        reward = 1e-3

    return float(reward)
