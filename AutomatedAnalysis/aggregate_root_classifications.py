#!/usr/bin/python

import os
import sys
import pandas as pd
import json

def get_new_col(aggregate_df, cols, rows):

    #create dct to convert
    tags = {}
    tags['Tags'] = []

    #create other dict to dump into json
    json_dict = {}
    json_dict['Island'] = []
    json_dict['Peninsula'] = []
    json_dict['PeninsulaFailure'] = []
    json_dict['WeakIsland'] = []
    json_dict['WeakPeninsula'] = []
    json_dict['Investigate'] = []

    
    #iterate through rows
    #for each row 
    for i in range(rows):
        count_AL = 0
        count_NL = 0
        count_SLR = 0
        count_SLP = 0

        tot_val = 0
        fail_for = ""

        #go through columns to figure out classification
        for j in range(cols):

            if aggregate_df.iloc[i, j] == 'AL':
                count_AL += 1
                tot_val += 1
                root = str(aggregate_df.columns[j])[5]
                root = root.lower()
                fail_for += root
                

            elif aggregate_df.iloc[i,j] == 'NL':
                count_NL += 1
                tot_val += 1
                root = str(aggregate_df.columns[j])[5]
                fail_for += root

            elif aggregate_df.iloc[i,j] == 'SLR':
                count_SLR += 1
                tot_val += 1
                root = str(aggregate_df.columns[j])[5]
                fail_for += root

            elif aggregate_df.iloc[i, j] == 'SLP':
                count_SLP += 1
                tot_val += 1
                root = str(aggregate_df.columns[j])[5]
                fail_for += root

            elif aggregate_df.iloc[i, j] == 'RL':
                tot_val += 1
                root = str(aggregate_df.columns[j])[5]
                fail_for += root

        tag_list = []

        if count_AL == tot_val:
            tag_list.append('Island')
            json_dict['Island'].append(int(aggregate_df.index[i]))

        if count_AL != tot_val and count_AL + count_SLR + count_SLP == tot_val:
            tag_list.append('WeakIsland')
            json_dict['WeakIsland'].append(int(aggregate_df.index[i]))

        if count_AL > 0 and count_AL != tot_val:
            tag_list.append('Peninsula')
            json_dict['Peninsula'].append(int(aggregate_df.index[i]))
            json_dict['PeninsulaFailure'].append(fail_for)

        if count_AL == 0 and count_SLR + count_SLP > 0 and count_SLR + count_SLP < tot_val:
            tag_list.append('WeakPeninsula')
            json_dict['WeakPeninsula'].append(int(aggregate_df.index[i]))

        if count_SLR + count_SLP > 0:
            tag_list.append('RoutingIssue')
            json_dict['Investigate'].append(int(aggregate_df.index[i]))

        tags['Tags'].append(tag_list)

    df = pd.DataFrame(tags, aggregate_df.index)

    return df, json_dict





#Get address of directory and create dataframe
dir_addr = sys.argv[1]
classification_aggregate_df = pd.DataFrame()
percentage_aggregate_df = pd.DataFrame()


#vertical concat all of the dataframes
for filename in os.listdir(dir_addr):
    total_path = dir_addr + "/" + filename

    if total_path != sys.argv[4] and total_path != sys.argv[8]:
        df = pd.read_csv(total_path, sep='\t')
        df = df.set_index('probe')
        classification_df = df.iloc[: , :1]
        percentage_df = df.iloc[: , -1:]
        classification_aggregate_df = pd.concat([classification_aggregate_df, classification_df], axis=1)
        percentage_aggregate_df = pd.concat([percentage_aggregate_df, percentage_df], axis=1)




#sort the dataframe
classification_aggregate_df = classification_aggregate_df.reindex(sorted(classification_aggregate_df.columns), axis=1)

#figure out dimensions of 
rows = classification_aggregate_df.shape[0]
cols = classification_aggregate_df.shape[1]

df, json_dict  = get_new_col(classification_aggregate_df, cols, rows)

classification_aggregate_df = pd.concat([classification_aggregate_df, df], axis=1)


classification_aggregate_df.to_csv(sys.argv[2], sep='\t', mode = 'a')
percentage_aggregate_df.to_csv(sys.argv[5], sep = '\t', mode ='a')

island_list = json_dict['Island']
island_dict = {}
island_dict['Islands'] = island_list

peninsula_list = json_dict['Peninsula']
peninsula_failure_list = json_dict['PeninsulaFailure']
peninsula_dict = {}
peninsula_dict['Peninsula']= peninsula_list
peninsula_dict['PeninsulaFailureList'] = peninsula_failure_list

#Peninsula Repeat Offenders
freq_dict = {"A": 0, "B":0, "C":0, "D":0, "E":0, "F":0, "G":0, "H":0, "I":0, "J":0, "K":0, "L":0, "M":0}
for pen_str in peninsula_failure_list:
    for char in pen_str:
        freq_dict[char] += 1

#Summary Statistics
summary_stat = {}
summary_stat['TotalProbes'] = [rows]
summary_stat['TotalIslands'] = [len(island_list)]
summary_stat['TotalPeninsulas'] = [len(peninsula_list)]
summary_stat['TotalWeakIslands'] = [len(json_dict['WeakIsland'])]
summary_stat['TotalWeakPeninsulas'] = [len(json_dict['WeakPeninsula'])]


print(json_dict)
#json_object = json.dumps(json_dict) 

with open(sys.argv[3], "w") as outfile:
    json.dump(json_dict, outfile)
 
with open(sys.argv[6], "w") as outfile:
    json.dump(island_dict, outfile)

with open(sys.argv[7], "w") as outfile:
    json.dump(peninsula_dict, outfile)

with open(sys.argv[9], "w") as outfile:
    json.dump(summary_stat, outfile)

with open(sys.argv[10], "w") as outfile:
    json.dump(freq_dict, outfile)
