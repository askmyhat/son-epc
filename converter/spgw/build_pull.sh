#!/bin/bash

function c_xargs() {
  args=$1
  shift
  echo -n $args | xargs -d',' -I'{}' $@
}

sudo apt-get -y install linux-headers-4.8.0-53 linux-image-4.8.0-53-generic linux-image-extra-4.8.0-53-generic

pushd $(dirname $0)
registry=$1
images=$2
c_xargs $images sudo docker image pull $registry/{}
c_xargs $images sudo docker image tag $registry/{} {}
c_xargs $images sudo systemctl enable docker-container@{}.service
popd
