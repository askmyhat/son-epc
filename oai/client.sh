function getIp {
  sudo docker inspect $1 | jq '.[0].NetworkSettings.Networks | map(.IPAddress)[0]' | sed 's/"//g'
}

function getHost {
  sudo docker inspect $1 | jq '.[0].Config.Hostname' | sed 's/"//g'
}

hss_mgmt=`getIp hss`
hss_data=$hss_mgmt/24
mme_mgmt=`getIp mme`
mme_data=$mme_mgmt/24
spgw_mgmt=`getIp spgw`
spgw_data=$spgw_mgmt/24
hss_host=`getHost hss`
mme_host=`getHost mme`
spgw_host=`getHost spgw`

echo "HSS: $hss_host: $hss_mgmt ($hss_data)"
echo "MME: $mme_host: $mme_mgmt ($mme_data)"
echo "SPGW: $spgw_host: $spgw_mgmt ($spgw_data)"

args="--hss_mgmt_ip $hss_mgmt --hss_s6a_ip $hss_data"
args+=" --mme_mgmt_ip $mme_mgmt --mme_s11_ip $mme_data"
args+=" --mme_s1_ip $mme_data"
args+=" --sgw_s1_ip $spgw_data --pgw_sgi_ip $spgw_data"

spec_args="--hss_host $hss_host --mme_host $mme_host --spgw_host $spgw_host"
spec_args+=" --spgw_mgmt_ip $spgw_mgmt --spgw_s11_ip $spgw_data"
son-vm-client $args $@ oai $spec_args
