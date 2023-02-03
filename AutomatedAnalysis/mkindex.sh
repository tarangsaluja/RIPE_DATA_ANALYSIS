#!/bin/bash

set -e

#generate index.html for the top-level dir

path=${1:-/nfs/lander/ripe_atlas_islands/output/}

exec >$path/../.index.html

#header

cat <<HEADER
<!DOCTYPE html>
<html>
  <head>
    <title>RIPE Atlas Islands and Peninsulas</title>
    <style>
      table, th, td {
        border: none;
      }
      td {
        padding-left: 2em;
        padding-right: 2em;
      }
    </style>
  </head>
  <body>
    <h1>RIPE Atlas Islands and Peninsulas</h1>
    <br>
    Every day <a href="https://ant.isi.edu">ANT project</a> analyzes the 
    <a href="https://atlas.ripe.net">RIPE Atlas</a> data and determines
    <i>islands</i> and <i>peninsulas</i> among RIPE Atlas anchors with respect to DNS Roots.
    Islands are probes that consistently cannot reach any of the 13 letters of the DNS Roots, and peninsulas
    are exhibiting partial connectivity and can reach some but not others.
    <br><br> 
    This information is generated at the end of the day (24 hour period, UTC) and provided 
    as-is in the hope of being useful to RIPE Atlas, DNS Root operators, as well as individual probe operators.
    <br><br>
    <table>
HEADER
for date in $(cd $path; ls -d ????-??-?? | sort -r); do
    cat <<ROWS 
    <tr>
      <td>$date</td>
      <td><a href='$date/IPV4_probe_UDPSOA_measurement/RIPE_ATLAS_PROBE_CLASSIFICATIONS/island.json'>v4/islands</a>
      <td><a href='$date/IPV4_probe_UDPSOA_measurement/RIPE_ATLAS_PROBE_CLASSIFICATIONS/peninsula.json'>v4/peninsulas</a>
      <td><a href='$date/IPV6_probe_UDPSOA_measurement/RIPE_ATLAS_PROBE_CLASSIFICATIONS/island.json'>v6/islands</a>
      <td><a href='$date/IPV6_probe_UDPSOA_measurement/RIPE_ATLAS_PROBE_CLASSIFICATIONS/peninsula.json'>v6/peninsulas</a>
    </tr>
ROWS
done

cat <<FOOTER
    </table>
  </body>
</html>
FOOTER

mv $path/../.index.html $path/index.html
