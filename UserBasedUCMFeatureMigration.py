import pandas as pd
import csv
import os
import sys
import shutil
import requests
import json

def createREADME(directory_path):
    print("Creating README.txt")
    readme = "*** PLEASE USE TEXT EDITOR TO MANIPULATE .csv FILES. EXCEL remove '+' from Phone number and error will occur in .csv file upload." + '\n\n' \
             "*** ALSO, If you see any error, do manual validation for that error e.g. number is not adding in CH or showing red, essentially means that they " + \
             "have to investigate why number is not getting added (either already present or invalid)" + '\n\n' \
            \
            "These are the steps to use output files:" + '\n\n' \
            "1) If number.txt is there, review it and use that to provision in Control Hub (CH) at: Calling -> Manage -> Add. Copy and past numbers in CH." + '\n' \
            "   Note: You can configure 1000 numbers at a time in CH. If there are more than 1000 numbers in CSV then up to 1000 numbers needs to be configured multiple times." + '\n\n' \
            "2) Review and Provision VirtualLineBulk.csv in CH at: Calling -> Virtual Lines -> Manage -> Upload CSV."  + '\n\n' \
            "3) Review and Provision UserFeatures_Internal.csv or UserFeatures_External.csv in CH at: Calling -> Service Settings -> Manage User Calling Data." + '\n' \
            "   UserFeatures_Internal.csv contain Call Forward setting from UCM for internal call forward and UserFeatures_External.csv."  + '\n' \
            "   from UCM external call forward setting. Rest of the settings are same. Note: This is only for user, not for workspace."  + '\n\n' \
            "   NOTE: 'Monitored Line/Call Park Extension 1', Monitored Line/Call Park Extension 2' etc. columns should have emailID. Investigate if a DN shows up there."   + '\n\n' \
            "4) Create a zip (using right click on the Filtered -> <custom device pool name> directory, use Compress. Use this zip file to upload to " + '\n' \
            "   CH at: Updates and Migrations -> Migrate features from UCM -> Actions -> Import Config." + '\n' \
            "   This will provision ConfiguredLineBulk.csv and deviceLineKeyConfiguration.csv into Webex Calling." + '\n\n' \
            "5) Review and Provision CallPickupGroup.csv, CallParkGroup.csv, HuntGroupBulk.csv, CallQueueBulk.csv and AutoAtteandant.csv at: " + '\n' \
            "   Calling -> Features -> <Feature> -> Manage."
    
    readme_file = directory_path + "/README.txt"
    with open(readme_file, 'w') as f:
        f.write(readme)


#Create User, Device and Virtual Lines Filtered List
# Loop through all of the emails and devices in userstomigrate_sample and filter out rows from following CSVs:
# VirtualLineBulk, ConfiguredLineBulk, deviceLineKeyConfiguration, callForward_Internal, callForward_External
# and create new set of CSV files under a sub-directory - FilteredCSVs

