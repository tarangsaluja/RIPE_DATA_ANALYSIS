#!/usr/bin/python

import sys
import json
import pandas as pd
from os.path import exists
import matplotlib.pyplot as plt


#Separate the queries into dictionary with 
#KEY: Probes
#VALUE: List of queries corresponding to probes
def probe_separate_data(data, start_time, end_time):
    probe_dict = {}

    #add queriesto probe_dict
    for query in data:
        if (query["timestamp"] < end_time and query["timestamp"] >= start_time):
            if query["prb_id"] in probe_dict.keys():
                probe_dict[query["prb_id"]].append(query)
            else:
                probe_dict[query["prb_id"]] = []
                probe_dict[query["prb_id"]].append(query)

    return probe_dict


#Go through queries for each probe and extract useful data
def UDPSOA_analysis(probe_dict, root):

    #initialize lists to be collected for each probe
    root_list = []
    length_list = []
    probe_list = []
    error_list = []
    count_list = []
    percent_list = []
    sequence_list = []

    #iterate through probes
    for prb_id in probe_dict.keys():

        #initialize variables before iterating through queries 
        fail_start = 0
        longest_fail = 0
        fail_status = False
        last_query = {}
        error = 0
        count = 0
        seq = []

        #iterate through queries
        for query in probe_dict[prb_id]:


            #if there is an error, increase appropriate variabels
            #ifnot an error, then modify appropriate variables
            if "error" in query.keys():
                seq.append(-1)
                error += 1
                if fail_status == False:
                    fail_status = True
                    fail_start = query["timestamp"]
            else:
                seq.append(1)
                if fail_status == True:
                    fail_status = False
                    fail_duration = query["timestamp"] - fail_start
                    if fail_duration > longest_fail:
                        longest_fail = fail_duration
            last_query = query
            count += 1
        
        #check edge case for longest failure
        if fail_status == True:
            fail_duration = last_query["timestamp"] - fail_start
            if fail_duration > longest_fail:
                longest_fail = fail_duration
        
        #compute percentage failure
        if count > 0:
            percent = float(error)*100/float(count)
        else:
            percent = 0
        
        #add relevant information
        if count > 0:
            root_list.append(root)
            length_list.append(longest_fail)
            probe_list.append(prb_id)
            error_list.append(error)
            count_list.append(count)
            percent_list.append(percent)
            sequence_list.append(seq)

    #create relevant dataframes 
    length_df = pd.DataFrame(list(zip(root_list, probe_list, length_list)), columns = ['root_list', 'probe_list', 'length_list'])
    percent_df = pd.DataFrame(list(zip(root_list, probe_list, count_list, error_list, percent_list)), columns = ['root_list', 'probe_list', 'count_list', 'error_list', 'percent_list'])
    sequence_df = pd.DataFrame(list(zip(root_list, probe_list, sequence_list)), columns = ['root_list', 'probe_list', 'sequence_list'])
    return length_df, percent_df, sequence_df


#def construct_table_UDPSOA(probe_dict, root):
#    root_list = []
#    count_list = []
#    percent_list = []
#    error_list = []
#    probe_list = []
#    for prb_id in probe_dict.keys():
#        count = 0
#        error = 0
#        for query in probe_dict[prb_id]:
#            if "error" in query.keys():
#                error += 1
#            count += 1
#        root_list.append(root)
#        count_list.append(count)
#        error_list.append(error)
#        probe_list.append(prb_id)
#
#        if count > 0:
#            percent = float(error)*100/float(count)
#        else:
#            percent = 0
#
#        percent_list.append(percent)
#
#    df = pd.DataFrame(list(zip(root_list, probe_list, count_list, error_list, percent_list)), columns = ['root_list', 'probe_list', 'count_list', 'error_list', 'percent_list'])
#    return df


#Go through queries and extract relevant data
def Ping_analysis(probe_dict, root):

    #initialize lists to be collected for each probe
    root_list = []
    length_list = []
    probe_list = []
    error_list = []
    count_list = []
    percent_list = []
    sequence_list = []

    #iterate through probes
    for prb_id in probe_dict.keys():

        #initialize variables to be modified
        fail_start = 0
        longest_fail = 0
        fail_status = False
        last_query = {}
        error = 0
        count = 0
        seq = []

        #iterate through queries
        for query in probe_dict[prb_id]:

            fail = True

            #check if fail
            for d in query["result"]:
                if "rtt" in d.keys():
                    fail = False
                    break
            
            #modify according to whether or not it is a fail
            if fail:
                error += 1
                seq.append(-1)
                if fail_status == False:
                    fail_status = True
                    fail_start = query["timestamp"]
            else:
                seq.append(1)
                if fail_status == True:
                    fail_status = False
                    fail_duration = query["timestamp"] - fail_start
                    if fail_duration > longest_fail:
                        longest_fail = fail_duration
            count += 1
            last_query = query

        #check edge case for longest outage
        if fail_status == True:
            fail_duration = last_query["timestamp"] - fail_start
            if fail_duration > longest_fail:
                longest_fail = fail_duration

        #compute percentage failure
        if count > 0:
            percent = float(error)*100/float(count)
        else:
            percent = 0
        
        #add information to the appropriate lists
        root_list.append(root)
        length_list.append(longest_fail)
        probe_list.append(prb_id)
        error_list.append(error)
        count_list.append(count)
        percent_list.append(percent)
        sequence_list.append(seq)

    #create appropriate dfs
    length_df = pd.DataFrame(list(zip(root_list, probe_list, length_list)), columns = ['root_list', 'probe_list', 'length_list'])
    percent_df = pd.DataFrame(list(zip(root_list, probe_list, count_list, error_list, percent_list)), columns = ['root_list', 'probe_list', 'count_list', 'error_list', 'percent_list'])
    sequence_df = pd.DataFrame(list(zip(root_list, probe_list, sequence_list)), columns = ['root_list', 'probe_list', 'sequence_list'])
    return length_df, percent_df, sequence_df
    




