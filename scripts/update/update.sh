#!/bin/bash

LOG=$(cat /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/autogit_log)

echo "####################### from update #############################" >> ${LOG}
sudo reboot 
sudo reboot 0
echo 0 > /home/mehdi/Documents/Mehdi/carla_gym_RL/vars/update_flag