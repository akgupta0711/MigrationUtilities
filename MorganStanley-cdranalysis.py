from pandasql import sqldf
import pandas as pd
import numpy as np
import csv
import os
import sys
from datetime import datetime, timedelta

def calculateBhca(calls):
    """
    Calculates the Busy Hour Call Attempts (BHCA) from a list of calls.

    Args:
        calls: A list of dictionaries, where each dictionary has 'start_time' 
               (datetime object) and 'duration_minutes' (integer).

    Returns:
        The BHCA (integer) and the start time of the busy hour (datetime object).
    """

    max_calls_in_hour = 0
    busy_hour_start_time = None
    total_call_bandwidth = 0
    total_call_video_bandwidth = 0
    
    # Iterate through potential busy hour start times (every minute of the day)
    for hour in range(24):
        for minute in range(60):
            current_hour_start = datetime(calls[0]["start_time"].year, calls[0]["start_time"].month, 
                                          calls[0]["start_time"].day, hour, minute)
            current_hour_end = current_hour_start + timedelta(minutes=60)
            
            calls_in_current_hour = 0

            bandwidth = 0
            video_bandwidth = 0

            # Count calls that fall within or overlap with the current hour window
            for call in calls:
                call_end_time = call["start_time"] + timedelta(minutes=call["duration_minutes"])
                if (call["start_time"] >= current_hour_start and call["start_time"] < current_hour_end) or \
                   (call_end_time > current_hour_start and call_end_time <= current_hour_end) or \
                   (call["start_time"] <= current_hour_start and call_end_time >= current_hour_end):
                    calls_in_current_hour += 1
                    bandwidth = bandwidth + call['bandwidth']
                    video_bandwidth = video_bandwidth + call['video_bandwidth']

            if calls_in_current_hour > max_calls_in_hour:
                max_calls_in_hour = calls_in_current_hour
                busy_hour_start_time = current_hour_start
                total_call_bandwidth = bandwidth
                total_call_video_bandwidth = video_bandwidth

    return max_calls_in_hour, busy_hour_start_time, total_call_bandwidth, total_call_video_bandwidth


