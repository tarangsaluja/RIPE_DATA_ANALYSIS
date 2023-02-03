#!/usr/bin/python

import json
import sys

with open(sys.argv[1], 'r') as j:
    v4_dict = json.loads(j.read())

with open(sys.argv[2], 'r') as j:
    v6_dict = json.loads(j.read())

#v4_dict = json.loads(sys.argv[1])
#v6_dict = json.loads(sys.argv[2])

v4_islands = v4_dict['Islands']
v6_islands = v6_dict['Islands']


v6_misconfig = [island for island in v6_islands]
v4_misconfig = [island for island in v4_islands]
both_misconfig = [island for island in v6_islands if island in v4_islands]

v6_misconfig_dict = {}
v6_misconfig_dict['LAN Level Misconfiguration'] = v6_misconfig
v6_misconfig_dict['LAN Level Misconfiguration Count'] = len(v6_misconfig)

v4_misconfig_dict= {}
v4_misconfig_dict['LAN Level Misconfiguration'] = v4_misconfig
v4_misconfig_dict['LAN Level Misconfiguration Count'] = len(v4_misconfig)

both_misconfig_dict = {}
both_misconfig_dict['LAN Level Misconfiguration'] = both_misconfig
both_misconfig_dict['LAN Level Misconfiguration Count'] = len(both_misconfig)


with open(sys.argv[3], "w") as outfile:
    json.dump(v4_misconfig_dict, outfile)

with open(sys.argv[4], "w") as outfile:
    json.dump(v6_misconfig_dict, outfile)

with open(sys.argv[5], "w") as outfile:
    json.dump(both_misconfig_dict, outfile)


