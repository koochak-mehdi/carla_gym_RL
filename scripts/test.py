import time

logFile = ''
try:
    with open('/home/mehdi/Documents/Mehdi/carla_gym_RL/vars/var_script_log', 'r') as fLog:
        logFile = fLog.readline().split('\n')[0]
except Exception:
    logFile = '/home/mehdi/Documents/Mehdi/carla_gym_RL/logs/unknown.log'

with open(logFile, 'w') as fLog:
    for i in range(10):
        fLog.write(str(i) + '\n')
        time.sleep(.5)