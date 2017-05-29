#!/bin/bash

registry=$1

sudo apt-get -y install apt-transport-https ca-certificates curl

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sudo apt-get update

sudo apt-get -y install docker-ce

[[ -z $registry ]] || sudo cat > /etc/docker/daemon.json << EOF
{
  "insecure-registries": ["$registry"]
}
EOF

