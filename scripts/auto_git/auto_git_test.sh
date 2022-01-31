#!/bin/bash

DATELOG=`date +'%Y-%m-%d-%H-%M-%S'`
LOG="/home/${USER}/Documents/Mehdi/carla_gym_RL/logs/git_logs/${DATELOG}.log"
SCREEN=$(which screen)
AUTOGIT_SCREEN="autogit_screen"

echo $LOG > /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/autogit_log



${SCREEN} -dm ${AUTOGIT_SCREEN}
${SCREEN} -S ${AUTOGIT_SCREEN} -X stuff $'/home/mehdi/Documents/Mehdi/carla_gym_RL/scripts/auto_git/auto_git_run.sh\n'
