#!/bin/bash

#Steps taken by this script:
# 1) Create a temporary SSH key
# 2) Create a security group with rules that allow ingress SSH traffic
# 3) Create a VM instance with
#     a) image named $image_name
#     b) flavor names $flavor_name
#     c) network named $network_name
# 4) Add a floating if exists any not used one or create a new one
#    on the network named public
# 5) Create temporary SSH config that defines host "converter"
# 6) Install docker on "converter" through SSH and add docker service
#    Note: one must execute in "build.sh" (see step 8) the following:
#    "systemctl enable docker-container@image_name.service" where
#    image_name is the name of the image created by "build.sh"
# 7) Copy and targz out $build_package on "converter"
# 8) Run script "build.sh" from $build_package
# 9) Stop the VM and create a snapshot of it
# 10) Delete SSH config
# 11) Delete instance
# 12) Delete security group
# 13) Delete SSH key

#Environment variables to connect OpenStack 
#(usually setup by the devstack's openrc script: . ./devstack/openrc)
#OS_REGION_NAME=RegionOne
#OS_PROJECT_NAME=demo
#OS_IDENTITY_API_VERSION=2.0
#OS_PASSWORD=secret
#OS_AUTH_URL=http://localhost:5000/v2.0
#OS_USERNAME=demo
#OS_TENANT_NAME=demo
#OS_VOLUME_API_VERSION=2
#OS_NO_CACHE=1

function die() {
  echo $@
  exit 1
}

#These variables should be provided by the user
image_name="Ubuntu"
flavor_name="ds1G"
network_name="private"
build_package="build.tar.gz"
snapshot_name="Snapshot"
do_not_install_docker=0
while getopts ":i:f:n:b:s:dh" args; do
  case $args in
    i)
      image_name=$OPTARG
      ;;
    f)
      flavor_name=$OPTARG
      ;;
    n)
      network_name=$OPTARG
      ;;
    b)
      build_package=$OPTARG
      ;;
    s)
      snapshot_name=$OPTARG
      ;;
    d)
      do_not_install_docker=1
      ;;
    h)
      echo "Converter.sh -- Create OpenStack snapshot based on a build package"
      echo -e "\t-i name\t\tOpenStack base image (default: Ubuntu)"
      echo -e "\t-f name\t\tOpenStack flavor name (default: ds1G)"
      echo -e "\t-n name\t\tOpenStack network name (default: private)"
      echo -e "\t-b package\tBuild package (default: build.tar.gz)"
      echo -e "\t-s name\t\tSnapshot name (default: Snapshot)"
      echo -e "\t-d\t\tDisable docker installation"
      exit 0
      ;;
  esac
done
[[ -f $build_package ]] || die "Build script \"$build_package\" does not exist"

echo "Using build package $build_package"
echo "Using flavor $flavor_name, image $image_name, network $network_name"
echo "Snapshot will be saved with name $snapshot_name"
[[ $(openstack image show $snapshot_name 2>/dev/null) ]] && die "Image with name $snapshot_name already exists. Please specify a unique snapshot name"

ssh_config=""
key_name=""
private_key=""
secgroup_name=""
instance_name=""
floating_ip=""
image_id=`openstack image show $image_name -f value -c id 2>/dev/null`
flavor_id=`openstack flavor show $flavor_name -f value -c id 2>/dev/null`
network_id=`openstack network show $network_name -f value -c id 2>/dev/null`
[[ -n $flavor_id ]] || die "No flavor ID is found for name $flavor_name"
[[ -n $image_id ]] || die "No image ID is found for name $image_name"
[[ -n $network_id ]] || die "No network ID is found for name $network_name"

function getUniqueName() {
  local prefix=$1
  shift
  local cmd=$@

  local name_exists=0
  while [[ $name_exists == 0 ]]; do
    local random_name="${prefix}_$RANDOM"
    $cmd | grep -q $random_name
    name_exists=$?
  done
  echo $random_name
}

function createKey() {
  echo "Looking for available name for the key"
  key_name=`getUniqueName ConverterKey_ openstack keypair list -f value -c Name`
  echo "Choosen name: $key_name"

  private_key=`tempfile`
  echo "Creating key and saving private key in $private_key"
  openstack keypair create $key_name > $private_key
  echo "Key created with Name: $key_name"
}

function deleteKey() {
  echo "Deleting key $key_name and private key $private_key"
  openstack keypair delete $key_name
  rm $private_key
}

function getUniqueName() {
  local prefix=$1
  shift
  local cmd=$@

  local name_exists=0
  while [[ $name_exists == 0 ]]; do
    local random_name="${prefix}_$RANDOM"
    $cmd | grep -q $random_name
    name_exists=$?
  done
  echo $random_name
}

