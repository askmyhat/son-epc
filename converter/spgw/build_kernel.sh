#!/bin/bash

sudo apt-get -y install linux-headers-4.8.0-53 linux-image-4.8.0-53-generic linux-image-extra-4.8.0-53-generic
sudo sed -i 's/\(ExecStart.*\)%i/\1-v \/lib\/modules:\/lib\/modules %i/' /etc/systemd/system/docker-container@.service
