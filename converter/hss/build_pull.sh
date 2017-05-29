#!/bin/bash

function c_xargs() {
  args=$1
  shift
  xargs -d',' -I'{}' $@
}

pushd $(dirname $0)
registry=$1
images=$2
c_xargs $images docker pull $registry/{}
c_xargs $images docker tag $registry/{} {}
c_xargs $images sudo systemctl enable docker-container@{}.service
popd
