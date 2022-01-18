import carla
from rich import print

from carla_gym.component.others import *

class BbVisualizer:
    def __init__(self, world, life_time):
        self.world = world
        self.life_time = life_time
        
        self.debug = self.world.debug

        self.vehicles_list = None
        self.occupied_slots = None
        self.bb_list = None

    def update_info(self, vehicles, occupied):
        self.vehicles_list = vehicles
        self.occupied_slots = occupied
    
    def update_scene(self):
        for i in range(len(self.occupied_slots)):
            bb = self.vehicles_list[i].bounding_box
            bb.location = carla.Location(
                x = self.occupied_slots[i].x,
                y = self.occupied_slots[i].y,
                z = bb.location.z + 21 * SCALING_FACTOR
            )

            self.draw_box(bb)
    
    def draw_box(self, bb):
        self.debug.draw_box(
            box=bb,
            rotation=carla.Rotation(0,0,0),
            thickness=THICKNESS,
            color=yellow,
            life_time=self.life_time,
            persistent_lines=False
        )