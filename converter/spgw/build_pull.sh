#!/bin/bash

function c_xargs() {
  args=$1
  shift
  echo -n $args | xargs -d',' -I'{}' $@
}

pushd $(dirname $0)
registry=$1
images=$2
c_xargs $images sudo docker image pull $registry/{}
c_xargs $images sudo docker image tag $registry/{} {}
c_xargs $images sudo systemctl enable docker-container@{}.service
popd
