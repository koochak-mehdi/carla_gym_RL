LOG=$(cat /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/carla_log)
CARLA_SCREEN="carla_screen"
SCREEN=$(which screen)
REBOOT=$(which reboot)

/Carla/CARLA_0.9.12/CarlaUE4.sh -RenderOffScreen > /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/carla_run_var

FLAG=$(cat /home/${USER}/Documents/Mehdi/carla_gym_RL/vars/carla_run_var | grep Segmentation)

if [[ ! -z "${FLAG}" ]] # if is empty
then
    sudo ${REBOOT} 0
fi

sudo systemctl stop carla_check.service
${SCREEN} -S ${CARLA_SCREEN} -X quit