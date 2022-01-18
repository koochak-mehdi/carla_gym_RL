from enum import Enum
import carla

class Population(Enum):
    empty = 0
    secluded = 1
    normal = 2
    crowded = 3

class Visualization(Enum):
    hide = 0
    show = 1

red = carla.Color(255, 0, 0)
green = carla.Color(0, 255, 0)
blue = carla.Color(47, 210, 231)
cyan = carla.Color(0, 255, 255)
yellow = carla.Color(255, 255, 0)
orange = carla.Color(255, 162, 0)
white = carla.Color(255, 255, 255)

SCALING_FACTOR = .01
THICKNESS = .05