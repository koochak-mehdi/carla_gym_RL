#!/bin/bash

ls -la > /home/mehdi/Documents/Mehdi/carla_gym_RL/vars/test_var

FLAG=$(cat /home/mehdi/Documents/Mehdi/carla_gym_RL/vars/test_var | grep mehdi)

if [[ ! -z "${FLAG}" ]] # if is empty
then
    echo "salam${FLAG}-"
else
    echo "bye${FLAG}-"
fi