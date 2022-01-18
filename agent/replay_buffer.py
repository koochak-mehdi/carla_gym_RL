import numpy as np
import pickle, os

class ReplayBuffe(object):
    def __init__(self, max_size, in_shape, n_actions):
        self.mem_size = max_size
        self.mem_cntr = 0
        self.state_memory = np.zeros((self.mem_size, in_shape))
        self.action_memory = np.zeros((self.mem_size, n_actions))
        self.reward_memory = np.zeros(self.mem_size)
        self.new_state_memory = np.zeros((self.mem_size, in_shape))
        self.done_memory = np.zeros(self.mem_size, dtype=bool)
        self.pickling_path = '/Carla/CARLA_0.9.12/PythonAPI/my_scripts/carla_scripts/carla_gym_custome_env/tmp/buffer'

    def store_transition(self, state, action, reward, state_, done):
        idx = self.mem_cntr % self.mem_size
        self.state_memory[idx] = state
        self.action_memory[idx] = action
        self.reward_memory[idx] = reward
        self.new_state_memory[idx] = state_
        self.done_memory[idx] = done

        self.mem_cntr += 1

    def sample_buffer(self, batch_size):
        max_mem = min(self.mem_cntr, self.mem_size)

        batch = np.random.choice(max_mem, batch_size)

        states = self.state_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        new_states = self.new_state_memory[batch]
        dones = self.done_memory[batch]

        return states, actions, rewards, new_states, dones
    