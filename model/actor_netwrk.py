import torch as t
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import numpy as np
import os
from rich import print

class ActorNetwork(nn.Module):
    def __init__(self, in_size, fc1_dims, fc2_dims, out_size, l_rate, name, 
            chkpt_dir='../tmp/ddpg'):
        super(ActorNetwork, self).__init__()
        self.name = name
        self.checkpoint_dir = chkpt_dir
        self.checkpoint_file = os.path.join(chkpt_dir, name + '_ddpg.pth')
        self.checkpoint_file_best = os.path.join(chkpt_dir, name + '_best_ddpg.pth')

        self.fc1 = nn.Linear(in_size, fc1_dims)
        self.fc2 = nn.Linear(fc1_dims, fc2_dims)

        self.bn1 = nn.LayerNorm(fc1_dims)
        self.bn2 = nn.LayerNorm(fc2_dims)

        self.mu = nn.Linear(fc2_dims, out_size)

        f1 = 1./np.sqrt(self.fc1.weight.data.size()[0])
        self.fc1.weight.data.uniform_(-f1, f1)
        self.fc1.bias.data.uniform_(-f1, f1)

        f2 = 1./np.sqrt(self.fc2.weight.data.size()[0])
        self.fc2.weight.data.uniform_(-f2, f2)
        self.fc2.bias.data.uniform_(-f2, f2)

        f3 = .003
        self.mu.weight.data.uniform_(-f3, f3)
        self.mu.bias.data.uniform_(-f3, f3)

        self.optimizer = optim.Adam(self.parameters(), lr=l_rate)

        self.device = 'cuda' if t.cuda.is_available() else 'cpu'
        self.to(self.device)


    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        x = F.relu(self.bn2(self.fc2(x)))
        x = self.mu(x)
        #print(f'from actor -- x: ', x.shape)
        if len(x.shape) == 1:
            x1 = t.tanh(x[:-1])
            x2 = (t.tanh(x[-1]).clone()*(.6)).detach().requires_grad_(True).view(-1)
        else:
            x1 = t.tanh(x[:-1, :])
            x2 = (t.tanh(x[-1, :]).clone()*(.6)).detach().requires_grad_(True).view(1, -1)
            

        #print(f'from actor -- x1: {x1.shape} -- x2: {x2.shape}')
        x = t.cat((x1, x2))
        
        return x

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