from gym.envs.registration import register

register(
    id='carla-env-v0',
    entry_point='carla_gym.envs:CarlaEnv'
)