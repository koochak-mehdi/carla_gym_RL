import collections
import carla
import pandas as pd
import os, time

from rich import print

from carla_gym.component.others import *


class SlotVisualizer:
    def __init__(self, world, life_time):
        self.world = world
        self.debug = world.debug
        self.life_time = life_time
        self.border = (460 * SCALING_FACTOR, 220 * SCALING_FACTOR)

        self.free_slots = None
        self.occupied_slots = None
    
    def update_info(self, occupied, free):
        self.occupied_slots = occupied
        self.free_slots = free
    
    def update_scene(self):
        #print('-' * 50)
        print('from vis -- %s free' %len(self.free_slots))
        for slot in self.free_slots:
            print(slot)
            self.draw_border(slot, green)

        print('-' * 50)
        print('from vis -- %s occupied' %len(self.occupied_slots))
        for slot in self.occupied_slots:
            slot = carla.Location(
                x = slot.x,
                y = slot.y,
                z = 21 * SCALING_FACTOR
            )
            print(slot)
            self.draw_border(slot, red)

    def draw_border(self, slot, color):

        lt, rt, lb, rb = self.get_border(slot)

        #self.debug.draw_string(location=slot, text=txt, draw_shadow=False, color=red, life_time=self.life_time)
        self.debug.draw_point(slot, .1, color, self.life_time, False)
        self.debug.draw_line(
            lt,
            rt,
            thickness=THICKNESS, 
            color=color, 
            life_time=self.life_time, 
            persistent_lines=False)
        self.debug.draw_line(
            lt,
            lb,
            thickness=THICKNESS, 
            color=color, 
            life_time=self.life_time, 
            persistent_lines=False)
        self.debug.draw_line(
            lb,
            rb,
            thickness=THICKNESS, 
            color=color, 
            life_time=self.life_time, 
            persistent_lines=False)
        self.debug.draw_line(
            rb,
            rt,
            thickness=THICKNESS, 
            color=color, 
            life_time=self.life_time, 
            persistent_lines=False)
        

    def get_border(self, center):
        lt = carla.Location(
            x = (center.x + self.border[0]/2) ,
            y = (center.y + self.border[1]/2) ,
            z = center.z
        )
        rt = carla.Location(
            x = (center.x - self.border[0]/2) ,
            y = (center.y + self.border[1]/2) ,
            z = center.z
        ) 
        lb = carla.Location(
            x = (center.x + self.border[0]/2) ,
            y = (center.y - self.border[1]/2) ,
            z = center.z
        )
        rb = carla.Location(
            x = (center.x - self.border[0]/2) ,
            y = (center.y - self.border[1]/2) ,
            z = center.z
        )
        return lt, rt, lb, rb

    

if __name__ == '__main__':
    client = carla.Client('localhost', 2000)
    client.set_timeout(20)
    world = client.load_world('Town05_opt')
    world.unload_map_layer(carla.MapLayer.ParkedVehicles)
    '''spectator = world.get_spectator()
    spectator_trs = carla.Transform(
        carla.Location(
            x = -1050 * SCALING_FACTOR,
            y = -3150 * SCALING_FACTOR,
            z = 2250 * SCALING_FACTOR
        ),
        carla.Rotation(
            pitch = 270,
            yaw = 90
        )
    )
    spectator.set_transform(spectator_trs)

    csv_path = '/Carla/CARLA_0.9.12/PythonAPI/my_scripts/park_platz/slot_locations.csv'
    obj = SlotVisualizer(world, csv_path, 20)
    obj.update_scene()
    time.sleep(20)'''