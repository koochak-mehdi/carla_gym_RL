from agent.replay_buffer import ReplayBuffe
from agent.ou_action_noise import OUActionNoise
from model.actor_netwrk import ActorNetwork
from model.critic_network import CriticNetwork

import torch as t
import torch.nn.functional as F
import numpy as np
import pylab, pickle, os

class AgentDDPG:
    def __init__(self, env_name, lr_a, lr_c, in_dims, tau, n_actions, gamma=.99,
                    max_size=10_000_000, fc1_dims=400, fc2_dims=300, batch_size=64,
                    tmp_path=None):
        self.env_name = env_name
        self.gamma = gamma
        self.tau = tau
        self.batch_size = batch_size
        self.lr_a = lr_a
        self.lr_c = lr_c

        if tmp_path is None:
            self.tmp_path = '/home/omen_ki_rechner/Documents/Mehdi/carla_gym_RL/tmp'
        else:
            self.tmp_path = tmp_path

        self.epsilon_min    = .01
        self.epsilon        = 1.0
        self.epsilon_decay  = .0000005
        self.explore_probability = self.init_expl_prob()

        #self.memory = ReplayBuffe(max_size, in_dims, n_actions)
        self.memory = self.load_buffer(max_size, in_dims, n_actions)
        self.noise = OUActionNoise(mu=np.zeros(n_actions))

        self.actor = ActorNetwork(in_dims, fc1_dims, fc2_dims, n_actions, lr_a, 'actor', chkpt_dir=os.path.join(self.tmp_path, 'ddpg'))
        self.target_actor = ActorNetwork(in_dims, fc1_dims, fc2_dims, n_actions, lr_a, 'target_actor', chkpt_dir=os.path.join(self.tmp_path, 'ddpg'))

        self.critic = CriticNetwork(in_dims, fc1_dims, fc2_dims, n_actions, lr_c, 'critic', chkpt_dir=os.path.join(self.tmp_path, 'ddpg'))
        self.target_critic = CriticNetwork(in_dims, fc1_dims, fc2_dims, n_actions, lr_c, 'target_critic', chkpt_dir=os.path.join(self.tmp_path, 'ddpg'))

        self.update_network_parameters(tau=1)

        pylab.figure(figsize=(18, 9))
        self.plot_info_dict = self.init_plot_info()
    
    def load_buffer(self, max_size, in_dims, n_actions):
        if os.path.isfile(os.path.join(self.tmp_path, 'buffer', 'memory.pkl')):
            print('... loading buffer ...')
            with open(os.path.join(self.tmp_path, 'buffer', 'memory.pkl'), 'rb') as memoryPkl:
                return pickle.load(memoryPkl)
        else:
            print('... creating buffer ...')
            return ReplayBuffe(max_size, in_dims, n_actions)

    def init_plot_info(self):
        # load plot Info
        plot_pkl_path = os.path.join(self.tmp_path, 'plot_info', 'plotInfo.pkl')
        if os.path.exists(plot_pkl_path):
            print('... loading plot info ...')
            with open(plot_pkl_path, 'rb') as pltInfoPklFile:
                return pickle.load(pltInfoPklFile)
        else:
            print('... creating plot info ...')
            return {'scores': list(), 'episodes': list(), 'average': list()}

    def save_buffer(self):
        print('... saving memory buffer ...')
        with open(os.path.join(self.tmp_path, 'buffer', 'memory.pkl'), 'wb') as memoryPkl:
            pickle.dump(self.memory, memoryPkl)     

    def init_expl_prob(self):
        expl_prob_path = os.path.join(self.tmp_path, 'expl_prob', 'expl_prob.txt')
        if os.path.exists(expl_prob_path):
            with open(expl_prob_path, 'r') as explFile:
                print('... loading explore probabilty ...')
                return float(explFile.readline())
        else:
            return 0.0
    
    def save_expl_prob(self, expl_prob):
        expl_prob_path = os.path.join(self.tmp_path, 'expl_prob', 'expl_prob.txt')
        with open(expl_prob_path, 'w') as explFile:
            print('... saving explore probability ...')
            explFile.write(str(expl_prob))

    def choose_action(self, observation, decay_step):
        self.explore_probability = self.epsilon_min + (self.epsilon - self.epsilon_min) * np.exp(-self.epsilon_decay * decay_step)

        self.actor.eval()
        state = t.tensor(np.array(observation), dtype=t.float, device=self.actor.device)

        mu = self.actor.forward(state)

        if self.explore_probability > np.random.rand():
            #print('... random action ...')
            noise = t.tensor(self.noise()/10, dtype=t.float, device=self.actor.device)
            mu_prime = mu.clone()
            mu_prime[0] = mu[0] + noise[0]
            mu_prime[1] = mu[1] - noise[1] * 10#*.6
            
            mu_prime = t.clamp(mu_prime, min=-1, max=1).to(self.actor.device)         
            self.actor.train()
            return mu_prime.cpu().detach().numpy(), self.explore_probability
        else:
            #print('... model action ...')
            self.actor.train()
            return mu.cpu().detach().numpy(), self.explore_probability

    def remember(self, state, action, reward, new_state, done):
        self.memory.store_transition(state, action, reward, new_state, done)

    def save_models(self):
        self.actor.save_checkpoint()
        self.target_actor.save_checkpoint()
        self.critic.save_checkpoint()
        self.target_critic.save_checkpoint()

    def load_models(self):
        self.actor.load_checkpoint()
        self.target_actor.load_checkpoint()
        self.critic.load_checkpoint()
        self.target_critic.load_checkpoint()

    def learn(self):
        if self.memory.mem_cntr < self.batch_size:
            return
        #print('from agent -- learning started!')
        
        states, actions, rewards, new_states, dones = self.memory.sample_buffer(self.batch_size)

        states      = t.tensor(states, dtype=t.float, device=self.actor.device)
        actions     = t.tensor(actions, dtype=t.float, device=self.actor.device)
        rewards     = t.tensor(rewards, dtype=t.float, device=self.actor.device)
        new_states  = t.tensor(new_states, dtype=t.float, device=self.actor.device)
        dones       = t.tensor(dones, device=self.actor.device)

        target_action   = self.target_actor.forward(new_states)
        critic_value_   = self.target_critic.forward(new_states, target_action)
        critic_value    = self.critic.forward(states, actions)

        critic_value_[dones]    = 0.0
        critic_value_           = critic_value_.view(-1)

        target = rewards + self.gamma * critic_value_
        target = target.view(self.batch_size, 1)

        self.critic.optimizer.zero_grad()
        critic_loss = F.mse_loss(target, critic_value)
        critic_loss.backward()
        self.critic.optimizer.step()

        self.actor.optimizer.zero_grad()
        actor_loss  = -self.critic.forward(states, self.actor.forward(states))
        actor_loss  = t.mean(actor_loss) 
        actor_loss.backward()
        self.actor.optimizer.step()

    def update_network_parameters(self, tau=None):
        if tau is None:
            tau = self.tau
        
        actor_params         = self.actor.named_parameters()
        target_actor_params  = self.target_actor.named_parameters()

        critic_params        = self.critic.named_parameters()
        target_critic_params = self.target_critic.named_parameters()

        actor_state_dict         = dict(actor_params)
        target_actor_state_dict  = dict(target_actor_params)

        critic_state_dict        = dict(critic_params)
        target_critic_state_dict = dict(target_critic_params)

        for name in actor_state_dict:
            actor_state_dict[name] = tau * actor_state_dict[name].clone() + \
                                    (1-tau) * target_actor_state_dict[name].clone()

        for name in critic_state_dict:
            critic_state_dict[name] = tau * critic_state_dict[name].clone() +\
                                    (1-tau) * target_critic_state_dict[name].clone()
        
        self.target_actor.load_state_dict(actor_state_dict)
        self.target_critic.load_state_dict(critic_state_dict)

    def plot_results(self, score, episode):
        self.plot_info_dict['scores'].append(score)
        self.plot_info_dict['episodes'].append(episode)
        self.plot_info_dict['average'].append(sum(self.plot_info_dict['scores'])/len(self.plot_info_dict['scores']))

        pylab.plot(self.plot_info_dict['episodes'], self.plot_info_dict['scores'], 'b')
        pylab.plot(self.plot_info_dict['episodes'], self.plot_info_dict['average'], 'r')

        pylab.xlabel('steps', fontsize=18)
        pylab.ylabel('score', fontsize=18)

        try:
            pylab.savefig(f'{self.env_name}_ddpg_ac.png')
        except OSError as e:
            print(e)
        
        return str(self.plot_info_dict['average'][-1])
    
    def save_plot_info(self):
        print('... saving plot info ...')
        with open(os.path.join(self.tmp_path, 'plot_info', 'plotInfo.pkl'), 'wb') as pltIinfoPklFile:
            pickle.dump(self.plot_info_dict, pltIinfoPklFile)
        

    