#!/bin/bash

set -e

START=${1:-$((($(date +%s)/(24*60*60)-1)*24*60*60))}
END=${2:-$((START+24*60*60-1))}
BIN=${3:-3600}

S=$(readlink -f $(dirname $0))
cd $S

KIND=IPV4_probe_UDPSOA_measurement
source paths.sh
LOG=$B/cronjob.log
exec >>$LOG 2>&1

ipv4_soa_island=$class_island_json
ipv4_soa_peninsula=$class_peninsula_json
./parse_script.sh $START $END $KIND.json $BIN udpsoa

KIND=IPV6_probe_UDPSOA_measurement
source paths.sh
ipv6_soa_island=$class_island_json
ipv6_soa_peninsula=$class_peninsula_json
./parse_script.sh $START $END IPV6_probe_UDPSOA_measurement.json $BIN udpsoa

#./parse_script.sh $START $END IPV4_anchor_UDPSOA_measurement.json $BIN  udpsoa "f"
#./parse_script.sh $START $END IPV6_anchor_UDPSOA_measurement.json $BIN udpsoa "f"
#./parse_to_table.sh $START $END IPV4_anchor_Ping_measurement.json $BIN ping "f"
#./parse_to_table.sh $START $END IPV4_probe_Ping_measurement.json $BIN ping "f"
#./parse_to_table.sh $START $END IPV6_anchor_Ping_measurement.json $BIN ping "f"
#./parse_to_table.sh $START $END IPV6_probe_Ping_measurement.json $BIN ping "f"

#bash parse_to_table.sh $START $END test.json $BIN udpsoa

./get_LAN_misconfig.py $ipv4_soa_island     $ipv6_soa_island    $soa_v4_misconfig_LAN $soa_v6_misconfig_LAN $both_misconfig_LAN
./get_ISP_misconfig.py $ipv4_soa_peninsula  $ipv6_soa_peninsula $soa_v4_misconfig_ISP $soa_v6_misconfig_ISP

./mkindex.sh

rm -rf $B/cache/*
