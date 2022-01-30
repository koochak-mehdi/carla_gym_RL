#!/bin/bash

LOG=$(cat /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/varlog)
PYTHON=$(which python)
SCREEN=$(which screen)
SCRIPT_SCREEN="script_screen"
#for i in 0 1 2 3 4 5 6 7 8 9 10
#do
#    echo "The date is task1: $(date)" >> ${LOG}
#    sleep 1
#done
${PYTHON} /home/${USER}/Documents/Mehdi/carla_gym_RL/scripts/test.py
echo "mehdi" >> ${LOG}
sudo systemctl stop script_check.service
${SCREEN} -S ${SCRIPT_SCREEN} -X quit