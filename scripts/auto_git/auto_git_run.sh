#!/bin/bash

REPO='/home/mehdi/Documents/Mehdi/carla_gym_RL'
COMMIT_TIMESTAMP=`date +'%Y-%m-%d %H:%M:%S'`
GIT=$(which git)
LOG=$(cat /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/autogit_log)
AUTOGIT_SCREEN="autogit_screen"
UPDATE_FLAG=$(cat /home/mehdi/Documents/Mehdi/carla_gym_RL/vars/update_flag)

cd ${REPO}
${GIT} add --all . >> ${LOG}
${GIT} commit -m "Automated commit on ${COMMIT_TIMESTAMP}" >> ${LOG}
${GIT} push origin test_learing >> ${LOG}

if[[ ${UPDATE_FLAG} -eq 1 ]]
then
    /home/mehdi/Documents/Mehdi/carla_gym_RL/scripts/update/update.sh
fi

sudo systemctl stop auto_git.service
${SCREEN} -S ${AUTOGIT_SCREEN} -X quit