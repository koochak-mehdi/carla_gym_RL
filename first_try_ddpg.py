import pickle
import gym
import carla
import carla_gym
import logging
from time import gmtime, strftime
import os

from agent.agent_ddpg import AgentDDPG
#from rich import print

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
print('root_dir -- ', ROOT_DIR)

date = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
log_dir = os.path.join(ROOT_DIR, 'logs', 'simulations')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

log_file = os.path.join(log_dir, date + '.log')
logging.basicConfig(level=logging.DEBUG,
                    filename=log_file,
                    filemode='w',
                    format='%(message)s')
logger = logging.getLogger(__name__)

def write_score_down(score):
    score_file_path = os.path.join(ROOT_DIR, 'score.txt')
    with open(score_file_path, 'w') as sFile:
        sFile.write(str(score))

def load_last_best_score():
    score_file_path = os.path.join(ROOT_DIR, 'score.txt')
    with open(score_file_path, 'r') as sFile:
        return float(sFile.readline())

def write_down_episode(episode):
    episode_file_path = os.path.join(ROOT_DIR, 'tmp/episode/episode.txt')
    with open(episode_file_path, 'w') as eFile:
        eFile.write(str(episode))

def load_last_episode():
    episode_file_path = os.path.join(ROOT_DIR, 'tmp/episode/episode.txt')
    with open(episode_file_path, 'r') as eFile:
        return int(eFile.readline())

if __name__ == '__main__':
    
    env_args = dict()
    env_args['init_message']    = 'Hi :)'
    env_args['env_name']        = 'carla-env-v0'
    env_args['host']            = '127.0.0.1'
    env_args['port']            = 2000
    env_args['timeout']         = 5.0
    env_args['map']             = 'Town05_opt'
    env_args['unloaded_part']   = carla.MapLayer.ParkedVehicles
    env_args['autopilot']       = False
    env_args['res']             = '640x480'
    env_args['filter']          = 'vehicle.mini.cooper_s_2021'
    env_args['generation']      = '1'
    env_args['rolename']        = 'hero'
    env_args['gamma_camera']    = 2.2
    env_args['sync']            = True
    env_args['dt']              = .01
    env_args['n_episodes']      = 10_000
    env_args['data_path']       = os.path.join(ROOT_DIR, 'carla_gym/data')
    env_args['slots_csv']       = 'slot_locations.csv'
    env_args['agent_csv']       = 'agent_locations.csv'
    env_args['agent_json']      = 'agent_loaction.json'
    env_args['camera_json']     = 'camera_locations.json'
    env_args['camera_number']   = 2
    env_args['parking_camera']  = 'main_camera'
    env_args['obs_sensor_pos']  = 'sensor_locations.json'
    env_args['pMode']           = None  # scenario
    env_args['vMode']           = None
    env_args['life_time']       = None
    env_args['render']          = True
    env_args['T_episode']       = 2000
    env_args['sim_time']        = env_args['dt'] * env_args['n_episodes'] * env_args['T_episode']
    env_args['min_score']       = -100_000
    env_args['tmp_path']        = os.path.join(ROOT_DIR, 'tmp')
    env_args['d_max']           = 43.5
    env_args['w']               = 1.0
    env_args['verbose']         = True
    env_args['width'], env_args['height'] = [int(x) for x in env_args['res'].split('x')]

    env = gym.make('carla-env-v0', args=env_args)
    in_dims = env.observation_space_shape[0]
    n_actions = env.action_space_shape[0]
    #print(in_dims, n_actions)

    agent = AgentDDPG(
        env_name=env_args['env_name'],
        lr_a=.0001,
        lr_c=.001,
        in_dims=in_dims,
        tau=.001,
        batch_size=64,
        fc1_dims=400,
        fc2_dims=300,
        n_actions=n_actions,
        tmp_path=os.path.join(ROOT_DIR, 'tmp'),
        logger=logger
    )
    
    # load Model
    models_path = os.path.join(env_args['tmp_path'], 'ddpg')
    if len(os.listdir(models_path)) != 0:
        agent.load_models()

    # load Buffer
    # this is done inside of agent

    # load episode
    episode_pkl_path = os.path.join(env_args['tmp_path'], 'episode', 'episode.txt')
    if os.path.exists(episode_pkl_path):
        e = load_last_episode()
    else:
        e = 0

    # load plot Inf
    # this part will also be done inside the agent 

    # load decay_step
    decay_step_path = os.path.join(env_args['tmp_path'], 'decay', 'decay_step.txt')
    if os.path.exists(decay_step_path):
        with open(decay_step_path, 'r') as decayFile:
            decay_step = int(decayFile.readline())
    else:
        decay_step = 0

    best_score = load_last_best_score()
    #for e in range(env_args['n_episodes']):
    while e < env_args['n_episodes']:
        title = '-'*25+ f' {e+1} '+ '-'*25
        logger.info(title)
        print(title)
        current_state = env.reset()
        done = False
        score = 0
        
        agent.noise.reset()

        while not done:
            if env_args['render']:
                env.render()

            action, explore_prob = agent.choose_action(current_state, decay_step)

            next_state, reward, done, _ = env.step(action)
            agent.remember(current_state, action, reward, next_state, done)

            agent.learn()

            score += reward
            current_state = next_state
            decay_step += 1
            with open(decay_step_path, 'w') as decayFile:
                decayFile.write(str(decay_step))

            if done:
                # save episode number
                write_down_episode(e)

                # save memory buffer
                agent.save_buffer()
                average = agent.plot_results(score, e)
                summery = f'episode: {e+1}/10000, score: {score}, average: {average}, ex-prob: {explore_prob}'
                print(summery)
                logger.info(summery)
                
                # save plot info lists
                agent.save_plot_info()

                # save explore prob
                agent.save_expl_prob(explore_prob)

                #if score > float(average):
                agent.save_models()

                if score > best_score:
                    best_score = score
                    write_score_down(best_score)
                    agent.save_models()
        e += 1
