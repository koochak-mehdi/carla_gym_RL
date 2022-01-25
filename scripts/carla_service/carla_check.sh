#!/bin/bash

# variables
carla_screen="carla_screen"
counter=0
DATELOG=`date +'%Y-%m-%d-%H-%M-%S'`
LOG="/home/${USER}/carla_auto_git_log/${DATELOG}_carla.log"

# commands
SCREEN=$(which screen)
PGREP=$(which pgrep)

# check if carla is running
carla_output=$(${PGREP} CarlaUE4)
readarray -t carla_PIDS <<< "$carla_output"

# check carla
if [[ ${#carla_PIDS[@]} -le 1 ]]
then
    if [[ ${#carla_PIDS[@]} -eq 1 ]]
    then
        if [ ! -n "${carla_PIDS[0]}" ]
        then
            echo "running carla ..." >> ${LOG}
            ${SCREEN} -dm $carla_screen
            ${SCREEN} -S $carla_screen -X stuff '/Carla/CARLA_0.9.12/CarlaUE4.sh -RenderOffScreen\n'

            sleep 10

            # check if carla is running
            carla_output=$(${PGREP} CarlaUE4)
            readarray -t carla_PIDS <<< "$carla_output"

            if [[ ${#carla_PIDS[@]} -le 1 ]]
            then
                echo 'rebooting ...' >> ${LOG}
                #bash -c 'sudo reboot 0'
            fi
        fi
    fi
else
    echo "carla already is running ..." >> ${LOG}
    break
fi