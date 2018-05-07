import math

from future.utils import old_div


def calc_turn_value(us, them, current_yaw):
    """ Calc turn speed required to steer 'us' towards 'them'."""
    dx = them[0] - us[0]
    dz = them[1] - us[1]
    yaw = -180 * math.atan2(dx, dz) / math.pi
    difference = yaw - current_yaw
    while difference < -180:
        difference += 360
    while difference > 180:
        difference -= 360
    difference /= 180.0
    return difference


def get_path_value(agent, position):
    current_yaw = agent.get_observations_value('Yaw')
    current_pos = agent.get_position()
    turn = calc_turn_value((current_pos[0], current_pos[2]), (position[0], position[1]), current_yaw)
    # Calculate a speed to use - helps to avoid orbiting:
    dx = position[0] - current_pos[0]
    dz = position[1] - current_pos[2]
    speed = 1.0 - (old_div(1.0, (1.0 + abs(old_div(dx, 3.0)) + abs(old_div(dz, 3.0)))))
    if abs(dx) + abs(dz) < 1.0:
        speed = 0
        
    return speed, turn
