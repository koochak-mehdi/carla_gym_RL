import torch as t
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import os
import numpy as np

from rich import print

class CriticNetwork(nn.Module):
    def __init__(self, in_size, fc1_dims, fc2_dims, out_size, l_rate, name, 
            chkpt_dir='/home/omen_ki_rechner/Documents/Mehdi/carla_gym_RL/tmp/ddpg'):
        super(CriticNetwork, self).__init__()
        self.name = name
        self.checkpoint_dir = chkpt_dir
        self.checkpoint_file = os.path.join(chkpt_dir, name + '_ddpg.pth')
        self.checkpoint_file_best = os.path.join(chkpt_dir, name + '_best_ddpg.pth')

        self.fc1 = nn.Linear(in_size, fc1_dims)
        self.fc2 = nn.Linear(fc1_dims, fc2_dims)

        self.bn1 = nn.LayerNorm(fc1_dims)
        self.bn2 = nn.LayerNorm(fc2_dims)
        
        self.action_value = nn.Linear(out_size, fc2_dims)

        self.q = nn.Linear(fc2_dims, 1)

        f1 = 1./np.sqrt(self.fc1.weight.data.size()[0])
        self.fc1.weight.data.uniform_(-f1, f1)
        self.fc1.bias.data.uniform_(-f1, f1)

        f2 = 1./np.sqrt(self.fc2.weight.data.size()[0])
        self.fc2.weight.data.uniform_(-f2, f2)
        self.fc2.bias.data.uniform_(-f2, f2)

        f3 = 1./np.sqrt(self.action_value.weight.data.size()[0])
        self.action_value.weight.data.uniform_(-f3, f3)
        self.action_value.bias.data.uniform_(-f3, f3)

        f4 = .003
        self.q.weight.data.uniform_(-f4, f4)
        self.q.bias.data.uniform_(-f4, f4)

        self.optimizer = optim.Adam(self.parameters(), lr=l_rate, weight_decay=.01)

        self.device = 'cuda' if t.cuda.is_available() else 'cpu'
        self.to(self.device)

    def forward(self, state, action):
        state_value = F.relu(self.bn1(self.fc1(state)))
        state_value = self.bn2(self.fc2(state_value))

        action_value = self.action_value(action)

        state_action_value = F.relu(t.add(state_value, action_value))
        state_action_value = self.q(state_action_value)

        return state_action_value

    def save_checkpoint(self):
        print('... saving checkout ...')
        t.save(self.state_dict(), self.checkpoint_file)

    def load_checkpoint(self):
        print('... loading checkpoint ...')
        self.load_state_dict(t.load(self.checkpoint_file))

    def save_best(self):
        print('... saving best checkpoint ...')
        t.save(self.state_dict, self.checkpoint_file_best)
    
    def load_best(self):
        print('... loading best checkpoint ...')
        self.load_state_dict(t.load(self.checkpoint_file_best))