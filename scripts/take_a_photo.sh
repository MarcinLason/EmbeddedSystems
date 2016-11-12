#!/bin/bash

if [ $# -eq 1 ]
then
    PATH=$1
else
    PATH="."
DATE=$(date +"%Y-%m-%d_%H:%M:%S")
raspistill -o $PATH/$DATE.jpg
fi