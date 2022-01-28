#!/bin/bash

# variables
mode=$1
script_screen="script_screen"
root_script="/home/omen_ki_rechner/Documents/Mehdi/carla_gym_RL"
DATELOG=`date +'%Y-%m-%d-%H-%M-%S'`
LOG="/home/${USER}/Documents/Mehdi/carla_gym_RL/logs/${DATELOG}_script.log"


# commands
GIT=$(which git)
SCREEN=$(which screen)
PS=$(which ps)
GREP=$(which grep)
AWK=$(which awk)
ECHO=$(which echo)

echo "The date is task1: $(date)" >> ${LOG}

# check if script is running
script_output=$(${PS} -aux | ${GREP} '[f]irst_try_ddpg' | ${AWK} '{print $2}')
readarray -t script_PIDS <<< "$output"

if [[ $mode -eq 1 ]]
then
    echo "mode check"

    # check script
    if [[ ${#script_PIDS[@]} -ge 1 ]]
    then
        if [[ ${#script_PIDS[@]} -eq 1 ]]
        then

            if [ ! -n "${script_PIDS[0]}" ]
            then
                ${ECHO} "killing screen seesion ..." >> ${LOG}
                ${SCREEN} -S $script_screen -X quit

                ${ECHO} "running script ..." >> ${LOG}
                ${SCREEN} -dm $script_screen
                ${SCREEN} -S $script_screen -X stuff $'conda activate carla_env\n'
                ${SCREEN} -S $script_screen -X stuff $"python $root_script/first_try_ddpg.py\n"
            fi
        fi
    else
        ${ECHO} "script is already running ..." >> ${LOG}
    fi

else
    ${ECHO} "mode stop and git" >> ${LOG}

    # kill script screen
    ${SCREEN} -S $script_screen -X quit

    # do git thigs
    REPO='/Carla/CARLA_0.9.12/PythonAPI/my_scripts/carla_gym_RL'
    COMMIT_TIMESTAMP=`date +'%Y-%m-%d %H:%M:%S'`

    cd ${REPO}
    ${GIT} add --all . >> ${LOG}
    ${GIT} commit -m "Automated commit on ${COMMIT_TIMESTAMP}" >> ${LOG}
    ${GIT} push origin feature_automated_simulation >> ${LOG}
fi