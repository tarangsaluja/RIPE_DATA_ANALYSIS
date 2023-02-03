#!/bin/bash

set -e

START=$1
STOP=$2
JSON_FILE=$3
BIN=$4
TYPE=$5 #what kind of measurement this is


KIND=${JSON_FILE%.json}

source paths.sh



#Find Duration of window we are interested in 
DURATION=$(($STOP - $START))


#Figure out the window of data which has to be downloaded since it is in 4 hour chunks
STARTNUM=$(($START / 14400))
BEGIN=$(($STARTNUM * 14400))
STOPNUM=$(($(($STOP / 14400))+1))
END=$(($STOPNUM * 14400))


#create array to keep track of files names
declare -a data_names=()

#create array to keep track of root
declare -a roots=()

#create array of root servers
declare -a root_servers=("A" "B" "C" "D" "E" "F" "G" "H" "I" "J" "K" "L" "M")

#create dictionary which keeps track of associations between ids and probes
declare -A assoc=$(
  jq -r '"(",(to_entries | .[] | "["+(.key|@sh)+"]="+(.value|@sh)),")"' \
          $JSON_FILE
)



#Each iteration of file downloading if needed
WINDOWSTART=$BEGIN
WINDOWEND=$(($BEGIN + 14399))
RIPE_API="https://atlas.ripe.net/api/v2/measurements"
#Download all the data
while (($WINDOWEND < $END)); do
	#Create folder for day if it does not yet exist
	DAY=$(($WINDOWSTART/86400))
        DAY_TIME=$(($DAY*86400))

	#convert Unix timestamp to datetime for filenaming
	FILE_WINDOWSTART=$(date -u +%Y%m%dt%H%M -d @${WINDOWSTART})

	#Download chunks of data and save the filenames where the data is stored
	for i in ${!assoc[@]}; do
	        ofile="$CDIR/$FILE_WINDOWSTART.14400.${assoc[$i]}.${TYPE}.json"
		data_names+=($ofile)
		roots+=($i)
       		if ! [ -f "$ofile" ]; then
                	url="$RIPE_API/${assoc[$i]}/results/?start=$WINDOWSTART&stop=$WINDOWEND&format=txt"
                	wget -t 30 -c "$url" -O $ofile -a $CDIR/wget.log || exit 1 
       		fi
	done
	WINDOWSTART=$(($WINDOWSTART + 14400))
	WINDOWEND=$(($WINDOWSTART + 14399))
done

mkdir -p "$ODIR/RIPE_ATLAS_DATA"
mkdir -p "$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS"
mkdir -p "$ODIR/RIPE_ATLAS_GROUND_TRUTH"

echo "file root" > info.txt
#Save the files with the needed data into textfiles
file_len=${#roots[@]}
for n in $(seq 0 $file_len); do
   echo ${data_names[$n]} >> "$ODIR/RIPE_ATLAS_DATA/${roots[$n]}.txt"
   echo "-------"
   cat "$ODIR/RIPE_ATLAS_DATA/${roots[$n]}.txt"
   echo "-------"
done 


class_rdata_json="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/${DURATION}.${BIN}.${TYPE}.root_data.json"
class_badprobes_json="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/${DURATION}.${BIN}.${TYPE}.bad_probe_by_root.json"
key_len=${#assoc[@]}
for i in ${!assoc[@]}; do
	percent_csv="$ODIR/RIPE_ATLAS_DATA/${i}.${assoc[$i]}.${DURATION}.${BIN}.${TYPE}.percent.csv"
	lengths_csv="$ODIR/RIPE_ATLAS_DATA/${i}.${assoc[$i]}.${DURATION}.${BIN}.${TYPE}.length.csv"
	sequence_csv="$ODIR/RIPE_ATLAS_DATA/${i}.${assoc[$i]}.${DURATION}.${BIN}.${TYPE}.sequence.csv"
        txtfile="$ODIR/RIPE_ATLAS_DATA/${i}.txt"
	class_pcent_csv="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/${i}.${assoc[$i]}.${DURATION}.${BIN}.${TYPE}.classifications_percentages.csv"
	touch $class_rdata_json

	[ -f $percent_csv ] ||
		./parse_data.py $START $STOP $i $BIN $TYPE $percent_csv $lengths_csv $sequence_csv  $txtfile

	[ -f $class_pcent_csv ] ||
		./categorize_probes.py $percent_csv $sequence_csv $class_pcent_csv $class_rdata_json $class_badprobes_json
done


[ -f $class_aggr_csv ] ||
	./aggregate_root_classifications.py "$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS" \
                $class_aggr_csv $class_class_json $class_rdata_json $class_percent_csv \
                $class_island_json $class_peninsula_json $class_badprobes_json $summary_json $class_penfreq_json

gt_orgstats_json="$ODIR/RIPE_ATLAS_GROUND_TRUTH/${DURATION}.${BIN}.${TYPE}.org_statistics.json"
gt_finstats_json="$ODIR/RIPE_ATLAS_GROUND_TRUTH/${DURATION}.${BIN}.${TYPE}.fin_statistics.json"
gt_noislestats_json="$ODIR/RIPE_ATLAS_GROUND_TRUTH/${DURATION}.${BIN}.${TYPE}.noIsland_statistics.json"

for i in ${!assoc[@]}; do
        txtfile="$ODIR/RIPE_ATLAS_DATA/${i}.txt"
	gt_percent_csv="$ODIR/RIPE_ATLAS_GROUND_TRUTH/${i}.${assoc[$i]}.${DURATION}.${BIN}.${TYPE}.percent_by_type.csv"
        #xxx why do we run this in a loop if we're going to run it once?
	[ -f $gt_orgstats_json ] ||
		./recalculate_DNSMON.py $START $STOP $i $BIN $TYPE $txtfile $class_island_json $class_badprobes_json \
                        $gt_percent_csv $gt_orgstats_json $gt_finstats_json $gt_noislestats_json
	rm $txtfile
done 