function createSecGroup() {
  echo "Looking for available name for the security gorup"
  secgroup_name=`getUniqueName ConverterSecGroup_ openstack security group list -f value -c Name`
  echo "Choosen name: $secgroup_name"

  echo "Creating security group"
  openstack security group create $secgroup_name
  echo "Adding ingress IPv4 rule"
  openstack security group rule create --ethertype IPv4 --ingress --remote-ip 0.0.0.0/0 $secgroup_name
  echo "Adding ingress IPv6 rule"
  openstack security group rule create --ethertype IPv6 --ingress --remote-ip ::/0 $secgroup_name
}

function deleteSecGroup() {
  echo "Deleting security group $secgroup_name"
  openstack security group delete $secgroup_name
}

function createInstance() {
  echo "Looking for available name for the instance"
  instance_name=`getUniqueName ConverterInstance_ openstack server list -f value -c Name`
  echo "Choosen name: $instance_name"

  echo "Creating instance"
  openstack server create --flavor $flavor_id --image $image_id --key-name $key_name --security-group $secgroup_name --network $network_id $instance_name
}

function deleteInstance() {
  echo "Deleting converter instance $instance_name"
  openstack server delete $instance_name
}

function waitUntilActive() {
  echo -n "Waiting until instance ($instance_name) is active"
  local instance_status=`openstack server show $instance_name -f value -c status`
  while [[ $instance_status != "ACTIVE" ]]; do
    echo -n "."
    sleep 1
    instance_status=`openstack server show $instance_name -f value -c status`
  done
  echo "OK"
}

function waitUntilSshAlive() {
  echo -n "Waiting until instance's ssh comes up"
  nc -z $floating_ip 22
  local isSshPortOpen=$?
  while [[ $isSshPortOpen != 0 ]]; do
    echo -n "."
    sleep 1
    nc -z $floating_ip 22
    isSshPortOpen=$?
  done
  echo "OK"
}

function addFloatingIP() {
  echo "Looking for available floating IP"
  floating_ip=`openstack floating ip list -f value -c Port -c "Floating IP Address" | awk '$2=="None"{print $1; exit}'`
  if [[ -n $floating_ip ]]; then
    echo "Found: $floating_ip"
  else
    echo "Not found, creating one"
    floating_ip=`openstack floating ip create public -f value -c floating_ip_address`
    echo "Created $floating_ip"
  fi

  echo "Adding floating IP $floating_ip_address"
  local instance_id=`openstack server show $instance_name -f value -c id`
  openstack server add floating ip $instance_id $floating_ip
}

function createSshConfig() {
  ssh_config=`tempfile`
  cat << EOF > $ssh_config
  Host converter
    Hostname $floating_ip
    User ubuntu
    IdentityFile $private_key
    StrictHostKeyChecking no
EOF
}

function deleteSshConfig() {
  rm $ssh_config
}

function c_ssh() {
  ssh -q -F $ssh_config $@
}

function c_scp() {
  scp -q -F $ssh_config $@
}

function installDocker() {
  c_scp install_docker.sh converter:install_docker.sh
  c_ssh converter ./install_docker.sh
  c_scp docker-container@.service converter:/tmp/docker-container@.service
  c_ssh converter sudo mv /tmp/docker-container@.service /etc/systemd/system/docker-container@.service
}

function buildImages() {
  c_ssh converter mkdir build_dir
  c_scp $build_package converter:$build_package
  c_ssh converter tar -C build_dir -xzf $build_package
  c_ssh converter bash ./build_dir/build.sh
}

function stopInstance() {
  echo "Stopping instance $instance_name"
  openstack server stop $instance_name
  echo -n "Waiting until instance ($instance_name) is shutoff"
  local instance_status=`openstack server show $instance_name -f value -c status`
  while [[ $instance_status != "SHUTOFF" ]]; do
    echo -n "."
    sleep 1
    instance_status=`openstack server show $instance_name -f value -c status`
  done
  echo "OK"
}

function createSnapshot() {
  echo "Creating snapshot from $instance_name"
  openstack server image create $instance_name --name $snapshot_name
  echo -n "Waiting until snapshot ($snapshot_name) is ready"
  local image_status=`openstack image show $snapshot_name -f value -c status`
  while [[ $image_status != "active" ]]; do
    echo -n "."
    sleep 1
    image_status=`openstack image show $snapshot_name -f value -c status`
  done
  echo "OK"
}

createKey
createSecGroup
createInstance
waitUntilActive
addFloatingIP
waitUntilSshAlive
createSshConfig

[[ $do_not_install_docker == 1 ]] || installDocker
buildImages

stopInstance
createSnapshot

deleteSshConfig
deleteInstance
deleteSecGroup
deleteKey

