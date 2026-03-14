#!/bin/bash

sudo apt update -y
sudo apt install python3-pip -y

pip3 install flask

mkdir /app
cd /app

echo "Starting app"
python3 app.py