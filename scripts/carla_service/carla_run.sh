LOG=$(cat /home/mehdi/Documents/Mehdi/carla_gym_RL/vars/varlog_carla)
CARLA_SCREEN="carla_screen"
SCREEN=$(which screen)

/Carla/CARLA_0.9.12/CarlaUE4.sh -RenderOffScreen
sudo systemctl stop carla_check.service
${SCREEN} -S ${CARLA_SCREEN} -X quit