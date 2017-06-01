#!/bin/bash

function split {
  d=$1
  shift
  echo $@ | sed 's/'$d'/\n/g'
}

function getIp {
  server=$1
  interface=$2
  addresses=`openstack server show $server -f value -c addresses`
  address=`split ';' $addresses | awk -F'=' '$1 ~ /'$interface'/{print $2}'`
  ipv4_adress=`split ',' $address | sed -n -r '/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/p'`
  awk '{if(NF > 2) print "Multiple address found ("$0"). Choosing "$1}' 1>&2 <<< $ipv4_adress
  ipv4_adress=`awk '{print $1}' <<< $ipv4_adress`
  echo $ipv4_adress
}

hss_mgmt=`getIp hss mgmt`
hss_data=$hss_mgmt/24
mme_mgmt=`getIp mme mgmt`
mme_data=$mme_mgmt/24
spgw_mgmt=`getIp spgw mgmt`
spgw_data=$spgw_mgmt/24
hss_host=hss
mme_host=mme
spgw_host=spgw

mme_access=`getIp mme private`
mme_access="$mme_access/24"
spgw_access=`getIp spgw private`
spgw_access="$spgw_access/24"

echo "HSS: $hss_host: $hss_mgmt ($hss_data)"
echo "MME: $mme_host: $mme_mgmt ($mme_data - $mme_access)"
echo "SPGW: $spgw_host: $spgw_mgmt ($spgw_data - $spgw_access)"

args="--hss_mgmt_ip $hss_mgmt --hss_s6a_ip $hss_data"
args+=" --mme_mgmt_ip $mme_mgmt --mme_s11_ip $mme_data"
args+=" --mme_s1_ip $mme_access"
args+=" --sgw_s1_ip $spgw_access --pgw_sgi_ip $spgw_data"

spec_args="--hss_host $hss_host --mme_host $mme_host --spgw_host $spgw_host"
spec_args+=" --spgw_mgmt_ip $spgw_mgmt --spgw_s11_ip $spgw_data"
son-vm-client $args $@ oai $spec_args

