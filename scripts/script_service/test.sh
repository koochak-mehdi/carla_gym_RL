#!/bin/bash

DATELOG=`date +'%Y-%m-%d-%H-%M-%S'`
LOG="/home/${USER}/carla_auto_git_log/${DATELOG}_test.log"


echo "The date is task1: $(date)" >> ${LOG}