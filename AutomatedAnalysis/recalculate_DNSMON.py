#!/usr/bin/python

import sys
import json
import pandas as pd
from os.path import exists
import statistics


def probe_separate_data(iteration_dict):

    probe_dict = {}
    for key in iteration_dict.keys():
        temp_dict ={}
        for query in iteration_dict[key]:
            if query["prb_id"] in temp_dict.keys():
                temp_dict[query["prb_id"]].append(query)
            else:
                temp_dict[query["prb_id"]] = []
                temp_dict[query["prb_id"]].append(query)
        probe_dict[key] = temp_dict

    return probe_dict


def iteration_separate_data(data, interval, start_time, end_time):
    iterations = (end_time - start_time)//interval

    #initialize dictionary with key iteration and value list of queries
    iteration_dict = {}
    for i in range(iterations+1):
        iteration_dict[i] = []

    #add queries to first dictionary
    for query in data:
        ts = query["timestamp"]
        if ts < end_time and ts >= start_time:
            iteration = (ts - start_time)//interval
            iteration_dict[iteration].append(query)

    return iteration_dict


def construct_table_UDPSOA_aggregate(iteration_dictionary, interval, start_time, root, islands, bad_probes):
    #df = pd.DataFrame(columns=['Root', 'VP', 'Pings Sent', 'Pings Failed', 'Timebin Start'])

    peninsulas = [probe for probe in bad_probes if probe not in islands]

    root_list = []
    full_count_list = []
    full_error_list = []
    full_percent_list = []
    no_islands_count_list = []
    no_islands_error_list = []
    no_islands_percent_list = []
    no_peninsula_count_list = []
    no_peninsula_error_list = []
    no_peninsula_percent_list = []
    no_bad_count_list = []
    no_bad_error_list= []
    no_bad_percent_list = []
    timebin_start_list = []
    timebin_duration_list = []

    for iteration in iteration_dict.keys():
        timebin_start = start_time + iteration*interval
        full_count = 0
        full_error = 0
        no_islands_count = 0
        no_islands_error = 0
        no_peninsula_count = 0
        no_peninsula_error = 0
        no_bad_count = 0
        no_bad_error = 0
        for query in iteration_dict[iteration]:
            if "error" in query.keys():
                full_error +=1
            full_count += 1

            if query["prb_id"] not in islands:
                if "error" in query.keys():
                    no_islands_error += 1
                no_islands_count += 1

            if query["prb_id"] not in peninsulas:
                if "error" in query.keys():
                    no_peninsula_error += 1
                no_peninsula_count += 1

            if query["prb_id"] not in bad_probes:
                if "error" in query.keys():
                    no_bad_error += 1
                no_bad_count += 1
        
        if full_count > 0:
            full_percent = 100*float(full_error)/float(full_count)
        else:
            full_percent = -1

        if no_islands_count > 0:
            no_islands_percent = 100*float(no_islands_error)/(no_islands_count)
        else:
            no_islands_percent = -1

        if no_peninsula_count > 0:
            no_peninsula_percent = 100*float(no_peninsula_error)/(no_peninsula_count)
        else:
            no_peninsula_percent = -1

        if no_bad_count > 0:
            no_bad_percent = 100*float(no_bad_error)/(no_bad_count)
        else:
            no_bad_percent = -1

        root_list.append(root)
        full_count_list.append(full_count)
        full_error_list.append(full_error)
        full_percent_list.append(full_percent)
        no_islands_count_list.append(no_islands_count)
        no_islands_error_list.append(no_islands_error)
        no_islands_percent_list.append(no_islands_percent)
        no_peninsula_count_list.append(no_peninsula_count)
        no_peninsula_error_list.append(no_peninsula_error)
        no_peninsula_percent_list.append(no_peninsula_percent)
        no_bad_count_list.append(no_bad_count)
        no_bad_error_list.append(no_bad_error)
        no_bad_percent_list.append(no_bad_percent)
        timebin_start_list.append(timebin_start)
        timebin_duration_list.append(interval)

    mean_std_dict = {}
    mean_std_dict[root] = []
    mean = sum(full_percent_list)/len(full_percent_list)
    std = statistics.pstdev(full_percent_list)
    mean_std_dict[root].append(mean)
    mean_std_dict[root].append(std)

    no_island_mean_std_dict = {}
    no_island_mean_std_dict[root] = []
    mean = sum(no_islands_percent_list)/len(no_islands_percent_list)
    std = statistics.pstdev(no_islands_percent_list)
    no_island_mean_std_dict[root].append(mean)
    no_island_mean_std_dict[root].append(std)

    final_mean_std_dict = {}
    final_mean_std_dict[root] = []
    mean = sum(no_bad_percent_list)/len(no_bad_percent_list)
    std = statistics.pstdev(no_bad_percent_list)
    final_mean_std_dict[root].append(mean)
    final_mean_std_dict[root].append(std)

    total_full_count = sum(full_count_list)
    total_full_error = sum(full_error_list)
    full_percent = 100*float(total_full_error)/float(total_full_count)

    total_no_islands_count = sum(no_islands_count_list)
    total_no_islands_error = sum(no_islands_error_list)
    no_islands_percent  = 100*float(total_no_islands_error)/float(total_no_islands_count)

    total_no_peninsula_count = sum(no_peninsula_count_list)
    total_no_peninsula_error = sum(no_peninsula_error_list)
    no_peninsula_percent = 100*float(total_no_peninsula_error)/float(total_no_peninsula_count)

    total_no_bad_count = sum(no_bad_count_list)
    total_no_bad_error = sum(no_bad_error_list)
    no_bad_percent = 100*float(total_no_bad_error)/float(total_no_bad_count)

    start_time = timebin_start_list[0]
    duration = sum(timebin_duration_list)


    root_list.append(root)
    full_count_list.append(total_full_count)
    full_error_list.append(total_full_error)
    full_percent_list.append(full_percent)
    no_islands_count_list.append(total_no_islands_count)
    no_islands_error_list.append(total_no_islands_error)
    no_islands_percent_list.append(no_islands_percent)
    no_peninsula_count_list.append(total_no_peninsula_count)
    no_peninsula_error_list.append(total_no_peninsula_error)
    no_peninsula_percent_list.append(no_peninsula_percent)
    no_bad_count_list.append(total_no_bad_count)
    no_bad_error_list.append(total_no_bad_error)
    no_bad_percent_list.append(no_bad_percent)
    timebin_start_list.append(start_time)
    timebin_duration_list.append(duration)

    df = pd.DataFrame(list(zip(root_list, full_count_list, full_error_list, full_percent_list, no_islands_count_list, no_islands_error_list, no_islands_percent_list, no_peninsula_count_list, no_peninsula_error_list, no_peninsula_percent_list, no_bad_count_list, no_bad_error_list, no_bad_percent_list, timebin_start_list, timebin_duration_list)),
               columns =['Root', 'TotalQueriesSent', 'TotalQueriesUnanswered', 'TotalPercentFail', 'NoIslandsQueriesSent', 'NoIslandsQueriesUnanswered', 'NoIslandsPercentFail', 'NoPeninsulaQueriesSent', 'NoPeninsulaQueriesUnanswered', 'NoPeninsulaPercentFail', 'NoBadProbesQueriesSent', 'NoBadProbesQueriesUnanswered', 'NoBadProbesPercentFail', 'TimebinStart', 'TimebinDuration'])

    return final_mean_std_dict, no_island_mean_std_dict, mean_std_dict, df

