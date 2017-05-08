#!/bin/bash

pushd $(dirname $0)
git clone https://github.com/elekjani/son-epc.git
cd son-epc/oai
sudo docker build -f Dockerfile.base -t oai_base .
sudo docker build -f Dockerfile.hss -t oai_hss .
sudo systemctl enable docker-container@oai_hss.service
popd
