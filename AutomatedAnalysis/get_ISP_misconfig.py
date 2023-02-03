#!/usr/bin/python

import json
import sys

with open(sys.argv[1], 'r') as j:
    v4_peninsula_dict = json.loads(j.read())

with open(sys.argv[2], 'r') as j:
    v6_peninsula_dict = json.loads(j.read())


v6_peninsulas = v6_peninsula_dict['Peninsula']
v4_peninsulas = v4_peninsula_dict['Peninsula']

v4_ISP_misconfig = [probe for probe in v4_peninsulas]
v6_ISP_misconfig = [probe for probe in v6_peninsulas]

v4_ISP_misconfig_dict = {}
v4_ISP_misconfig_dict['ISPLevelMisconfiguration'] = v4_ISP_misconfig
v4_ISP_misconfig_dict['ISPLevelMisconfigurationCount'] = len(v4_ISP_misconfig)

v6_ISP_misconfig_dict = {}
v6_ISP_misconfig_dict['ISPLevelMisconfiguration'] = v6_ISP_misconfig
v6_ISP_misconfig_dict['ISPLevelMisconfigurationCount'] = len(v6_ISP_misconfig)

with open(sys.argv[3], "w") as outfile:
    json.dump(v4_ISP_misconfig_dict, outfile)

with open(sys.argv[4], "w") as outfile:
    json.dump(v6_ISP_misconfig_dict, outfile)