def construct_table_ping_aggregate(iteration_dictionary, interval, start_time, root, islands, bad_probes):
    #df = pd.DataFrame(columns=['Root', 'VP', 'PingsSent', 'PingsFailed', 'TimebinStart'])
    
    peninsulas = [probe for probe in bad_probes if probe not in islands]

    root_list = []
    full_count_list = []
    full_error_list = []
    full_percent_list = []
    no_islands_count_list = []
    no_islands_error_list = []
    no_islands_percent_list = []
    no_peninsula_count_list = []
    no_peninsula_error_list = []
    no_peninsula_percent_list = []
    no_bad_count_list = []
    no_bad_error_list= []
    no_bad_percent_list = []
    timebin_start_list = []
    timebin_duration_list = []

    for iteration in iteration_dict.keys():
        timebin_start = start_time + iteration*interval
        full_count = 0
        full_error = 0
        no_islands_count = 0
        no_islands_error = 0
        no_peninsula_count = 0
        no_peninsula_error = 0
        no_bad_count = 0
        no_bad_error = 0

        for query in iteration_dict[iteration]:
            fail = True
            for d in query["result"]:
                if "rtt" in d.keys():
                    fail = False
                    break
            if fail:
                full_error += 1
            full_count += 1

        if query["prb_id"] not in islands:
            fail = True
            for d in query["result"]:
                if "rtt" in d.keys():
                    fail = False
                    break
            if fail:
                no_islands_error += 1
            no_islands_count += 1

        if query["prb_id"] not in peninsulas:
            fail = True
            for d in query["result"]:
                if "rtt" in d.keys():
                    fail = False
                    break
            if fail:
                no_peninsula_error += 1
            no_peninsula_count += 1


        if query["prb_id"] not in bad_probes:
            fail = True
            for d in query["result"]:
                if "rtt" in d.keys():
                    fail = False
                    break
            if fail:
                no_bad_error += 1
            no_bad_count += 1

        if full_count > 0:
            full_percent = 100*float(full_error)/float(full_count)
        else:
            full_percent = -1

        if no_islands_count > 0:
            no_islands_percent = 100*float(no_islands_error)/(no_islands_count)
        else:
            no_islands_percent = -1

        if no_peninsula_count > 0:
            no_peninsula_percent = 100*float(no_peninsula_error)/(no_peninsula_count)
        else:
            no_peninsula_percent = -1

        if no_bad_count > 0:
            no_bad_percent = 100*float(no_bad_error)/(no_bad_count)
        else:
            no_bad_percent = -1

        root_list.append(root)
        full_count_list.append(full_count)
        full_error_list.append(full_error)
        full_percent_list.append(full_percent)
        no_islands_count_list.append(no_islands_count)
        no_islands_error_list.append(no_islands_error)
        no_islands_percent_list.append(no_islands_percent)
        no_peninsula_count_list.append(no_peninsula_count)
        no_peninsula_error_list.append(no_peninsula_error)
        no_peninsula_percent_list.append(no_peninsula_percent)
        no_bad_count_list.append(no_bad_count)
        no_bad_error_list.append(no_bad_error)
        no_bad_percent_list.append(no_bad_percent)
        timebin_start_list.append(timebin_start)
        timebin_duration_list.append(interval)

    total_full_count = sum(full_count_list)
    total_full_error = sum(full_error_list)
    full_percent = 100*float(total_full_error)/float(total_full_count)

    total_no_islands_count = sum(no_islands_count_list)
    total_no_islands_error = sum(no_islands_error_list)
    no_islands_percent  = 100*float(total_no_islands_error)/float(total_no_islands_count)

    total_no_peninsula_count = sum(no_peninsula_count_list)
    total_no_peninsula_error = sum(no_peninsula_error_list)
    no_peninsula_percent = 100*float(total_no_peninsula_error)/float(total_no_peninsula_count)

    total_no_bad_count = sum(no_bad_count_list)
    total_no_bad_error = sum(no_bad_error_list)
    no_bad_percent = 100*float(total_no_bad_error)/float(total_no_bad_count)

    start_time = timebin_start_list[0]
    duration = sum(timebin_duration_list)
    
    root_list.append(root)
    full_count_list.append(total_full_count)
    full_error_list.append(total_full_error)
    full_percent_list.append(full_percent)
    no_islands_count_list.append(total_no_islands_count)
    no_islands_error_list.append(total_no_islands_error)
    no_islands_percent_list.append(no_islands_percent)
    no_peninsula_count_list.append(total_no_peninsula_count)
    no_peninsula_error_list.append(total_no_peninsula_error)
    no_peninsula_percent_list.append(total_no_peninsula_percent)
    no_bad_count_list.append(total_no_bad_count)
    no_bad_error_list.append(total_no_bad_error)
    no_bad_percent_list.append(no_bad_percent)
    timebin_start_list.append(start_time)
    timebin_duration_list.append(duration)


    df = pd.DataFrame(list(zip(root_list, full_count_list, full_error_list, full_percent_list, no_islands_count_list, no_islands_error_list, no_islands_percent_list, no_peninsula_count_list, no_peninsula_error_list, no_peninsula_percent_list, no_bad_count_list, no_bad_error_list, no_bad_percent_list, timebin_start_list, timebin_duration_list)),
               columns =['Root', 'TotalQueriesSent', 'TotalQueriesUnanswered', 'TotalPercentFail', 'NoIslandsQueriesSent', 'NoIslandsQueriesUnanswered', 'NoIslandsPercentFail', 'NoPeninsulaQueriesSent', 'NoPeninsulaQueriesUnanswered', 'NoPeninsulaPercentFail', 'NoBadProbesQueriesSent', 'NoBadProbesQueriesUnanswered', 'NoBadProbesPercentFail', 'TimebinStart', 'TimebinDuration'])
    return df




