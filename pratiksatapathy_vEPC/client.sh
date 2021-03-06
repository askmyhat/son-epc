function getIp {
  inspect=`sudo docker inspect $1`
  echo $inspect | jq '.[0].NetworkSettings.Networks | map(.IPAddress)[0]' | sed 's/"//g'
}

hss_mgmt=`getIp hss_pp`
hss_data=$hss_mgmt
mme_mgmt=`getIp mme_pp`
mme_data=$mme_mgmt
pgw_mgmt=`getIp pgw_pp`
pgw_data=$pgw_mgmt
sgw_mgmt_1=`getIp sgw_pp_1`
sgw_mgmt_2=`getIp sgw_pp_2`
sgw_data_1=$sgw_mgmt_1
sgw_data_2=$sgw_mgmt_2
hss_host=`sudo docker inspect hss_pp | jq '.[0].Config.Hostname' | sed 's/"//g'`
mme_host=`sudo docker inspect mme_pp | jq '.[0].Config.Hostname' | sed 's/"//g'`
pgw_host=`sudo docker inspect pgw_pp | jq '.[0].Config.Hostname' | sed 's/"//g'`
sgw_host_1=`sudo docker inspect sgw_pp_1 | jq '.[0].Config.Hostname' | sed 's/"//g'`
sgw_host_2=`sudo docker inspect sgw_pp_2 | jq '.[0].Config.Hostname' | sed 's/"//g'`
ds_ip=$hss_data
local_ip=`sudo docker inspect hss_pp | jq '.[0].NetworkSettings.Networks | map(.Gateway)[0]' | sed 's/"//g'`
lb_ip=`getIp lb_pp`
sink_ip=`getIp sink_pp`
ransim_1=`getIp ransim_pp_1`
ransim_2=`getIp ransim_pp_2`

echo "HSS: $hss_host: $hss_mgmt ($hss_data)"
echo "MME: $mme_host: $mme_mgmt ($mme_data)"
echo "SGW_1: $sgw_host_1: $sgw_mgmt_1 ($sgw_data_1)"
echo "SGW_2: $sgw_host_2: $sgw_mgmt_2 ($sgw_data_2)"
echo "PGW: $pgw_host: $pgw_mgmt ($pgw_data)"
echo "local_ip: $local_ip"
echo "lb_ip: $lb_ip"
echo "sink_ip: $sink_ip"
echo "ransim_1: $ransim_1"
echo "ransim_2: $ransim_2"

args="--hss_mgmt_ip $hss_mgmt --hss_s6a_ip $hss_data"
args+=" --mme_mgmt_ip $mme_mgmt --mme_s11_ip $mme_data"
args+=" --mme_s1_ip $mme_data"
args+=" --sgw_s1_ip $sgw_data_1,$sgw_data_2 --pgw_sgi_ip $pgw_data"

spec_args="--sgw_mgmt_ip $sgw_mgmt_1,$sgw_mgmt_2"
spec_args+=" --sgw_s11_ip $sgw_data_1,$sgw_data_2"
spec_args+=" --pgw_mgmt_ip $pgw_mgmt"
spec_args+=" --sgw_s5_ip $sgw_data_1,$sgw_data_2 --pgw_s5_ip $pgw_data"
spec_args+=" --sink_ip $sink_ip"
spec_args+=" --ds_ip $ds_ip --trafmon_ip $local_ip"
spec_args+=" --lb_s1_ip $lb_ip  --lb_s11_ip $lb_ip  --lb_s5_ip $lb_ip"
spec_args+=" --lb_mgmt_ip $lb_ip"
son-vm-client $args $@ pp $spec_args
