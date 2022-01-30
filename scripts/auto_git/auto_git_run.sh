#!/bin/bash

REPO='/home/mehdi/Documents/Mehdi/carla_gym_RL'
COMMIT_TIMESTAMP=`date +'%Y-%m-%d %H:%M:%S'`
GIT=$(which git)
DATELOG=`date +'%Y-%m-%d-%H-%M-%S'`
LOG="/home/${USER}/Documents/Mehdi/carla_gym_RL/logs/git_logs/${DATELOG}.log"
AUTOGIT_SCREEN="autogit_screen"

cd ${REPO}
${GIT} add --all . >> ${LOG}
${GIT} commit -m "Automated commit on ${COMMIT_TIMESTAMP}" >> ${LOG}
${GIT} push origin test_learing >> ${LOG}

sudo systemctl stop auto_git.service
${SCREEN} -S ${AUTOGIT_SCREEN} -X quit