#!/bin/bash

REPO="/home/${USER}/Documents/Mehdi/carla_gym_RL"
COMMIT_TIMESTAMP=`date +'%Y-%m-%d %H:%M:%S'`

LOG=$(cat /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/autogit_log)
AUTOGIT_SCREEN="autogit_screen"
UPDATE_FLAG=$(cat /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/update_flag)
BRANCH="ki"

# commands
GIT=$(which git)
BASH=$(which bash)
SCREEN=$(which screen)

cd ${REPO}
${GIT} pull --all >> ${LOG}
${GIT} add --all . >> ${LOG}
${GIT} commit -m "Automated commit from ki on ${COMMIT_TIMESTAMP}" >> ${LOG}
${GIT} push origin ${BRANCH} >> ${LOG}

if [[ ${UPDATE_FLAG} -eq 1 ]]
then
    ${BASH} /home/${USER}/Documents/Mehdi/carla_gym_RL/scripts/update/update.sh
fi

sudo systemctl stop auto_git.service
${SCREEN} -S ${AUTOGIT_SCREEN} -X quit