#def construct_table_ping(probe_dict, root):
#    root_list = []
#    count_list = []
#    percent_list = []
#    error_list = []
#    probe_list = []
#    for prb_id in probe_dict.keys():
#        count = 0
#        error = 0
#        for query in probe_dict[prb_id]:
#            fail = True
#            for d in query["result"]:
#                if "rtt" in d.keys():
#                    fail = False
#                    break
#            if fail:
#                error += 1
#            count += 1
#        root_list.append(root)
#        count_list.append(count)
#        error_list.append(error)
#        probe_list.append(prb_id)

#        if count > 0:
#            percent = float(error)*100/float(count)
#        else:
#            percent = 0

 #       percent_list.append(percent)

 #   df = pd.DataFrame(list(zip(root_list, probe_list, count_list, error_list, percent_list)), columns = ['root_list', 'probe_list', 'count_list', 'error_list', 'percent_list'])
 #   return df


def plot_percent_graph(df, filename, label, x_lab):
    df = pd.DataFrame(df)

    stats_df = df \
    .groupby(label) \
    [label] \
    .agg('count') \
    .pipe(pd.DataFrame) \
    .rename(columns = {label: 'frequency'})

    # PDF
    stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])

    # CDF
    stats_df['cdf'] = stats_df['pdf'].cumsum()
    stats_df = stats_df.reset_index()

    
    plt.step(x = stats_df[label], y = stats_df['pdf'])
    plt.step(x = stats_df[label], y = stats_df['cdf'])

    plt.xlabel(x_lab)

    plt.savefig(filename)

    plt.clf()



    #plot = stats_df.plot(x = label, y = ['pdf', 'cdf'], grid = True)
   # plot.set_xlabel(x_lab)
   # fig = plot.get_figure()
   # fig.savefig(filename)



#./parse_data.py $START $STOP $i $BIN $TYPE $filename1 $filename3 $filename5  $txtfile

#Readin relevant variables
start_time = int(sys.argv[1])
end_time = int(sys.argv[2])
root = sys.argv[3]
#binn = sys.argv[4]
data_type = sys.argv[5]
data_info = (sys.argv[8].split("/"))[-2]
x_lab = str(root) + " " + str(data_info)

#Read in the data from the files
data = []
with open(sys.argv[9], 'r') as txtfile:
    for file in txtfile:
        file = file.rstrip('\n')
        print(file)
        if not file:
            continue
        with open(file, 'r') as finp:
            ndata = [json.loads(line) for line in finp]
            data.extend(ndata)

#print("data downloaded")



prb_dict = probe_separate_data(data, start_time, end_time)
if (data_type == "ping"):
    length_df, percent_df, sequence_df = Ping_analysis(prb_dict, root)
else:
    length_df, percent_df, sequence_df = UDPSOA_analysis(prb_dict, root)


percent_df.to_csv(sys.argv[6], sep='\t', index=False, mode = 'a')
length_df.to_csv(sys.argv[7], sep='\t', index=False, mode = 'a')
sequence_df.to_csv(sys.argv[8], sep='\t', index=False, mode = 'a')



#df2 = df1['percent_list']
#label = 'percent_list' 
#plot_percent_graph(df2, sys.argv[5], label, x_lab)


#df4 = df3['length_list']
#label = 'length_list'
#plot_percent_graph(df3, sys.argv[7], label, x_lab)
#df2 = pd.DataFrame(df2)
#
#stats_df = df2 \
#.groupby('percent_list') \
#['percent_list'] \
#.agg('count') \
#.pipe(pd.DataFrame) \
#.rename(columns = {'percent_list': 'frequency'})

# PDF
#stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])

# CDF
#stats_df['cdf'] = stats_df['pdf'].cumsum()
#stats_df = stats_df.reset_index()

#plot = stats_df.plot(x = 'percent_list', y = ['pdf', 'cdf'], grid = True)
#fig = plot.get_figure()
#fig.savefig(sys.argv[5])

#df1.to_csv(sys.argv[4], sep='\t', index=False, mode = 'a')
#df3.to_csv(sys.argv[6], sep='\t', index=False, mode = 'a')
