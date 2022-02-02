import os
#os.environ["SDL_VIDEODRIVER"]="dummy"

import carla
import gym
from gym import spaces
import pygame
import numpy as np
import math

from carla_gym.component.hud import HUD
from carla_gym.component.others import SCALING_FACTOR
from carla_gym.component.world import World



#from rich import print

from carla_gym.parking_component.parking_world import ParkingWorld

class CarlaEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, args):
        super(CarlaEnv, self).__init__()
        print(args['init_message'])

        self.action_space   = spaces.Tuple((
            spaces.Box(low=-1, high=1, shape=(1,)),
            spaces.Box(low=-0.7, high=0.7, shape=(1,))#,
            #spaces.Box(low=0, high=1, shape=(1,))
            #Discrete(2)
        ))
        

        self.args           = args
        self.verbose        = args['verbose']
        self.T_episode      = args['T_episode']
        self.cnt_episode    = 0
        self._init_carla_world()
        self._init_pygame()

        self.hud            = HUD(args['width'], args['height'])
        self.world          = World(self.sim_world, self.hud, args)
        self.parking_world  = ParkingWorld(args)
        self.desired_slot   = self.parking_world.desired_slot
        self.controller     = carla.VehicleControl()
        
        self.sim_world.tick()
        self.clock = pygame.time.Clock()

        self.agent          = self.world.player
        self.agn_location   = self.agent.get_transform()
        self.agn_velocity   = self.agent.get_velocity()
        self.state          = None
        
        self.action_space_shape      = (2,) #(3,)
        self.observation_space_shape = (11,)

        self.last_x = None
        self.last_y = None
        

    def step(self, action):
        #print('from env -- action --', action)
        
        self.controller.throttle = float(action[0])
        if self.controller.throttle < 0:
            self.controller.reverse = True
        else:
            self.controller.reverse = False

        self.controller.steer = float(action[1])
        #self.controller.brake = float(action[2])

        self.world.player.apply_control(self.controller)

        self.sim_world.tick()
        state = self._get_state()
        done = False

        # check whether it's out of parking
        reward_out_of_parking = 0
        if (state[0] > 21.5) or (state[0] < -41.0):
            done = True
            reward_out_of_parking = -7_000

        # check collision
        reward_collision = 0
        if self.world.collision_sensor.collided_obj:
            print('heyyyyyyyyy!')
            done = True
            reward_collision = -5_000

        # check heatMap
        reward_heatMap = self._get_reward_heatMap()

        # check distance
        reward_distance = self._get_reward_d(self.desired_slot)

        # check angle
        reward_angle = self._get_reward_a(self.desired_slot)

        # obstacle sensors
        #print('-'*50)
        #self._get_obs_sensor_data()
        
        if reward_heatMap >= 0:
            reward = reward_angle + reward_collision + reward_out_of_parking + reward_heatMap / reward_distance 
        else:
            reward = reward_angle + reward_collision + reward_out_of_parking + reward_heatMap

        if self.args['verbose']:
            #print(f'r: {reward} -- r_d: {reward_distance} -- r_h: {reward_heatMap} -- r_c: {reward_collision}')
            pass

        self.clock.tick_busy_loop(60)
        self.world.tick(self.clock)
        self.world.render(self.displays[0])
        self.parking_world.render(self.displays[1])
        self.cnt_episode += 1
        if self.cnt_episode >= self.T_episode:
            if reward_distance > .5:
                reward += -100
            done = True

        return state, reward, done, {}

    def reset(self):
        self.cnt_episode    = 0
        self.world.restart()
        self.agent          = self.world.player
        while self.agent.get_transform().location.z > 0.2:
            self.sim_world.tick()
            self.clock.tick_busy_loop(60)
            self.world.tick(self.clock)
            self.world.render(self.displays[0])
            self.parking_world.render(self.displays[1])
            if self.args['render']:
                self.render()
        state               = self._get_state()

        return state

    def render(self, mode='human'):
        cnt = 0
        for i in range(self.i):
            for j in range(self.j):
                self.screen.blit(self.displays[cnt], (640*i, 480*j))
                cnt += 1

        pygame.display.flip()
        pass

    def close(self):
        if self.world:
            self.world.destroy()
        if self.parking_world:
            self.parking_world.reset()
        pass

    def _init_carla_world(self):
        self.client = carla.Client(self.args['host'], self.args['port'])
        self.client.set_timeout(self.args['timeout'])
        self.sim_world = self.client.load_world(self.args['map'])
        self.sim_world.unload_map_layer(self.args['unloaded_part'])

        self.original_settings = self.sim_world.get_settings()
        self.settings = self.sim_world.get_settings()
        if not self.settings.synchronous_mode:
            self.settings.synchronous_mode = True
            self.settings.fixed_delta_seconds = self.args['dt']
        self.sim_world.apply_settings(self.settings)

        self.traffic_manager = self.client.get_trafficmanager()
        self.traffic_manager.set_synchronous_mode(True)
    
    def _init_pygame(self):
        pygame.init()
        pygame.font.init()

        #TODO: check how to handle none case
        self.screen, self.displays = self._create_displays()
        if self.screen:
            self.screen.fill((0,0,0))
        pygame.display.flip()    

    def _create_displays(self):
        w = self.args['width']
        h = self.args['height']
        n = self.args['camera_number']
        #print(w, h, n)
        displays = list()

        def get_i_j(n):
            if n <= 3:
                return n, 1
            elif n == 4:
                return 2, 2
            elif (n>4) and (n<=6):
                return 2, n//2

        if self.verbose:
            print('pygame screen created.')
        
        self.i, self.j = get_i_j(n)

        '''screen = pygame.display.set_mode(
            (w * self.i, h * self.j),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )'''

        pygame.init()

        screen = pygame.display.set_mode(
            (w * self.i, h * self.j)
        )

        for i in range(n):
            displays.append(
                pygame.Surface((w, h))
            )
            if self.verbose:
                print(f'{i} -- display created')
 

        return screen, displays

    def _get_location(self):
        transform   = self.world.player.get_transform()
        location    = transform.location
        rotation    = transform.rotation
        
        return (location.x, location.y, location.z), \
                (rotation.yaw)
    
    def _get_velocity(self):
        velocity    = self.world.player.get_velocity()
        speed       = 3.6 * math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
        return speed
    
    def _get_state(self):
        location, rotation  = self._get_location()
        speed               = self._get_velocity()
        obs_sensor          = self._get_obs_sensor_data()
        state = np.array(
            [*location, rotation, speed, *obs_sensor],
            dtype=np.float32
        )
        return state
    
    def _get_obs_sensor_data(self):
        obs_front_center    = self.world.obstacle_sensor_front_center.get_distance()        
        obs_front_left      = self.world.obstacle_sensor_front_left.get_distance()
        obs_front_right     = self.world.obstacle_sensor_front_right.get_distance()
        obs_rear_center     = self.world.obstacle_sensor_rear_center.get_distance()
        obs_rear_left       = self.world.obstacle_sensor_rear_left.get_distance()
        obs_rear_right      = self.world.obstacle_sensor_rear_right.get_distance()
        return obs_front_center, obs_front_right, obs_front_left, obs_rear_center, obs_rear_right, obs_rear_left

    def _get_reward_d(self, s_location):
        location, rotation = self._get_location()
        location = np.array(location[:2])
        s_location = np.array([s_location.x, s_location.y])

        d       = np.linalg.norm((location - s_location), 2) # * (-1)
        reward  = self.args['w'] * d / self.args['d_max']
        
        #print('from agent, reward d -- ', 10 * reward)
        return reward 
    
    def _get_reward_a(self, s_location):
        location, yaw = self._get_location()
        location = np.array(location[:2])
        s_location = np.array([s_location.x, s_location.y])

        if np.linalg.norm((location - s_location), 2) < 8.0:
            #yaw = rotation[1]
            a = -np.abs((yaw - 180)/ 180)
        else:
            a = 0
        
        return a
    
    def _get_reward_heatMap(self):
        location = self.world.player.get_transform().location
        x = location.x 
        y = location.y 

        # target
        flag_target = False
        if ((x > -940.0 and x < -460.0) and (y > -4530.0 and y < -4240.0)):
            flag_target = True
            rewad_heatMap = 5000

        if self.last_x is not None:
            if not flag_target:
                if (np.power((self.last_x - x), 2) + np.power((self.last_y - y), 2) < .2*.2 ):
                    return 0
            else:
                return rewad_heatMap
                
        flag_slots = False
        flag_lvl5 = False
        flag_lvl4 = False
        flag_lvl3 = False
        flag_lvl2 = False

        rewad_heatMap = 0

        # out of parking
        if (x > 2000):
            rewad_heatMap = -500
            return rewad_heatMap

        
        
        # inside slots
        if (((x > 130.0 and x < 1230.0) and (y > -4530.0 and y < -1740.0)) or \
        ((x > -1530.0 and x < -460.0) and (y > -4530.0 and y < -1740.0)) or \
        ((x > -3140.0 and x < -2080.0) and (y > -4530.0 and y < -1740.0))) and \
            not flag_target:
            flag_slots = True
            rewad_heatMap = 0
        
        # level 5
        if ((x > -3860 and x < -1530) and (y > -5010 and y < -965)) and (not flag_slots):
            flag_lvl5 = True
            rewad_heatMap = .5
        
        # new level 5
        m_5 = (-3700 + 3037) / (2030 - 1230)
        if ((x > 130.0 and y < -3037) and (y < m_5 * (x - 2030) - 3700)) and \
            not flag_slots:
            print('level 5')
            flag_lvl5 = True
            rewad_heatMap = .5

        # level 4
        m4 = (-1740 + 995) / (-460 + 485)
        if (y < (m4 * (x + 460) - 1740)) and \
                        (not flag_target) and \
                        (not flag_lvl5) and \
                        (not flag_slots):
            flag_lvl4 = True
            rewad_heatMap = 1
        
        # level 3
        m_31 = (-1700 + 995) / (2030 + 485)
        m_32 = (-3700 + 3037) / (2030 - 1230)
        if y > (m_31 * (x - 2030) - 1700) and (not flag_slots):
            flag_lvl3 = True
            rewad_heatMap = 3
        '''if ((x > 130.0 and y < -3037) and (y < m_32 * (x - 2030) - 3700)) and (not flag_slots):
            flag_lvl3 = True
            rewad_heatMap = 3'''

        # level 2
        m_21 = (-3037 + 2370) / (2030 - 1230)
        m_22 = (-4530 + 4240) / (-460 - 130)
        if ((x > 1230 and x < 2030) and (y < m_21 * (x - 2030) - 3037) and (y > m_21 * (x - 2030) - 3700)) or \
            ((x > -460 and x < 130) and (y > m_22 * (x + 460) + 4530)) \
                                                    and (not flag_lvl4):
            flag_lvl2 = True
            rewad_heatMap = 5
        
        # level 1
        if (not flag_lvl2) and (not flag_lvl3) and (not flag_lvl4) \
            and (not flag_lvl5) and (not flag_slots) and (not flag_target):
            flag_lvl1 = True
            rewad_heatMap = 10
        
        self.last_x = x
        self.last_y = y

        return rewad_heatMap

