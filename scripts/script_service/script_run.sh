#!/bin/bash

LOG=$(cat /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/script_log)
SCRIPT_SCREEN="script_screen"
PYTHON=$(which python)
SCREEN=$(which screen)
CONDA=$(which conda)


${PYTHON} /home/${USER}/Documents/Mehdi/carla_gym_RL/first_try_ddpg.py

sudo systemctl stop script_check.service
#${SCREEN} -S ${SCRIPT_SCREEN} -X quit