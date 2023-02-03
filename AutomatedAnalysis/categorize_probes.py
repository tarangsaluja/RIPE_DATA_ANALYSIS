#!/usr/bin/python

import sys
import pandas as pd
import json
import os


CATEGORIES = ['NL', 'RL', 'SLR', 'SLP', 'AL']


def cusum():
    return True

def categorize_data(percent_df, seq_df):
    
    #json_dict for categoreis
    json_dict = {}
    json_dict['bad_probe'] = []
    json_dict['investigate_persistent'] = []
    json_dict['investigate_random'] = []

    fail_summary = {}


    #initialize list of classifications/percents
    classification = []
    percentages = []


    #get appropriate lists
    probe_list = percent_df['probe'].tolist()
    root_list = percent_df['root'].tolist()
    root = root_list[0]

    #put probes in appropriate categories
    for probe in probe_list:
        percent = float(percent_df.loc[percent_df.probe == probe, 'percent'])
        if (percent == 0):
            classification.append('NL')
            percentages.append(percent)
        elif (percent <= 5):
            classification.append('RL')
            percentages.append(percent)
        elif (percent < 100):
            if cusum():
                classification.append('SLR')
                percentages.append(percent)
                json_dict['investigate_random'].append(int(probe))
            else:
                classification.append('SLP')
                percentages.append(percent)
                json_dict['investigate_persistent'].append(int(probe))
        else:
            classification.append('AL')
            percentages.append(percent)
            json_dict['bad_probe'].append(int(probe))


    classification_label = "Root " + root + " classification"
    percentage_label = "Root" + root + "percentage"
    classified_df = pd.DataFrame(list(zip(probe_list, classification, percentages)), columns = ['probe', classification_label, percentage_label])

    return_dict = {}
    return_dict[root] = json_dict

    fail_summary['bad probes'] = json_dict['bad_probe']
    fail_summary['total probes number'] = len(probe_list)
    fail_summary['bad probes number'] = len(json_dict['bad_probe'])

    bad_dict = {}
    bad_dict[root] = fail_summary

    return return_dict, classified_df, bad_dict


#read in dataframes
percent_df = pd.read_csv(sys.argv[1], sep='\t', header=None, names=['root', 'probe', 'count', 'error', 'percent'])
seq_df = pd.read_csv(sys.argv[2], sep='\t', header=None, names=['root', 'probe', 'sequence'])

#drop the first row
percent_df.drop(index=percent_df.index[0], axis=0, inplace=True)
seq_df.drop(index=seq_df.index[0], axis=0, inplace=True)

#get classifications for each probe
return_dict, classified_df, bad_dict = categorize_data(percent_df, seq_df)

#write df to csv
classified_df.to_csv(sys.argv[3], sep='\t', index=False, mode = 'a')

#append JSON to approrpriate file
with open(sys.argv[4], "a") as data:
    data.write(json.dumps(return_dict))
    data.close()

if os.path.exists(sys.argv[5]):
    with open(sys.argv[5], "r") as jsonFile:
            file_data = json.load(jsonFile)
else:
    file_data = {}

file_data.update(bad_dict)

with open(sys.argv[5], "w") as jsonFile:
        json.dump(file_data, jsonFile)


#with open(sys.argv[5], "a+") as data:
#    if os.stat(sys.argv[5]).st_size != 0:
#        file_data = json.loads(data)

#    else:
#        file_data = {}
#    file_data.update(bad_dict)
#    data.seek(0)
#    json.dump(file_data, data)



