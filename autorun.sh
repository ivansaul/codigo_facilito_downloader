#!/bin/bash

# update
sudo apt update -y

# Install firefox driver
sudo apt install firefox firefox-geckodriver -y

# Install ffmpeg
sudo apt install ffmpeg -y

# Install yt-dlp
pip install -U yt-dlp

# Install aria2
sudo apt install aria2 -y

# Install python requirements
pip install -r requirements.txt

# Run script
python facilito.py
#python downloader.py