start_time =int(sys.argv[1])
end_time= int(sys.argv[2])
root = sys.argv[3]
interval = int(sys.argv[4])
data_type = sys.argv[5]
data= []

for file in open(sys.argv[6],'r'):
    file = file.rstrip('\n')
    ndata = [json.loads(line) for line in open(file,'r')]
    data.extend(ndata)


iteration_dict = iteration_separate_data(data, interval, start_time, end_time)
probe_dict = probe_separate_data(iteration_dict)

with open(sys.argv[7], 'r') as j:
    islands_dict = json.load(j)
islands = islands_dict['Islands']

with open(sys.argv[8], 'r') as j:
    bad_probes_dict = json.load(j)
bad_probes = bad_probes_dict[root]['bad probes']

if (data_type == "ping"):
    df1 = construct_table_ping_aggregate(iteration_dict, interval, start_time, root, islands, bad_probes)
else:
    final_mean_std_dict, no_island_mean_std_dict, mean_std_dict, df1 = \
        construct_table_UDPSOA_aggregate(iteration_dict, interval, start_time, root, islands, bad_probes)


df1.to_csv(sys.argv[9], sep = '\t', index=False, mode ='a')

if exists(sys.argv[10]):
    with open(sys.argv[10], "r") as jsonFile:
            file_data = json.load(jsonFile)
else:
    file_data = {}

file_data.update(mean_std_dict)

with open(sys.argv[10], "w") as jsonFile:
        json.dump(file_data, jsonFile)

if exists(sys.argv[11]):
    with open(sys.argv[11], "r") as jsonFile:
        file_data = json.load(jsonFile)
else:
    file_data = {}

file_data.update(final_mean_std_dict)

with open(sys.argv[11], "w") as jsonFile:
    json.dump(file_data,jsonFile)


if exists(sys.argv[12]):
    with open(sys.argv[12], "r") as jsonFile:
        file_data = json.load(jsonFile)
else:
    file_data = {}

file_data.update(no_island_mean_std_dict)

with open(sys.argv[12], "w") as jsonFile:
    json.dump(file_data,jsonFile)


