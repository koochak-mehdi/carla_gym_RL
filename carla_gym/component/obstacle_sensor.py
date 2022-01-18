import carla
import weakref
import math
from carla_gym.component.global_functions import get_actor_display_name

GREEN = carla.Color(0, 255, 0)
RED = carla.Color(255, 0, 0)

# ==============================================================================
# -- ObstacleSensor -----------------------------------------------------------
# ==============================================================================

class ObstacleSensor(object):
    def __init__(self, parent_actor, location, yaw, pointer=True, life_time=.05):
        self._parent = parent_actor
        self.location = location
        self.yaw = yaw
        self.pointer = pointer
        self.life_time = life_time
        world = self._parent.get_world()
        self.debug = world.debug
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp_trs = carla.Transform(
            self.location,
            carla.Rotation(yaw=yaw)
        )
        self.sensor = world.spawn_actor(bp, bp_trs, attach_to=self._parent)

        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: ObstacleSensor._on_obstacle(weak_self, event))
        self.distance = 5.0
    
    @staticmethod
    def _on_obstacle(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.distance = event.distance
        actor_type = get_actor_display_name(event.other_actor)
        #print(f'from obstacle sensor -- {actor_type} -- {event.distance}')
        if self.pointer:
            self._visualize(event.transform)
    
    def reset(self):
        self.distance = 5.0

    def get_distance(self):
        return self.distance
    
    def _visualize(self, sensor_trs):
        parent_trs = self._parent.get_transform()
        point_sesnor = carla.Location(
            x = sensor_trs.location.x,
            y = sensor_trs.location.y,
            z = sensor_trs.location.z 
        )
        yaw_converted = (sensor_trs.rotation.yaw) * math.pi / 180
        angle_left = (sensor_trs.rotation.yaw - 14) * math.pi / 180 
        angle_right = (sensor_trs.rotation.yaw + 14) * math.pi / 180 

        point_a = carla.Location(
            x = sensor_trs.location.x + 5*math.cos(yaw_converted),
            y = sensor_trs.location.y + 5*math.sin(yaw_converted),
            z = sensor_trs.location.z
        )
        point_b = carla.Location(
            x = sensor_trs.location.x + 5*math.cos(angle_left),
            y = sensor_trs.location.y + 5*math.sin(angle_left),
            z = sensor_trs.location.z
        )
        point_c = carla.Location(
            x = sensor_trs.location.x + 5*math.cos(angle_right),
            y = sensor_trs.location.y + 5*math.sin(angle_right),
            z = sensor_trs.location.z
        )

        self.debug.draw_line(point_sesnor, point_a, .02, RED, self.life_time, False)
        self.debug.draw_line(point_sesnor, point_b, .02, GREEN, self.life_time, False)
        self.debug.draw_line(point_sesnor, point_c, .02, GREEN, self.life_time, False)