def main():

    '''
    cdrDir = "/Users/akgupta/Downloads/cdrs2"
    ucmCluster = "EM1-AMS-CCP-UCM"
    siptrunks = ["10.230.3.193-Verizon", "ICT-WW1-AMS141-AMS142"]
    clusterType = "leaf"
    '''
    cdrDir = ""
    ucmCluster = ""
    siptrunks = []
    clusterType = "leaf"
    
    # total arguments
    n = len(sys.argv)
    print("Total arguments passed:", n - 1)
    if n == 1:
        print("Usage: " + '\n' + "python cdranalysis.py cdrdir=<> ucmcluster=<> siptrunks=<> clustertype=<> clustertype=<>" + '\n')
        print("cdrdir = Directory where CDR CDV files are stored")
        print("ucmcluster = UCM cluster as globalCallId_ClusterId in CDR file ")
        print("siptrunks = list of comma separated list of SIP Trunk as destDeviceName and origDeviceName in CDR file. There shouldn't be any space around comma.")
        print("clustertype = leaf or sme. Default = leaf, if not provided" + '\n')
        print("Example:")
        print("$ python cdranalysis.py cdrdir=/Users/Downloads/cdrs ucmcluster=UCM-Cluster-1 siptrunks=SIP-Trunk-1,SIP-Trunk-2 clustertype=leaf" + '\n')
        exit()
        
    # Arguments passed
    print("\nName of Python script:", sys.argv[0])
    print("Argument passed are:", '\n')

    for i in range(1, n):
        param = sys.argv[i].split("=")
        print(param[0] + " = " + param[1])
        if param[0] == "cdrdir":
            cdrDir = param[1]
        if param[0] == "ucmcluster":
            ucmCluster = param[1]
        if param[0] == "siptrunks":
            siptrunks = param[1].split(",")
        if param[0] == "clustertype":
            clusterType = param[1]

    headerSet = False
    cdrRows = []
    files = os.listdir(cdrDir)
    try:
        for file in files:
            #print("CSR file: ", file)
            with open(cdrDir + '/' + file, 'r') as file:
                csvreader = csv.reader(file)
                if headerSet == False:
                    header = next(csvreader)
                else:
                    next(csvreader)

                removeDataTypeRow = True
                for row in csvreader:
                    if removeDataTypeRow:
                        removeDataTypeRow = False
                    else:
                        cdrRows.append(row)
    except:
        print("Error in CDR file read")

    cdr = pd.DataFrame(cdrRows)
    if headerSet == False:
        cdr.columns = header
        headerSet = True

    print()
    print("Writting all CDRs in combinedCDR.csv")
    cdr.to_csv('combinedCDR.csv', index=False) 

    print("Number of CDR rows across all CDR csv files:", len(cdr))

    bhcaForTrunks = []

    try:
        #Read CDR from CSV files
        cdrData = sqldf(
        '''SELECT globalCallId_ClusterId, destDeviceName, origDeviceName, globalCallID_callId, origLegCallIdentifier, destLegIdentifier, dateTimeConnect, dateTimeDisconnect, origMediaCap_Bandwidth, destMediaCap_Bandwidth, origVideoCap_Bandwidth, destVideoCap_Bandwidth from cdr
        ''')

        calls = []

        for trunk in siptrunks:
            rowIndex = 0
            for row in cdrData.iterrows():
                if clusterType == "leaf" and ucmCluster == row[1]['globalCallId_ClusterID']:
                    call = {}
                    if row[1]['origDeviceName'] == trunk.strip() and int(row[1]['dateTimeConnect']) != 0:
                        utc_datetime = datetime.fromtimestamp(int(row[1]['dateTimeConnect']))
                        call["start_time"] = utc_datetime
                        call["duration_minutes"] = (int(row[1]['dateTimeDisconnect']) - int(row[1]['dateTimeConnect'])) // 60
                        call['bandwidth'] = int(row[1]['origMediaCap_Bandwidth'])
                        call['video_bandwidth'] = int(row[1]['origVideoCap_Bandwidth'])
                        calls.append(call)
                        #print("Orig: ", trunk, int(row[1]['origMediaCap_Bandwidth']), call)
                    elif row[1]['destDeviceName'] == trunk.strip() and int(row[1]['dateTimeConnect']) != 0:
                        utc_datetime = datetime.fromtimestamp(int(row[1]['dateTimeConnect']))
                        call["start_time"] = utc_datetime
                        call["duration_minutes"] = (int(row[1]['dateTimeDisconnect']) - int(row[1]['dateTimeConnect'])) // 60
                        call['bandwidth'] = int(row[1]['destMediaCap_Bandwidth'])
                        call['video_bandwidth'] = int(row[1]['destVideoCap_Bandwidth'])
                        calls.append(call)
                        #print("Dest: ", trunk, int(row[1]['destMediaCap_Bandwidth']), call)

                    if rowIndex == len(cdrData) - 1 and calls:
                        print()
                        print("Determining BHCA data for SIP Trunk: ", trunk.strip())
                        bhca, busy_hour_start, bandwidth, video_bandwidth = calculateBhca(calls)
                        print(f"Busy Hour Call Attempts (BHCA): {bhca}")
                        print(f"Busy Hour Start Time: {busy_hour_start}")
                        print(f"Busy Hour Total Audio Bandwidth: {bandwidth}")
                        print(f"Busy Hour Total Video Bandwidth: {video_bandwidth}")
                        bhcaInfo = {}
                        bhcaInfo['SIP Trunk'] = trunk
                        bhcaInfo['BHCA'] = bhca
                        bhcaInfo['BHCA Start Time'] = busy_hour_start
                        bhcaInfo['BHCA Total Audio Bandwidth'] = bandwidth
                        bhcaInfo['BHCA Total Video Bandwidth'] = video_bandwidth
                        bhcaForTrunks.append(bhcaInfo)
                        calls = []
                
                rowIndex = rowIndex + 1
    except:
        print("Error in determining BHCA")

    # Write info to file
    if bhcaForTrunks:
        print()
        print("Writing BHCA output file for Cluster:", row[1]['globalCallId_ClusterID'])
        bhcaAcrossAllTrunks = pd.DataFrame(bhcaForTrunks)
        bhcaAcrossAllTrunks.to_csv('bhca_' + row[1]['globalCallId_ClusterID'] + '.csv', index=False) 
        print()
    else:
        print("There is no data for cluster:", row[1]['globalCallId_ClusterID'])

    # Feature usage
    featureUsageList = []
    featureUsage = {}

    try:
        print("Start processing features")
        adhocConferenceCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId 
            from cdr 
            where lastRedirectRedirectReason = 98 AND lastRedirectRedirectOnBehalfOf = 4
        ''')
        featureUsage["AdhocConferenceCalls"] =  len(adhocConferenceCalls)

        agentGreetingCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId FROM cdr 
            where destCallTerminationOnBehalfOf = 33 
            AND origCalledPartyRedirectOnBehalfOf = 33 
            AND lastRedirectRedirectOnBehalfOf = 33 
            AND origCalledPartyRedirectReason = 752 
            AND lastRedirectRedirectReason = 752
        ''')
        featureUsage["AgentGreetingCalls"] =  len(agentGreetingCalls)

        parkCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId from cdr 
            where ORIGCALLTERMINATIONONBEHALFOF = 3 AND DESTCALLTERMINATIONONBEHALFOF = 3
        ''')
        featureUsage["ParkCalls"] =  len(parkCalls)

        parkPickupCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId from cdr 
            where lastRedirectRedirectReason = 8 AND lastRedirectRedirectOnBehalfOf = 3
        ''')
        featureUsage["ParkPickupCalls"] =  len(parkPickupCalls)

        pickupCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId from cdr 
            where lastRedirectRedirectOnBehalfOf = 16 AND joinOnBehalfOf = 16 AND lastRedirectRedirectReason = 5
        ''')
        featureUsage["PickupCalls"] =  len(pickupCalls)

        huntPilotCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId
            from cdr 
            where huntPilotDN != null OR  calledPartyPatternUsage = 7 
        ''')
        featureUsage["HuntPilotCalls"] =  len(huntPilotCalls)

        sqlStatement = "SELECT DISTINCT CDR1.globalCallId_ClusterId, CDR1.globalCallID_callManagerId, CDR1.globalCallID_callId " \
        "from cdr as CDR1 inner join cdr as CDR2 on CDR1.destLegIdentifier = CDR2.origConversationID --OR " \
        "CDR1.origLegCallIdentifier = CDR2.origConversationID Where CDR1.globalCallId_ClusterId != " + row[1]['globalCallId_ClusterID'] + " and CDR1.origCalledPartyRedirectReason = 354"
        recordingCalls = sqldf(sqlStatement)
        featureUsage["RecordingCalls"] =  len(recordingCalls)

        bargeCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId from cdr 
            where origCalledPartyRedirectReason = 114 AND lastRedirectRedirectReason = 114  AND origCalledPartyRedirectOnBehalfOf = 15 AND 
            lastRedirectRedirectOnBehalfOf = 15 AND joinOnBehalfOf = 15 
        ''')
        featureUsage["BargeCalls"] =  len(bargeCalls)

        monitoringCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId from cdr
            where origCalledPartyRedirectReason = 370 
            AND origCalledPartyRedirectOnBehalfOf = 28 
            AND lastRedirectRedirectOnBehalfOf = 28 
        ''')
        featureUsage["MonitoringCalls"] =  len(monitoringCalls)

        cBargeCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId from cdr 
            where lastRedirectRedirectReason = 98 AND lastRedirectRedirectOnBehalfOf = 4 
            AND originalCalledPartyNumber = finalCalledPartyNumber 
            AND originalCalledPartyNumber = lastRedirectDn
            AND finalCalledPartyNumber = lastRedirectDn
            AND originalCalledPartyNumber LIKE 'b00%'
        ''')
        featureUsage["CBargeCalls"] =  len(cBargeCalls)

        immediateDivertCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId
            from cdr 
            where  
            origCalledPartyRedirectOnBehalfOf = 14 OR lastRedirectRedirectOnBehalfOf = 14
        ''')
        featureUsage["ImmediateDivertCalls"] =  len(immediateDivertCalls)

        ipV6Calls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId, origIpv4v6Addr, destIpv4v6Addr
            from cdr 
            where origIpv4v6Addr LIKE '%:%' OR destIpv4v6Addr LIKE '%:%'
        ''')
        featureUsage["IPV6Calls"] =  len(ipV6Calls)

        forwardedORRedirectedCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId 
            from cdr 
            where origCalledPartyRedirectReason in (1,2,15) AND lastRedirectRedirectReason in (1,2,15) 
            AND origCalledPartyRedirectOnBehalfOf = 5 AND lastRedirectRedirectOnBehalfOf = 5
        ''')
        featureUsage["ForwardedORRedirectedCalls"] =  len(forwardedORRedirectedCalls)

        nativeCallQueueCalls = sqldf(
        '''SELECT DISTINCT globalCallId_ClusterId, globalCallID_callManagerId, globalCallID_callId
            from cdr 
            where huntPilotDN != null OR  calledPartyPatternUsage = 7 AND wasCallQueued = 1
        ''')
        featureUsage["NativeCallQueueCalls"] =  len(nativeCallQueueCalls)

        featureUsageList.append(featureUsage)

    except:
        print("Error in processing features")

    # Write info to file
    if featureUsageList:
        print()
        print("Writing feature usage report to file for Cluster:", row[1]['globalCallId_ClusterID'])
        featureUsageInfo = pd.DataFrame(featureUsageList)
        featureUsageInfo.to_csv('featureUsage_' + row[1]['globalCallId_ClusterID'] + '.csv', index=False) 
        print()
    else:
        print("There is no data for cluster:", row[1]['globalCallId_ClusterID'])


# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 
    
