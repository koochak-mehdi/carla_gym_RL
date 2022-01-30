#!/bin/bash

DATELOG=`date +'%Y-%m-%d-%H-%M-%S'`
LOG="/home/${USER}/Documents/Mehdi/carla_gym_RL/logs/carla_logs/${DATELOG}_test.log"
SCREEN=$(which screen)
CARLA_SCREEN="carla_screen"

echo $LOG > /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/varlog_carla

${SCREEN} -dm ${CARLA_SCREEN}
${SCREEN} -S ${CARLA_SCREEN} -X stuff $'/home/mehdi/Documents/Mehdi/carla_gym_RL/scripts/carla_service/carla_run.sh\n'