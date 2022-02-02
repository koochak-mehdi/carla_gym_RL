#!/bin/bash

PS=$(which ps)
GREP=$(which grep)
AWK=$(which awk)
SCREEN=$(which screen)

# check if script is running
script_output=$(${PS} -aux | ${GREP} '[f]irst_try_ddpg' | ${AWK} '{print $2}')

LOGS=/home/omen_ki_rechner/Documents/Mehdi/carla_gym_RL/logs/simulations
VAR=/home/omen_ki_rechner/Documents/Mehdi/carla_gym_RL/vars/watchdog_var
P_WATCHDOG_VAR=$(cat ${VAR})
SCRIPT_SCREEN="script_screen"


if [[ ${#script_output[@]} -eq 1 ]]
then
    if [[ ! -z ${script_output[0]} ]]
    then
        my_list=$( ls ${LOGS} )
        echo ${#my_list[@]} > ${VAR}
        if [[ ${P_WATCHDOG_VAR} -eq ${#my_list[@]} ]]
        then
            sleep 1
            my_list=$( ls ${LOGS} )
            if [[ ${P_WATCHDOG_VAR} -eq ${#my_list[@]} ]]
            then
                sudo systemctl stop script_check.service
                ${SCREEN} -S ${SCRIPT_SCREEN} -X quit
            fi
        fi
    fi
fi