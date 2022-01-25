#!/bin/bash

# variables
mode=$1
script_screen="script_screen"
root_script="/Carla/CARLA_0.9.12/PythonAPI/my_scripts/carla_gym_RL/"

# check if script is running
script_output=$(ps -aux | grep '[f]irst_try_ddpg' | awk '{print $2}')
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
                echo "killing screen seesion ..."
                screen -S $script_screen -X quit

                echo "running script ..."
                screen -dm $script_screen
                screen -S $script_screen -X stuff $'conda activate carla_env\n'
                screen -S $script_screen -X stuff $"python $root_script/first_try_ddpg.py\n"
            fi
        fi
    else
        echo "script is already running ..."
    fi

else
    echo "mode stop and git"

    # kill script screen
    screen -S $script_screen -X quit

    # do git thigs
    # TODO
fi