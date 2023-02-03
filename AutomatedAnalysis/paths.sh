# $START, $KIND need to be set

B="/nfs/landervol13/ripe_atlas_islands"

date_start=$(date -u +%Y-%m-%d -d @$START)

ODIR="$B/output/$date_start/$KIND"
CDIR="$B/cache/$date_start/"
mkdir -p $ODIR $CDIR

class_aggr_csv="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/aggregate_classifications.csv"
class_class_json="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/classifications.json"
class_percent_csv="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/percentages.csv"
class_island_json="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/island.json"
class_peninsula_json="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/peninsula.json"
summary_json="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/summary.json"
class_penfreq_json="$ODIR/RIPE_ATLAS_PROBE_CLASSIFICATIONS/pen_frequency.json"

soa_v6_misconfig_LAN="$ODIR/soa_v6_misconfig_LAN.json"
soa_v4_misconfig_LAN="$ODIR/soa_v4_misconfig_LAN.json"
both_misconfig_LAN="$ODIR/both_misconfig_LAN.json"
soa_v6_misconfig_ISP="$ODIR/soa_v6_misconfig_ISP.json"
soa_v4_misconfig_ISP="$ODIR/soa_v4_misconfig_ISP.json"
