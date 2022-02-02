#!/bin/bash

DATELOG=`date +'%Y-%m-%d-%H-%M-%S'`
LOG="/home/${USER}/Documents/Mehdi/carla_gym_RL/logs/script_logs/${DATELOG}_test.log"
SCREEN=$(which screen)
SCRIPT_SCREEN="script_screen"

echo $LOG > /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/script_log



${SCREEN} -dm ${SCRIPT_SCREEN}
${SCREEN} -S ${SCRIPT_SCREEN} -X stuff $'conda activate carla_env\n'
${SCREEN} -S ${SCRIPT_SCREEN} -X stuff $'/home/omen_ki_rechner/Documents/Mehdi/carla_gym_RL/scripts/script_service/script_run.sh\n'

