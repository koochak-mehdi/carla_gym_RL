import carla
import pygame
import random, time
import numpy as np
import pandas as pd
import json, os

from carla import ColorConverter as cc

from carla_gym.component.others import *
from carla_gym.parking_component.slot_visualizer import SlotVisualizer
from carla_gym.parking_component.bb_visualizer import BbVisualizer

#rom rich import print

class ParkingWorld:
    def __init__(self, args):
        self.args = args
        self.verbose = args['verbose']
        self._init_carla()

        self.slots_db       = pd.read_csv(os.path.join(args['data_path'], args['slots_csv']))
        self.camera_db      = self._load_camera_db()
        self.camera_main    = args['parking_camera']
        self.pMode          = args['pMode']

        self.camera         = self._init_camera()
        
        self.n_samples      = self._get_n_samples()

        self.occupied_slots = list()
        self.free_slots     = list()
        self.desired_slot   = self._set_desired_slot()

        self.ctr            = carla.VehicleControl()
        self.ctr.hand_brake = True

    def render(self, display):
        self.camera.listen(lambda data: self._render(self.camera, data, display))
    
        
    def _render(self, camera, data, display):
        image = data
        image.convert(cc.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        surface = pygame.surfarray.make_surface(array.swapaxes(0,1))
        display.blit(surface, (0,0))
        camera.stop()

    def _set_desired_slot(self):
        slot = carla.Location(
            x = -680 * SCALING_FACTOR,
            y = -4390 * SCALING_FACTOR,
            z = 21 * SCALING_FACTOR
        )
        debug = self.sim_world.debug
        debug.draw_point(slot, .1, green, self.args['sim_time'], False)
        return slot

    def _init_carla(self):
        self.client = carla.Client(self.args['host'], self.args['port'])
        self.client.set_timeout(self.args['timeout'])
        self.sim_world = self.client.get_world()
        
    def _load_camera_db(self):
        with open(os.path.join(self.args['data_path'], self.args['camera_json']), 'r') as jFile:
            camera_data = json.load(jFile)
        
        #camera_names = list(camera_data.keys())
        return camera_data #, camera_names
    
    def _init_camera(self):
        camera_bp = self.camera_bp = self.sim_world.get_blueprint_library().find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', f'{self.args["width"]}')
        camera_bp.set_attribute('image_size_y', f'{self.args["height"]}')

        camera_trs = carla.Transform(
                carla.Location(
                    x = self.camera_db[self.camera_main]['location'][0] * SCALING_FACTOR,
                    y = self.camera_db[self.camera_main]['location'][1] * SCALING_FACTOR,
                    z = self.camera_db[self.camera_main]['location'][2] * SCALING_FACTOR
                ),
                carla.Rotation(
                    pitch   = self.camera_db[self.camera_main]['rotation'][0],
                    yaw     = self.camera_db[self.camera_main]['rotation'][1],
                    roll    = self.camera_db[self.camera_main]['rotation'][2]
                )
            )
        return self.sim_world.try_spawn_actor(
                    camera_bp, camera_trs
                )

    def _get_n_samples(self):
        if self.pMode == Population.empty:
            return []
        elif self.pMode == Population.secluded:
            return random.randrange(1, 20)
        elif self.pMode == Population.normal:
            return random.randrange(21, 40)
        else:
            return random.randrange(41, 60)

    def reset(self):
        if self.camera:
            if self.verbose:
                print('parking world -- destroy -- ', self.camera)
            self.camera.destroy()