def createUserDeviceVirtuallineFilteredList(directory_path, userstomigrate_sample, VirtualLineBulk, ConfiguredLineBulk, deviceLineKeyConfiguration, userFeaturesInternal, userFeaturesExternal, setExternalMailbox, group):

    print("Starting to create user list based user / device specific CSV files" + '\n\n')
    deviceLineKeyList = []
    shareLineUserNotInUserList = []
    
    for indexUL, rowUL in userstomigrate_sample.iterrows():
        try:
            print("Start filtering ConfiguredLineBulk for user/device in UserList", rowUL['EMAIL ID'], rowUL['DEVICE MAC'], group)
            for indexCL, rowCL in ConfiguredLineBulk.iterrows():
                
                headers = list(ConfiguredLineBulk.columns)

                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    if pd.isnull(rowUL['EMAIL ID']) == True:
                        continue
                    try: 
                        try: 
                            if (pd.isnull(rowCL['Location ' + str(userNum)]) != False):
                                rowCL['Location ' +  str(userNum)] = rowUL['Location']
                        except:
                            pass
                        if ('Username' in header) and ((rowUL['CUSTOM DEVICE POOL'] == group) or (group == "all")):
                            try:
                                if ((pd.isnull(rowCL['Username ' + str(userNum)]) == False) and (rowCL['Username ' + str(userNum)] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowCL.fillna('', inplace=True)
                                        if rowCL not in deviceLineKeyList:
                                            deviceLineKeyList.append(rowCL)
                                            appended = True
                                if ((pd.isnull(rowCL['Username ' + str(userNum)]) == False) and (rowCL['Username ' + str(userNum)] != rowUL['EMAIL ID'])):
                                    if rowCL['Username ' + str(userNum)] not in shareLineUserNotInUserList:
                                        shareLineUserNotInUserList.append(rowCL['Username ' + str(userNum)])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                    except:
                        print("Issue in creating  with filtered ConfiguredLineBulk for header ", header)
                
                if ((rowUL['CUSTOM DEVICE POOL'] == group) or (group == "all")):
                    deviceID = rowUL['DEVICE MAC']
                    try:
                        if rowUL['DEVICE MAC'] and rowUL['DEVICE MAC'].startswith("SEP"):
                            deviceID = rowUL['DEVICE MAC'][3:]
                    except:
                        pass

                    try:
                        if ((pd.isnull(rowCL['Device MAC']) == False) and (rowCL['Device MAC'] == deviceID)):
                            rowCL.fillna('', inplace=True)
                            deviceLineKeyList.append(rowCL)
                    except:
                        print("Issue with Device MAC", deviceID)

        except: 
            print("Error in processing for createUserDeviceVirtuallineFilteredList for: ", rowUL['EMAIL ID'], rowUL['DEVICE MAC'])
    
    # Warn if there shared Line users which are not in UserList
    if shareLineUserNotInUserList:
        print('\n\n' + "WARNING: You have users in shared Line users but not in userList ")  
        
    # Creating filtered VirtualLineBulk
    # Use deviceLineKeyList which contains filtered list of devices based on user list
    vl = pd.DataFrame(deviceLineKeyList)
    headers = vl.columns.tolist()
    vlList = []
    
    for row in deviceLineKeyList:
        userNum = 1
        print("Start filtering Virtual Line  CSV for device in ConfiguredLineBulk: " + row['Device MAC'])
        for header in headers:
            try: 
                if 'Type' in header:     
                    if (row['Type ' + str(userNum)] and (row['Type ' + str(userNum)] == "VIRTUAL_PROFILE")):
                        virtualExtNum = {}
                        virtualExtNum['Extension'] = ""
                        virtualExtNum['Phone Number'] = ""
                        virtualExtNum['Location'] = ""
                        try:
                            if row['Extension ' + str(userNum)]: 
                                virtualExtNum['Extension'] = int(row['Extension ' + str(userNum)])
                                row['Extension ' + str(userNum)] = int(row['Extension ' + str(userNum)])
                        except:
                            pass
                        try:
                            if row['Phone Number ' + str(userNum)]:
                                virtualExtNum['Phone Number'] = int(row['Phone Number ' + str(userNum)])
                                row['Phone Number ' + str(userNum)] = int(row['Phone Number ' + str(userNum)])
                        except:
                            pass
                        try:
                            if row['Location ' + str(userNum)]:
                                virtualExtNum['Location'] = row['Location ' + str(userNum)]
                        except:
                            pass
                                
                        # Store in a temprarory list
                        if virtualExtNum:
                            vlList.append(virtualExtNum)
                    
                    # Make sure all phone numbers are integer in deviceLineKeyList
                    if (row['Type ' + str(userNum)] and ((row['Type ' + str(userNum)] == "USER") or (row['Type ' + str(userNum)] == "PLACE"))):
                        try:
                            if row['Extension ' + str(userNum)]: 
                                row['Extension ' + str(userNum)] = int(row['Extension ' + str(userNum)])
                        except:
                            pass
                        try:
                            if row['Phone Number ' + str(userNum)]:
                                row['Phone Number ' + str(userNum)] = int(row['Phone Number ' + str(userNum)])
                        except:
                            pass 
                    
                    userNum = userNum + 1
                    
            except:
                print("Issue in creating  with filtered VirtualLineBulk for header ", header)  
                userNum = userNum + 1
                
    # Remove duplicate rows from VirtualLineBulk file and filter for Virtual line from 
    vlOrig = VirtualLineBulk.drop_duplicates()
    # Change Extension to int
    vlFilteredList = []
    for row in vlOrig.iterrows():
        try:
            index = 0
            while index < len(vlList):
                if (str(row[1]['Phone Number']) and str(vlList[index]['Phone Number'])) and ((str(row[1]['Phone Number']) == str(vlList[index]['Phone Number'])) or (str(vlList[index]['Phone Number']) in str(row[1]['Phone Number'])) or (str(row[1]['Phone Number']) in str(vlList[index]['Phone Number']))):
                    row[1]['Location'] = vlList[index]['Location']
                    vlFilteredList.append(row[1])
                    break
                if (str(row[1]['Extension']) and str(vlList[index]['Extension'])) and (str(row[1]['Extension']) == str(vlList[index]['Extension'])):
                    row[1]['Location'] = vlList[index]['Location']
                    vlFilteredList.append(row[1])
                    break
                index = index + 1
        except:
            print("Error in creating Virtual Line Filered list for ", row[1]['Display Name'])

    # Create numbers.csv
    numbers = ""
    for elem in vlFilteredList:
        if str(elem['Phone Number']) != "":
            if numbers:
                numbers = numbers +","
            numbers = numbers + str(elem['Phone Number'])
    
    if numbers:
        numbers_file = directory_path + "/numbers.txt"
        with open(numbers_file, 'w') as f:
            f.write(numbers)
    
    # Filter deviceLineKeyConfiguration for Device MAC in ConfiguredLineBulk
    print('\n\n' + "Start filtering device Line Key Configuration CSV")
    deviceList = []
    for row in deviceLineKeyList:
        deviceList.append(row['Device MAC'])
        
    deviceLineKeyConfigurationFiltered = deviceLineKeyConfiguration[deviceLineKeyConfiguration['Device MAC'].isin(deviceList)]
    # Create filtered device LineKey Configuration CSV
    deviceLineKeyConfigurationFiltered.to_csv(directory_path + '/deviceLineKeyConfiguration.csv', index=False)
    
    # Create filtered Virtual Line CSV
    fileVL = directory_path + '/VirtualLineBulk.csv'
    with open(fileVL, 'w') as file2:
        writer = csv.writer(file2)
        writer.writerow(vlOrig.columns.tolist())
        writer.writerows(vlFilteredList)    

    # Create filtred Configured Line CSV
    fileCL = directory_path + '/ConfiguredLineBulk.csv'
    with open(fileCL, 'w') as file3:
        writer = csv.writer(file3)
        writer.writerow(headers)
        writer.writerows(deviceLineKeyList)

    # Filter userFeaturesInternal for user in userstomigrate_sample
    print("Start filtering User Features Filtered CSV")
    userList = []
    for indexUL, rowUL in userstomigrate_sample.iterrows():
        if pd.isnull(rowUL['EMAIL ID']) == False:
            userList.append(rowUL['EMAIL ID'])

    userFeaturesInternalFiltered = userFeaturesInternal[userFeaturesInternal['User Email'].isin(userList)]
    userFeaturesInternalFiltered = userFeaturesInternalFiltered.replace({True: 'TRUE', False: 'FALSE'})
    if setExternalMailbox:
        userFeaturesInternalFiltered['Message Storage External Mailbox Email'] = userFeaturesInternalFiltered['User Email']
        userFeaturesInternalFiltered['Message Storage Type'] = "EXTERNAL"
    # Create filtered device LineKey Configuration CSV
    userFeaturesInternalFiltered.to_csv(directory_path + '/UserFeatures_Internal.csv', index=False) 

    # Filter userFeaturesExternal for user in userstomigrate_sample       
    userFeaturesExternalFiltered = userFeaturesExternal[userFeaturesExternal['User Email'].isin(userList)]
    userFeaturesExternalFiltered = userFeaturesExternalFiltered.replace({True: 'TRUE', False: 'FALSE'})
    if setExternalMailbox:
        userFeaturesExternalFiltered['Message Storage External Mailbox Email'] = userFeaturesExternalFiltered['User Email']
        userFeaturesInternalFiltered['Message Storage Type'] = "EXTERNAL"

    # Create filtered device LineKey Configuration CSV
    # Create filtered device LineKey Configuration CSV
    userFeaturesExternalFiltered.to_csv(directory_path + '/UserFeatures_External.csv', index=False)    

def createLocationFeatureFilteredList(directory_path, userstomigrate, HuntGroupBulk, CallQueueBulk, AutoAttendantBulk, CallParkGroup, CallPickupGroup, SharedLineGroup, group):
    
    print('\n\n' + "Starting to create user list based Location feature based CSV files")
    ### Hunt Group ###
    huntGroupList = []
    agentNotInUserList = []
    headers = list(HuntGroupBulk.columns)
    for indexCL, rowHG in HuntGroupBulk.iterrows():
        try:
            print("Start filtering HuntGroupBulk for user/device in Hunt Group" + rowHG['Name'])
            for iindexUL, rowUL in userstomigrate.iterrows():
                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    try: 
                        if 'Agent' in header:
                            try:
                                if ((pd.isnull(rowHG['Agent' + str(userNum) + ' ID']) == False) and (rowHG['Agent' + str(userNum) + ' ID'] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowHG.fillna('', inplace=True)
                                        huntGroupList.append(rowHG)
                                        appended = True
                                if ((pd.isnull(rowHG['Agent' + str(userNum) + ' ID']) == False) and (rowHG['Agent' + str(userNum) + ' ID'] != rowUL['EMAIL ID'])):
                                    if rowHG['Agent' + str(userNum) + ' ID'] not in agentNotInUserList:
                                        agentNotInUserList.append(rowHG['Agent' + str(userNum) + ' ID'])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                    except:
                        print("Issue in creating  with filtered HuntGroupBulk for header ", header)
        except: 
            print("Error in processing for createLocationFeatureFilteredList for Hunt Group: ", rowHG['Name'])  
    # Warn if there agents which are not in UserList
    if agentNotInUserList:
        print("WARNING: You have in agents in Hunt Groups but not in userList", agentNotInUserList) 

    # Create filtred HuntGroupBulkCSV
    fileHG = directory_path + '/HuntGroupBulk.csv'
    with open(fileHG, 'w') as file1:
        writer = csv.writer(file1)
        writer.writerow(headers)
        writer.writerows(huntGroupList)

    ### Call Queue ###
    callQueueList = []
    agentNotInUserList = []
    headers = list(CallQueueBulk.columns)
    for indexCL, rowCQ in CallQueueBulk.iterrows():
        try:
            print("Start filtering CallQueueBulk for user/device in Hunt Group" + rowCQ['Name'])
            for iindexUL, rowUL in userstomigrate.iterrows():
                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    try: 
                        if 'Agent' in header:
                            try:
                                if ((pd.isnull(rowCQ['Agent' + str(userNum) + ' ID']) == False) and (rowCQ['Agent' + str(userNum) + ' ID'] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowCQ.fillna('', inplace=True)
                                        callQueueList.append(rowCQ)
                                        appended = True
                                if ((pd.isnull(rowCQ['Agent' + str(userNum) + ' ID']) == False) and (rowCQ['Agent' + str(userNum) + ' ID'] != rowUL['EMAIL ID'])):
                                    if rowCQ['Agent' + str(userNum) + ' ID'] not in agentNotInUserList:
                                        agentNotInUserList.append(rowCQ['Agent' + str(userNum) + ' ID'])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                    except:
                        print("Issue in creating  with filtered CallQueueBulk for header ", header)
        except: 
            print("Error in processing for createLocationFeatureFilteredList for Call Queue: ", rowCQ['Name'])  
    # Warn if there agents which are not in UserList
    if agentNotInUserList:
        print("WARNING: You have in agents in Call Queues but not in userList", agentNotInUserList) 

    # Create filtred HuntGroupBulkCSV
    fileCQ = directory_path + '/CallQueueBulk.csv'
    with open(fileCQ, 'w') as file2:
        writer = csv.writer(file2)
        writer.writerow(headers)
        writer.writerows(callQueueList)

    ### Call Park Group ###
    callParkList = []
    callParkName = ""
    callPark = {}
    appendCallPark = False
    for rowCP in CallParkGroup.iterrows():
        if (rowCP[1]['Feature Type'] == "CALL PARK GROUP"):
            if rowCP[1]['Config Name'] != callParkName:
                callParkName = rowCP[1]['Config Name']
                callPark = {}
                callPark['Call Park Name'] = rowCP[1]['Config Name']
                callPark['Location Name'] = ""
                callPark['Recall To'] = ""
                callPark['Hunt Group Name'] = ""
                callPark['Member Action'] = "ADD"
                userNum = 1
                if callParkName:
                    appendCallPark = True
                    
            if pd.isnull(rowCP[1]['Email ID']) == False:
                callPark['Agent' + str(userNum) + ' ID'] = rowCP[1]['Email ID']
            elif pd.isnull(rowCP[1]['User']) == False:
                callPark['Agent' + str(userNum) + ' ID'] = rowCP[1]['User']
            elif pd.isnull(rowCP[1]['Device']) == False:
                callPark['Agent' + str(userNum) + ' ID'] = rowCP[1]['Device']
            else:
                callPark['Agent' + str(userNum) + ' ID'] = rowCP[1]['Line']
            userNum = userNum + 1
            
        if (rowCP[1]['Feature Type'] == "CALL PARK GROUP") and callParkName and appendCallPark:
            callParkList.append(callPark)
    
    callParkBulk = pd.DataFrame(callParkList)
    callParkBulk.fillna('', inplace=True)
    callParkBulk = callParkBulk.drop_duplicates()
    callParkFilteredList = []
    userNotInUserList = []
    headers = list(callParkBulk.columns)
    for indexCL, rowCPk in callParkBulk.iterrows():
        try:
            print("Start filtering callParkBulk for user/device in Hunt Group " + rowCPk['Call Park Name'])
            for iindexUL, rowUL in userstomigrate.iterrows():
                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    try: 
                        if 'Agent' in header:
                            try:
                                if ((pd.isnull(rowCPk['Agent' + str(userNum) + ' ID']) == False) and (rowCPk['Agent' + str(userNum) + ' ID'] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowCPk.fillna('', inplace=True)
                                        callParkFilteredList.append(rowCPk)
                                        appended = True
                                if ((pd.isnull(rowCPk['Agent' + str(userNum) + ' ID']) == False) and (rowCPk['Agent' + str(userNum) + ' ID'] != rowUL['EMAIL ID'])):
                                    if rowCPk['Agent' + str(userNum) + ' ID'] not in agentNotInUserList:
                                        agentNotInUserList.append(rowCPk['Agent' + str(userNum) + ' ID'])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                    except:
                        print("Issue in creating  with filtered callParkBulk for header ", header)
        except: 
            print("Error in processing for createLocationFeatureFilteredList for Call Park Group: ", rowCPk['Call Park Name'])  
    # Warn if there agents which are not in UserList
    if agentNotInUserList:
        print("WARNING: You have in agents in Call parks but not in userList", agentNotInUserList) 

    # Create filtred CallParkGroup
    fileCPG = directory_path + '/CallParkGroup.csv'
    with open(fileCPG, 'w') as file3:
        writer = csv.writer(file3)
        writer.writerow(headers)
        writer.writerows(callParkFilteredList)

    ### Call Pickup Group ###
    callPickupList = []
    callPickupName = ""
    callPickup = {}
    appendCallPickup = False
    for rowCP in CallPickupGroup.iterrows():
        if (rowCP[1]['Feature Type'] == "CALL PICKUP GROUP"):
            if rowCP[1]['Config Name'] != callPickupName:
                callPickupName = rowCP[1]['Config Name']
                callPickup = {}
                callPickup['Name'] = rowCP[1]['Config Name']
                callPickup['Location'] = ""
                callPickup['Notification Type'] = ""
                callPickup['Notification Delay Timer In Seconds'] = ""
                callPickup['Agent Action'] = "ADD"
                userNum = 1
                if callPickupName:
                     appendCallPickup = True
                    
            if pd.isnull(rowCP[1]['Email ID']) == False:
                callPickup['Agent' + str(userNum) + ' ID'] = rowCP[1]['Email ID']
            elif pd.isnull(rowCP[1]['User']) == False:
                callPickup['Agent' + str(userNum) + ' ID'] = rowCP[1]['User']
            elif pd.isnull(rowCP[1]['Device']) == False:
                callPickup['Agent' + str(userNum) + ' ID'] = rowCP[1]['Device']
            else:
                callPickup['Agent' + str(userNum) + ' ID'] = rowCP[1]['Line']
            userNum = userNum + 1
            
        if (rowCP[1]['Feature Type'] == "CALL PICKUP GROUP") and callPickupName and appendCallPickup:
            callPickupList.append(callPickup)
    
    callPickupBulk = pd.DataFrame(callPickupList)
    callPickupBulk.fillna('', inplace=True)
    callPickupBulk = callPickupBulk.drop_duplicates()
    callPickupFilteredList = []
    userNotInUserList = []
    headers = list(callPickupBulk.columns)
    for indexCL, rowCPk in callPickupBulk.iterrows():
        try:
            print("Start filtering callParkBulk for user/device in Hunt Group " + rowCPk['Name'])
            for iindexUL, rowUL in userstomigrate.iterrows():
                # Creating filtered ConfiguredLineBulk
                userNum = 1
                appended = False
                for header in headers:
                    try: 
                        if 'Agent' in header:
                            try:
                                if ((pd.isnull(rowCPk['Agent' + str(userNum) + ' ID']) == False) and (rowCPk['Agent' + str(userNum) + ' ID'] == rowUL['EMAIL ID'])):
                                    if appended == False:
                                        rowCPk.fillna('', inplace=True)
                                        callPickupFilteredList.append(rowCPk)
                                        appended = True
                                if ((pd.isnull(rowCPk['Agent' + str(userNum) + ' ID']) == False) and (rowCPk['Agent' + str(userNum) + ' ID'] != rowUL['EMAIL ID'])):
                                    if rowCPk['Agent' + str(userNum) + ' ID'] not in agentNotInUserList:
                                        agentNotInUserList.append(rowCPk['Agent' + str(userNum) + ' ID'])
                                userNum = userNum + 1
                            except:
                                userNum = userNum + 1
                    except:
                        print("Issue in creating  with filtered callParkBulk for header ", header)
        except: 
            print("Error in processing for createLocationFeatureFilteredList for Call Pickup Group: ", rowCPk['Name'])  
    # Warn if there agents which are not in UserList
    if agentNotInUserList:
        print("WARNING: You have in agents in Call Pickup but not in userList", agentNotInUserList) 

    # Create filtred Call Pickup Group CSV
    fileCPU = directory_path + '/CallPickupGroup.csv'
    with open(fileCPU, 'w') as file4:
        writer = csv.writer(file4)
        writer.writerow(headers)
        writer.writerows(callPickupFilteredList)

def IdenfiyDNInMultipleDP(directory_path, DevicePool):

    ### Identify if DN exist in multiple device pool
    print("Inside IdenfiyDNInMultipleDP")
    devicePool = {}
    dnInDP = []
    headers = ["Directory Number", "Device Pool", "Device Pool"]
        
    for rowDP in DevicePool.iterrows():
        devicePool[rowDP[1][0].split(',')[0]] = rowDP[1][0].split(',')[1:]
    for key in devicePool.keys():
        
        for num in devicePool[key]:
            for numList in devicePool.keys():
                if (num in devicePool[numList]) and (numList != key):
                    dnInDP.append([num, key, numList])

    fileDNInMultipleDP = directory_path + '/DNInMultipleDevicePool.csv'
    with open(fileDNInMultipleDP, 'w') as file5:
        writer = csv.writer(file5)
        writer.writerow(headers)
        writer.writerows(dnInDP)
    print("Directory numbers which present in multiple Device Pools are listed in DNInMultipleDevicePool.csv ")

def VirtualLineDisplayUpdate(csvDir, ucmcsvDir, replace):
    print(ucmcsvDir)
    try:
        ucmPhone = []
        with open(ucmcsvDir + '/phone.csv', 'r') as file:
            csvreader = csv.reader(file)
            header = next(csvreader)
            for row in csvreader:
                ucmPhone.append(row)
        phone = pd.DataFrame(ucmPhone)
        phone.columns = header
    except:
        print("phone.csv is not present in csvdir, hence skipping.")
        return
    try:
        virtualLineBulk = []
        with open(csvDir + '/VirtualLineBulk.csv', 'r') as file:
            csvreader = csv.reader(file)
            header = next(csvreader)
            for row in csvreader:
                virtualLineBulk.append(row)
        virtualLine = pd.DataFrame(virtualLineBulk)
        virtualLine.columns = header
    except:
        print("VirtualLineBulk.csv is not present in csvdir, hence skipping")
        return

    headers = list(phone.columns)
    # Extension
    virtualLineDescription = []
    extensionAlreadyHandled = []
    for inxVL, rowVL in virtualLine.iterrows():
        if (pd.isnull(rowVL['Extension']) == False) and rowVL['Extension'] not in extensionAlreadyHandled:
        
            for header in headers:
                index = 1
                if (header == 'Directory Number ' + str(index)):
                    for idxPhrowPh, rowPh, in phone.iterrows():
                        
                        if (pd.isnull(rowPh['Directory Number ' + str(index)]) == False) and (rowPh['Directory Number ' + str(index)]) == rowVL['Extension']:
                            virtualLineWithDescriotion = {}
                            if (pd.isnull(rowPh['Alerting Name ' + str(index)]) == False):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['extension'] = rowVL['Extension']
                                virtualLineWithDescriotion['descriotion'] = rowPh['Alerting Name ' + str(index)]
                                
                                if rowVL['Extension'] not in extensionAlreadyHandled:
                                    virtualLineDescription.append(virtualLineWithDescriotion)
                            elif (pd.isnull(rowPh['ASCII Alerting Name ' + str(index)]) == False):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['extension'] = rowVL['Extension']
                                virtualLineWithDescriotion['descriotion'] = rowPh['ASCII Alerting Name ' + str(index)]
                                
                                if rowVL['Extension'] not in extensionAlreadyHandled:
                                    virtualLineDescription.append(virtualLineWithDescriotion)
                            elif (pd.isnull(rowPh['Line Description ' + str(index)]) == False):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['extension'] = rowVL['Extension']
                                virtualLineWithDescriotion['descriotion'] = rowPh['Line Description ' + str(index)]
                                
                                if rowVL['Extension'] not in extensionAlreadyHandled:
                                    virtualLineDescription.append(virtualLineWithDescriotion)
                            elif (pd.isnull(rowPh['Display ' + str(index)]) == False):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['extension'] = rowVL['Extension']
                                virtualLineWithDescriotion['descriotion'] = rowPh['Line Description ' + str(index)]
                                
                                if rowVL['Extension'] not in extensionAlreadyHandled:
                                    virtualLineDescription.append(virtualLineWithDescriotion)
                            elif (pd.isnull(rowPh['ASCII Display ' + str(index)]) == False):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['extension'] = rowVL['Extension']
                                virtualLineWithDescriotion['descriotion'] = rowPh['Line Description ' + str(index)]
                                
                                if rowVL['Extension'] not in extensionAlreadyHandled:
                                    virtualLineDescription.append(virtualLineWithDescriotion)
                            
                            if rowVL['Extension'] not in extensionAlreadyHandled:
                                extensionAlreadyHandled.append(rowVL['Extension'])
        
                        if (header == 'Directory Number ' + str(index)):
                            index = index + 1
    
    description = []
    for inxVL, rowVL in virtualLine.iterrows():
        descriptionFound = False
        for vl in virtualLineDescription:
            
            if (pd.isnull(rowVL['Extension']) == False) and vl['extension'] == rowVL['Extension']:
                description.append(vl['descriotion'])
                descriptionFound = True
        if descriptionFound == False:
            description.append('')
    
    virtualLine['Description (Extension)'] = description

    # Phone number
    virtualLinePhoneNumberDescription = []
    phoneNumberAlreadyHandled = []
    for inxVL, rowVL in virtualLine.iterrows():
        
        if (pd.isnull(rowVL['Phone Number']) == False) and (rowVL['Phone Number'] not in phoneNumberAlreadyHandled):
            for header in headers:
                index = 1
                if (header == 'Directory Number ' + str(index)):
                    for idxPhrowPh, rowPh, in phone.iterrows():
                        if (pd.isnull(rowPh['Directory Number ' + str(index)]) == False) and ((rowPh['Directory Number ' + str(index)]) == rowVL['Phone Number'] \
                                or ('+' + str(rowPh['Directory Number ' + str(index)])) == rowVL['Phone Number']) or (rowPh['Directory Number ' + str(index)]) == ('+' + str(rowVL['Phone Number'])):
                            virtualLineWithDescriotion = {}
                            if (pd.isnull(rowPh['Alerting Name ' + str(index)]) == False) and ((rowPh['Alerting Name ' + str(index)]) != ""):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['Phone Number'] = rowVL['Phone Number']
                                virtualLineWithDescriotion['descriotion'] = rowPh['Alerting Name ' + str(index)]
                                if rowVL['Phone Number'] not in phoneNumberAlreadyHandled:
                                    virtualLinePhoneNumberDescription.append(virtualLineWithDescriotion)
                            elif (pd.isnull(rowPh['ASCII Alerting Name ' + str(index)]) == False) and (rowPh['ASCII Alerting Name ' + str(index)] != ""):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['Phone Number'] = rowVL['Phone Number']
                                virtualLineWithDescriotion['descriotion'] = rowPh['ASCII Alerting Name ' + str(index)]
                                if rowVL['Phone Number'] not in phoneNumberAlreadyHandled:
                                    virtualLinePhoneNumberDescription.append(virtualLineWithDescriotion)
                            elif (pd.isnull(rowPh['Line Description ' + str(index)]) == False) and (rowPh['Line Description ' + str(index)] != ""):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['Phone Number'] = rowVL['Phone Number']
                                virtualLineWithDescriotion['descriotion'] = rowPh['Line Description ' + str(index)]
                                if rowVL['Phone Number'] not in phoneNumberAlreadyHandled:
                                    virtualLinePhoneNumberDescription.append(virtualLineWithDescriotion)
                            elif (pd.isnull(rowPh['Display ' + str(index)]) == False) and (rowPh['Display ' + str(index)] != ""):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['Phone Number'] = rowVL['Phone Number']
                                virtualLineWithDescriotion['descriotion'] = rowPh['Line Description ' + str(index)]
                                if rowVL['Phone Number'] not in phoneNumberAlreadyHandled:
                                    virtualLineDescription.append(virtualLineWithDescriotion)
                            elif (pd.isnull(rowPh['ASCII Display ' + str(index)]) == False) and (rowPh['ASCII Display ' + str(index)] != ""):
                                virtualLineWithDescriotion['index'] = inxVL
                                virtualLineWithDescriotion['Phone Number'] = rowVL['Phone Number']
                                virtualLineWithDescriotion['descriotion'] = rowPh['Line Description ' + str(index)]
                                if rowVL['Phone Number'] not in phoneNumberAlreadyHandled:
                                    virtualLinePhoneNumberDescription.append(virtualLineWithDescriotion)
                            
                            if rowVL['Phone Number'] not in phoneNumberAlreadyHandled:
                                phoneNumberAlreadyHandled.append(rowVL['Phone Number'])
        
                        if (header == 'Directory Number ' + str(index)):
                            index = index + 1

    description = []
    for inxVL, rowVL in virtualLine.iterrows():
        descriptionFound = False
        for vl in virtualLinePhoneNumberDescription:
            
            if (pd.isnull(rowVL['Phone Number']) == False) and vl['Phone Number'] == rowVL['Phone Number']:
                description.append(vl['descriotion'])
                descriptionFound = True
        if descriptionFound == False:
            description.append('')
    
    virtualLine['Description (Phone Number)'] = description

    replacesVirtualLine = []
    handleDuplicatePhoneNumber = []
    handleDuplicateExtension = []
    if replace:
        for inxVL, rowVL in virtualLine.iterrows():
            vlElem = {}
            vlElem['First Name'] = rowVL['First Name']
            vlElem['Last Name'] = rowVL['Last Name']
            vlElem['Display Name'] = rowVL['Display Name']

            # Overwrite First Name, Last Name and Display Name with from Alerting name n, ASCII Alerting name n or Line Description 1 or 
            # Display n or ASCII Display n, from phone.csv
            if (pd.isnull(rowVL['Description (Phone Number)']) == False) and (rowVL['Description (Phone Number)'] != ""):

                if rowVL['Phone Number'] in handleDuplicatePhoneNumber:
                    continue
                else:
                    handleDuplicatePhoneNumber.append(rowVL['Phone Number'])

                name = rowVL['Description (Phone Number)'].split(' ')
                vlElem['First Name'] = name[0]
                index = 1
                vlElem['Last Name'] = ""
                while index < len(name):
                    vlElem['Last Name'] = vlElem['Last Name'] + name[index]
                    index = index + 1
                vlElem['Display Name'] = rowVL['Description (Phone Number)']

            elif (pd.isnull(rowVL['Description (Extension)']) == False) and (rowVL['Description (Extension)'] != ""):

                if rowVL['Extension'] in handleDuplicateExtension:
                    continue
                else:
                    handleDuplicateExtension.append(rowVL['Extension'])

                name = rowVL['Description (Extension)'].split(' ')
                vlElem['First Name'] = name[0]
                index = 1
                vlElem['Last Name'] = ""
                while index < len(name):
                    vlElem['Last Name'] = vlElem['Last Name'] + name[index]
                    index = index + 1
                vlElem['Display Name'] = rowVL['Description (Extension)']
            
            vlElem['Location'] = rowVL['Location']
            vlElem['Phone Number'] = rowVL['Phone Number']
            vlElem['Extension'] = rowVL['Extension']

            replacesVirtualLine.append(vlElem)

        virtualLine = pd.DataFrame(replacesVirtualLine)

    VirtualLineWithDescriptionDir = csvDir + "/VirtualLineWithDescription"
    
    if replace:
        # Copy VirtualLineBulk.csv before replacing it
        source_file = csvDir + '/VirtualLineBulk.csv'
        destination_file = csvDir + '/ORIGINAL_VirtualLineBulk.csv'

        try:
            shutil.copyfile(source_file, destination_file)
            os.remove(csvDir + '/VirtualLineBulk.csv')
        except FileNotFoundError:
            print(f"Error: Source file '{source_file}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        virtualLine.to_csv(csvDir + '/VirtualLineBulk.csv', index=False)
    else:
        if not os.path.exists(VirtualLineWithDescriptionDir):
            os.mkdir(VirtualLineWithDescriptionDir)
        else:
            try:
                shutil.rmtree(VirtualLineWithDescriptionDir)
                os.mkdir(VirtualLineWithDescriptionDir)
            except OSError as e:
                print("Clould not create ", VirtualLineWithDescriptionDir)
        virtualLine.to_csv(VirtualLineWithDescriptionDir + '/VirtualLineBulk.csv', index=False)

def BulkProvision(csvDir, orgid, auth):
    print("Inside BulkProvision", csvDir, orgid, auth)

def main():

    csvDir = "" 
    userList = ""
    insightDir = ""
    setExternalMailbox = False
    groups = ""
    replace = False
    
    # total arguments
    n = len(sys.argv)
    print("Total arguments passed:", n - 1)

    if n == 1:
        print("Usage for identifying UCM Directory numbers which are in multiple device pools: " + '\n' + "./UserBasedUCMFeatureMigration.py DNInMultipleDP insightDir=(see below)" + '\n')
        print("Usage for updating VirtualLineBulk.csv (please see below description for replacevirtualline for details): " + '\n' + "./UserBasedUCMFeatureMigration.py virtuallinedisplayupdate csvDir=(see below) replacevirtualline=(see below) ucmcsvDir=(see below) " + '\n')
        print("Usage for user list based filtering: " + '\n' + "./UserBasedUCMFeatureMigration.py csvDir=(see below) userList=(see below) insightDir=(see below) setExternalMailbox=True groups=all replacevirtualline=true/false ucmcsvDir=(see below) " + '\n')
        print("Parameters used in above 3 usage:")
        print("DNInmultipleDP -> Option for identify Directory numbers which present in multiple Device Pools and list in DNInMultipleDevicePool.csv in insightDir" + '\n')
        print("csvDir=<Path to directory where UCM Feature Migration tool output .zip is unziped>. Filtered data will be created under Filtered directory here."+ '\n')
        print("userList=<UserList file (same format as used in UCM migration tool) with path. Use EMAIL ID (not CUCM USER ID) and you can add Location column to overide user/device location." + '\n')
        print("insightDir=<Path to directory where UCM Migration Insight tool output .zip is unziped>. This is needed for Call Park and Pickup group WxC CSVs needs to be creeated from Migration Insight output" + '\n')
        print("setExternalMailbox=True if user's External Mailbox is set to user's email, otherwise don't include this option." + '\n')
        print("groups=all to create all filtered data under All_CUSTOM_DevicePool. If this option not included then filtered data will be under direcory based on custom device pool name." + '\n')
        print("replacevirtualline=true/false. True/true - script will replace VirtualLineBulk.csv (keep the original file as ORIGINAL_VirtualLineBulk.csv) in with updated First name, Last name, Display name from Alerting name n, ASCII Alerting name n or Line Description 1 or Display n or ASCII Display n, from phone.csv (need to be there in ucmcsvDir) file. False/false - create VirtualLineBulk.csv  in a new subfolder VirtualLineWithDescription with description." + '\n')
        print("ucmcsvDir=<Path to directory where UCM tar file is un-tared>. This is only needed if replacevirtualline option is selected." + '\n')
        print('\n' + "This tool provide 5 main functionality: " + '\n')
        print('1) User list based filtering of output from "Migrate features from UCM" tool. Filtered data will be created under <csvDir>/Filtered directory.')
        print('2) Identify users which are part of group features but not present in provided User list')
        print('3) Create Call park and Call Pickup group WxC CSV files which currently "Migrate features from UCM" tool doesnt generate')
        print('4) Identify Directory numbers which present in multiple Device Pools and list in DNInMultipleDevicePool.csv in insightDir')
        print('5) Update VirtualLineBulk.csv with Description / First name, Last name, Display name from Alerting name n, ASCII Alerting name n or Line Description 1 or Display n or ASCII Display n, from phone.csv (need to be placed in csvdir)' + '\n')
        exit()  

    # Arguments passed
    print("\nName of Python script:", sys.argv[0])
    print("Argument passed are:")

    if len(sys.argv) == 3 and sys.argv[1] == "DNInMultipleDP":
        print("DNInMultipleDP")
        print(sys.argv[2] + '\n')
        insightDir = ""
        param = sys.argv[2].split("=")
        if param[0] == "insightDir":
            insightDir = param[1]
        DevicePool = pd.read_csv(insightDir + '/DevicePoolNumbers.txt', sep='\r', header=None)
        IdenfiyDNInMultipleDP(insightDir, DevicePool)
        exit()

    if len(sys.argv) == 5 and sys.argv[1] == "virtuallinedisplayupdate":
        print("virtuallinedisplayupdate")
        print(sys.argv[2])
        print(sys.argv[3])
        print(sys.argv[4] + '\n')
        csvDir = ""
        param = sys.argv[2].split("=")
        if param[0] == "csvDir":
            csvDir = param[1]
        param = sys.argv[3].split("=")
        if param[0] == "replacevirtualline":
            if param[1] == 'true' or param[1] == 'True':
                replace = True
            else:
                replace = False
        ucmcsvDir = ""
        param = sys.argv[4].split("=")
        if param[0] == "ucmcsvDir":
            ucmcsvDir = param[1]
        VirtualLineDisplayUpdate(csvDir, ucmcsvDir, replace)
        exit()

    if len(sys.argv) == 5 and sys.argv[1] == "bulkprovision":
        print("bulkprovision")
        print(sys.argv[2])
        print(sys.argv[3])
        print(sys.argv[4])
        csvDir = ""
        param = sys.argv[2].split("=")
        if param[0] == "csvDir":
            csvDir = param[1]
        param = sys.argv[3].split("=")
        if param[0] == "orgid":
            orgid = param[1]
        param = sys.argv[4].split("=")
        if param[0] == "auth":
            auth = param[1]
        BulkProvision(csvDir, orgid, auth)
        exit()

    for i in range(1, n):
        param = sys.argv[i].split("=")
        print(param[0] + " = " + param[1])
        if param[0] == "csvDir":
            csvDir = param[1]
        if param[0] == "userList":
            userList = param[1]
        if param[0] == "insightDir":
            insightDir = param[1]
        if param[0] == "setExternalMailbox":
            if param[1] == "False" or param[1] == "false":
                pass
            elif param[1] == "True" or param[1] == "true":
                setExternalMailbox = True
        if param[0] == "groups":
            groups = "all"
        if param[0] == "replacevirtualline":
            if param[1] == 'true' or param[1] == 'True':
                replace = True
            else:
                replace = False
        ucmcsvDir = ""
        if param[0] == "ucmcsvDir":
            ucmcsvDir = param[1]
            VirtualLineDisplayUpdate(csvDir, ucmcsvDir, replace)

    print('\n')
    
    print("Start Processing .... ") 
    ''' Read User List CSV '''
    
    userstomigrate = pd.read_csv(userList)
    userstomigrate = userstomigrate.drop_duplicates()

    ''' Read WxC CSV files output from UCM Feature Migration tool '''
    callForward_Internal = pd.read_csv(csvDir + '/UserFeatures_Internal.csv', low_memory=False)
    callForward_Internal = callForward_Internal.replace({True: 'TRUE', False: 'FALSE'})

    callForward_External = pd.read_csv(csvDir + '/UserFeatures_External.csv', low_memory=False)
    callForward_External = callForward_External.replace({True: 'TRUE', False: 'FALSE'})

    configuredLineBulk = pd.read_csv(csvDir + '/ConfiguredLineBulk.csv', low_memory=False)
    configuredLineBulk = configuredLineBulk.replace({True: 'TRUE', False: 'FALSE'})

    HuntGroupBulk = pd.read_csv(csvDir + '/HuntGroupBulk.csv', low_memory=False)
    HuntGroupBulk = HuntGroupBulk.replace({True: 'TRUE', False: 'FALSE'})

    CallQueueBulk = pd.read_csv(csvDir + '/CallQueueBulk.csv', low_memory=False)
    CallQueueBulk = CallQueueBulk.replace({True: 'TRUE', False: 'FALSE'})

    AutoAttendantBulk = pd.read_csv(csvDir + '/AutoAttendantBulk.csv', low_memory=False)
    AutoAttendantBulk = AutoAttendantBulk.replace({True: 'TRUE', False: 'FALSE'})
    
    ''' Read  CSV files output from UCM Migration Insight tool '''
    CallParkGroup = pd.read_csv(insightDir + '/HuntGroup_CallQueue_CallPark_CallPickUpGroups.csv', low_memory=False)
    CallParkGroup = CallParkGroup.replace({True: 'TRUE', False: 'FALSE'})

    CallPickupGroup = pd.read_csv(insightDir + '/HuntGroup_CallQueue_CallPark_CallPickUpGroups.csv', low_memory=False)
    CallPickupGroup = CallPickupGroup.replace({True: 'TRUE', False: 'FALSE'})

    SharedLineGroup = pd.read_csv(insightDir + '/shared_line_Group_migration_report.csv', low_memory=False)
    SharedLineGroup = SharedLineGroup.replace({True: 'TRUE', False: 'FALSE'})

    # Read deviceLineKeyConfiguration and convert into Dataframe
    deviceLineKey = []
    with open(csvDir + '/DeviceLineKeyConfigurationBulk.csv', 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            deviceLineKey.append(row)
    deviceLineKeyConfiguration = pd.DataFrame(deviceLineKey)
    deviceLineKeyConfiguration.columns = header

    # Read deviceLineKeyConfiguration and convert into Dataframe
    virtualLine = []
    with open(csvDir + '/VirtualLineBulk.csv', 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            virtualLine.append(row)
    virtualLineBulk = pd.DataFrame(virtualLine)
    virtualLineBulk.columns = header

    # Define the path for the new directory
    base_directory_path = csvDir + "/Filtered"

    # Create the directory
    # Check if the directory already exists
    if not os.path.exists(base_directory_path):
        os.mkdir(base_directory_path)
    else:
        try:
            shutil.rmtree(base_directory_path)
            os.mkdir(base_directory_path)
        except OSError as e:
            print(f"Error: {base_directory_path} : {e.strerror}")

    # Create directory based on Custom Device Pool and create WxC CSVs based users/devices for each custom device pool separately
    if groups == "":
        elems = userstomigrate['CUSTOM DEVICE POOL'].drop_duplicates()
        grouped = userstomigrate.groupby('CUSTOM DEVICE POOL')
        for elem in elems:
            print("---------------------------------------")
            print("Going to process for Custom device pool =", elem)
            custom_dp_grouped = grouped.get_group(elem)
            directory_path = base_directory_path + "/" + elem
            directory_path = directory_path.strip()
            
            if not os.path.exists(directory_path):
                os.mkdir(directory_path)
            else:
                pass

            ''' Generate filtered WxC CSVs based on User List '''
            createUserDeviceVirtuallineFilteredList(directory_path, custom_dp_grouped, virtualLineBulk, configuredLineBulk, deviceLineKeyConfiguration, callForward_Internal, callForward_External, setExternalMailbox, elem)
            createLocationFeatureFilteredList(directory_path, custom_dp_grouped, HuntGroupBulk, CallQueueBulk, AutoAttendantBulk, CallParkGroup, CallPickupGroup, SharedLineGroup, elem)
            createREADME(directory_path)

    # Create "All" directory inside "Filtered" and create WxC CSVs based on user list
    if groups == "all":
        print("---------------------------------------")
        print("Going to process for all custom device pools under All_CUSTOM_DevicePool")
        directory_path = csvDir + "/Filtered/All_CUSTOM_DevicePool"
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
        else:
            pass
        elem = "all"
        createUserDeviceVirtuallineFilteredList(directory_path, userstomigrate, virtualLineBulk, configuredLineBulk, deviceLineKeyConfiguration, callForward_Internal, callForward_External, setExternalMailbox, elem)
        createLocationFeatureFilteredList(directory_path, userstomigrate, HuntGroupBulk, CallQueueBulk, AutoAttendantBulk, CallParkGroup, CallPickupGroup, SharedLineGroup, elem)
        createREADME(directory_path)

# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 
    
