import re
import csv
import pandas as pd
import os

avaya_grougpage = []
avaya_pickupgroug = []
avaya_stations = []
avaya_answercoverage = []
avaya_processAbbreviateddial = []
avaya_huntgroup = []
avaya_huntgroupnumber = []

def processLocation(content, directory_path, raw_data_path):
    try:
        print("In processLocation")
        avaya_locations = []
        lines = content.splitlines()
        for line in lines:
            loc = {}
            if line[0].isdigit():
                elem = line.split()
                #print(elem)
                idx = -1
                try:
                    if elem.index('+'):
                        idx = elem.index('+')
                        #print(elem[idx])
                except:
                    pass
                try: 
                    if elem.index('-'):
                        idx = elem.index('-')
                        #print(elem[idx])
                except:
                    pass
                if idx != -1:
                    loc['Location Name'] = " ".join(elem[1:idx])
                    loc['Timezone Offset'] = "".join(elem[idx:idx + 2])
                    #print(elem[idx + 3])
                    if elem[idx + 3].startswith('*') or elem[idx + 3].startswith('#') or elem[idx + 3].isdigit():
                        loc['City/Area'] = ""
                    else:
                        loc['City/Area'] = elem[idx + 3]
                
            if loc:
                avaya_locations.append(loc)      

        # Write to a file
        pd.DataFrame(avaya_locations).to_csv(raw_data_path + '/avaya_location.csv', index=False)
        
    except:
        print("Error in processing location")
    

def processStation(content, directory_path, raw_data_path):
    try:
        print("In processStation")
        extensions = content.split("Extension:")

        for data in extensions:
            
            station = {}
            data = "Extension:" + data
            lines = data.splitlines()
            startButtonProcessing = False
            buttonPrefix = ""
            for line in lines:
                #print("LLLL", line)
                line = line.replace("STATION OPTIONS", "")
                line = line.replace("FEATURE OPTIONS", "")
                line = line.replace("ENHANCED CALL FORWARDING", "")
                line = line.replace("Forwarded Destination", "")
                line = line.replace("Active", "")
                line = line.replace("SITE DATA", "")
                line = line.replace("ABBREVIATED DIALING", "")
                line = line.replace("HOT LINE DESTINATION", "")
                line = line.replace("?", ":")
                line = line.replace(": ", ":")
                #print(line)
                if "Voice System name:" in line:
                    continue
                
                if startButtonProcessing == False and "BUTTON ASSIGNMENTS" in line or "BUTTON MODULE" in line:
                    #print(line.strip())
                    buttonPrefix = line.strip()
                    startButtonProcessing = True

                name = ""
                if "Name" in line and "Unicode Name" not in line:
                    name = line.split("Coverage")[0].strip()
                    name = name.split(":")[1]
                    #print("MMMM", name)
                    
                elems = line.split()
                temp = []
                for elem in elems:
                    if startButtonProcessing == True:
                        continue
                    if ":" in elem and not temp:
                        if "Name" in line and "Unicode Name" not in line:
                            station["Name"] = name
                        else: 
                            keyval = elem.split(":")
                            station[keyval[0]] = keyval[1]
                    if ":" not in elem:
                        temp.append(elem)
                    else:
                        if temp and startButtonProcessing == False:
                            elem = " ".join(temp) + " " + elem
                            #print(elem)
                            keyval = elem.split(":")
                            if "Coverage Path 2" in keyval[0]:
                                station["Coverage Path 2"] = keyval[1]
                            else:
                                station[keyval[0]] = keyval[1]
                            temp = []

                if startButtonProcessing == True and buttonPrefix == "BUTTON ASSIGNMENTS": 
                    if line[0].isdigit() or line[1].isdigit():
                        buttonContent = []
                        elems = line.split()
                        index = 0
                        
                        for elem in elems[index:]:
                            startCollectionIdx = index
                            buttonelems = elem.split(":")
                            if buttonelems[0].isdigit():
                                buttonContent.append(buttonelems[1])
                                for content in elems[startCollectionIdx+1:]:
                                    if not content[0].isdigit():
                                        buttonContent.append(content)
                                        startCollectionIdx = startCollectionIdx + 1
                                    else:
                                        break
                                
                                station[buttonPrefix + " " + buttonelems[0]] = " ".join(buttonContent)
                                buttonContent = []
                        
                            index = index + 1

                if line and startButtonProcessing == True and buttonPrefix == "BUTTON MODULE #1 ASSIGNMENTS" or buttonPrefix == "BUTTON MODULE #2 ASSIGNMENTS":
                    #print("Button Module", buttonPrefix, line)
                    if line[0].isdigit() or line[1].isdigit():
                        if "1:" in line and "13:" in line:
                            #print(line.split("13:"))
                            elems = line.split("13:")[0].strip()
                            #print(elems.split(":")[1])
                            #print(" ".join(elems.split(":"))[1:].strip())
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(1)] = " ".join(elems.split(":"))[1:].strip()
                                #print(" ".join(elems.split(":")))
                            else:
                                station[buttonPrefix + " " + str(1)] = ""
                            if line.split("13:")[1].strip():
                                #print(line.split("13:")[1].strip())
                                station[buttonPrefix + " " + str(13)] = line.split("13:")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(13)] = ""
                        if "2:" in line and "14:" in line:
                            #print(line.split("14:"))
                            elems = line.split("14:")[0].strip()
                            #print(elems.split(":")[1])
                            #print(" ".join(elems.split(":"))[1:].strip())
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(2)] = " ".join(elems.split(":"))[1:].strip()
                                #print(" ".join(elems.split(":")))
                            else:
                                station[buttonPrefix + " " + str(2)] = ""
                            if line.split("14:")[1].strip():
                                #print(line.split("13:")[1].strip())
                                station[buttonPrefix + " " + str(14)] = line.split("14:")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(14)] = ""
                        if "3:" in line and "15:" in line:
                            elems = line.split("15:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(3)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(3)] = ""
                            if line.split("15:")[1].strip():
                                station[buttonPrefix + " " + str(15)] = line.split("15")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(15)] = ""
                        if "4:" in line and "16:" in line:
                            elems = line.split("16:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(4)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(4)] = ""
                            if line.split("16:")[1].strip():
                                station[buttonPrefix + " " + str(16)] = line.split("16")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(16)] = ""
                        if "5:" in line and "17:" in line:
                            elems = line.split("17:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(5)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(5)] = ""
                            if line.split("17:")[1].strip():
                                station[buttonPrefix + " " + str(17)] = line.split("17")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(17)] = ""
                        if "6:" in line and "18:" in line:
                            elems = line.split("17:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(6)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(6)] = ""
                            if line.split("18:")[1].strip():
                                station[buttonPrefix + " " + str(18)] = line.split("18")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(18)] = ""
                        if "7:" in line and "19:" in line:
                            elems = line.split("219:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(7)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(7)] = ""
                            if line.split("19:")[1].strip():
                                station[buttonPrefix + " " + str(19)] = line.split("19")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(19)] = ""
                        if "8:" in line and "20:" in line:
                            elems = line.split("20:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(8)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(8)] = ""
                            if line.split("20:")[1].strip():
                                station[buttonPrefix + " " + str(20)] = line.split("20")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(20)] = ""
                        if "9:" in line and "21:" in line:
                            elems = line.split("21:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(9)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(9)] = ""
                            if line.split("21:")[1].strip():
                                station[buttonPrefix + " " + str(21)] = line.split("21")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(21)] = ""
                        if "10:" in line and "22:" in line:
                            elems = line.split("22:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(10)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(10)] = ""
                            if line.split("22:")[1].strip():
                                station[buttonPrefix + " " + str(22)] = line.split("22")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(22)] = ""
                        if "11:" in line and "23:" in line:
                            elems = line.split("23:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(11)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(11)] = ""
                            if line.split("23:")[1].strip():
                                station[buttonPrefix + " " + str(23)] = line.split("23")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(23)] = ""
                        if "12:" in line and "24:" in line:
                            elems = line.split("24:")[0].strip()
                            if elems.split(":")[1]:
                                station[buttonPrefix + " " + str(12)] = " ".join(elems.split(":"))[1:].strip()
                            else:
                                station[buttonPrefix + " " + str(12)] = ""
                            if line.split("24:")[1].strip():
                                station[buttonPrefix + " " + str(24)] = line.split("24")[1].strip()
                            else:
                                station[buttonPrefix + " " + str(24)] = ""
                            buttonPrefix = ""

            if station:
                avaya_stations.append(station)

        # Write to a file
        pd.DataFrame(avaya_stations).to_csv(raw_data_path + '/avaya_station.csv', index=False)

    except:
        print("Error in processing station")

# Process Avaya Hunt Group and Call Queue
def processHuntgroupCallQeuue(content, directory_path, raw_data_path, agents):
    try:
        print("In processHuntgroup")
        lines = content.splitlines()
        firstLine = True
        huntgroups = []
        hgLine = []
        for line in lines:
            #print(line)
            
            if firstLine == True and line[0].isdigit():
                elems = line.split()
                hgLine.append(elems[0])
                #print(hgLine)
                name = ""
                index = 0
                for elem in elems:
                    if index == 0:
                        index = index + 1
                    else:
                        name = "".join(name) + " " + elem
                if name:
                    name = name.strip()
                    hgLine.append(name)
                firstLine = False
                #print("Ist line", elems, hgLine)
            elif firstLine == False:
                elems = line.split()
                firstLine = True
                #print("2nd Line", elems)
                hgLine = hgLine + elems
                #print("Combined line", hgLine)
                huntgroups.append(hgLine)
                hgLine = []

        for hg in huntgroups:
            huntgroup = {}
            #print(hg)
            # Store hunt group number in 
            avaya_huntgroupnumber.append(hg[0])
            # Populate huntgroup dict
            huntgroup['Group Number'] = hg[0]
            huntgroup['Group Name'] = hg[1] 
            huntgroup['Extension'] = hg[2].replace("-","") 
            huntgroup['Group Type'] = hg[3] 
            acd = hg[4].split('/')
            huntgroup['ACD'] = acd[0] 
            if acd[1] == "-":
                huntgroup['MEAS'] = ""
            else:
                huntgroup['MEAS'] = acd[1]
            huntgroup['Vector'] = hg[5]
            huntgroup['MCH'] = hg[6] 
            huntgroup['Queue'] = hg[7] 
            huntgroup['No. Mem'] = hg[8] 
            if hg[9].isdigit():
                huntgroup['Coverage Path'] = hg[9]
                huntgroup['Notify/CTG Adj'] = hg[10]
                if hg[11].isdigit():
                    huntgroup['Dom Crtl'] = hg[11]  
                    huntgroup['Message Center'] = hg[12]
                else:
                    huntgroup['Dom Crtl'] = ""
                    huntgroup['Message Center'] = hg[11] 
            else:
                huntgroup['Coverage Path'] = ""
                huntgroup['Notify/CTG Adj'] = hg[9]
                if hg[10].isdigit():
                    huntgroup['Dom Crtl'] = hg[10]  
                    huntgroup['Message Center'] = hg[11]
                else:
                    huntgroup['Dom Crtl'] = ""
                    huntgroup['Message Center'] = hg[10]

            avaya_huntgroup.append(huntgroup)

        # Process Agents
        huntgroupwithagents = {}
        try:
            # Initialize huntgroupwithagents
            for elem in avaya_huntgroupnumber:
                huntgroupwithagents[elem] = []

            lines = agents.splitlines()
            for line in lines:
                elems = line.split()
                agent = {}
                if elems[3].isdigit():
                    #print(elems[2])
                    agent['name'] = elems[2]
                else:
                    #print(elems[2] + elems[3])
                    agent['name'] = elems[2] + " " + elems[3]
                
                if elems[5] == "lvl":
                    agent['skill'] = elems[4]
                elif elems[4] == "lvl":
                    agent['skill'] = elems[3]
                elif elems[6] == "lvl":
                    agent['skill'] = elems[5]
                elif elems[7] == "lvl":
                    agent['skill'] = elems[6]

                #print(agent)
                for elem in elems:
                    if elem in avaya_huntgroupnumber:
                        #print(elem)
                        huntgroupwithagents[elem].append(agent)

            #print(huntgroupwithagents.keys())
            for key in huntgroupwithagents.keys():
                if huntgroupwithagents[key]:
                    #print(key, huntgroupwithagents[key])
                    for elem in avaya_huntgroup:
                        if elem['Group Number'] == key:
                            index = 0
                            for agent in huntgroupwithagents[key]:
                                try:
                                    elem['Agent ' + str(index + 1)] = agent['name']
                                    elem['Skil ' + str(index + 1)] = agent['skill']
                                except:
                                    pass
                                #print(key, name)
                                index = index + 1 
        except:
            print("Error in processHuntgroupagents")

        # Device data into Huntgroup and Call Queue
        huntgroup = []
        callqueue = []
        avaya_callqueue = avaya_huntgroup
        index = 0
        for row in avaya_huntgroup:
            if row['Queue'] != 'y':
                huntgroup.append(row)
            index = index + 1
        index = 0
        for row in avaya_callqueue:
            if row['Queue'] != 'n':
                callqueue.append(row)
            index = index + 1
        
        # Write to a file
        pd.DataFrame(callqueue).to_csv(raw_data_path + '/avaya_callqueue.csv', index=False)
        pd.DataFrame(huntgroup).to_csv(raw_data_path + '/avaya_huntgroup.csv', index=False)
    except:
        print("Error in processing Huntgroup")

def processGrouppage(content, directory_path, raw_data_path):
    try:
        print("In processGroupPage")
        lines = content.splitlines()
        extAndName = []
        extensionSet = False
        nameSet = False
        gp = {}
        for line in lines:
            if "Group Name:" in line and nameSet == False:
                #print("Name: ", line.split(":")[1].strip().split("ASAI?")[0].strip())
                gp['Group Name'] = line.split(":")[1].strip().split("ASAI?")[0].strip()
                nameSet = True
            elif line[0].isdigit() or line[1].isdigit() or line[2].isdigit():
                elems = line.split()
                for elem in elems:
                    if ":" in elem and extensionSet == False:
                        extensionSet = True
                    elif extensionSet == True and elem != "n" and ":" not in elem:
                        extname = {}
                        extname['Extension'] = elem
                        extensionSet = False
                        #print("Extension", elem)
                        for station in avaya_stations:
                            if elem == station['Extension']:
                                #print(station['Name'])
                                extname['Name'] = station['Name']

                        extAndName.append(extname)

        
        index = 1
        for ext in extAndName:
            try:
                gp['Extension ' + str(index)] = ext['Extension']
                gp['Name ' + str(index)] = extname['Name']
            except:
                pass
            index = index + 1
        
        avaya_grougpage.append(gp)

        # Write to a file
        pd.DataFrame(avaya_grougpage).to_csv(raw_data_path + '/avaya_grouppage.csv', index=False)

    except:
        print("Error in processing Group page")

def processPickupgroup(content, directory_path, raw_data_path):
    try:
        print("In processPickupgroup")
        lines = content.splitlines()
        extAndName = []
        extensionSet = False
        nameSet = False
        pug = {}
        for line in lines:
            #print(line)
            if "Group Name:" in line and nameSet == False:
                #print("Name: ", line.split(":")[1].strip())
                pug['Group Name'] = line.split(":")[1].strip()
                nameSet = True
            elif line[0].isdigit() or line[1].isdigit():
                elems = line.split()
                for elem in elems:
                    if ":" in elem and extensionSet == False:
                        extensionSet = True
                    elif extensionSet == True and elem != " " and ":" not in elem:
                        extname = {}
                        extname['Extension'] = elem
                        extensionSet = False
                        #print("Extension", elem)
                        for station in avaya_stations:
                            if elem == station['Extension']:
                                #print(station['Name'])
                                extname['Name'] = station['Name']

                        extAndName.append(extname)
        
        index = 1
        for ext in extAndName:
            try:
                pug['Extension ' + str(index)] = ext['Extension']
                pug['Name ' + str(index)] = extname['Name']
            except:
                pass
            index = index + 1
        
        avaya_pickupgroug.append(pug)
            
        # Write to a file
        pd.DataFrame(avaya_pickupgroug).to_csv(raw_data_path + '/avaya_pickupgroup.csv', index=False)

    except:
        print("Error in processing Pickup group")

def processCoverageAnswergroup(content, directory_path, raw_data_path):
    try:
        print("In coverageAnswergroup")
        lines = content.splitlines()
        extAndName = []
        extensionSet = False
        nameSet = False
        cag = {}
        for line in lines:
            #print(line)
            if "Group Name:" in line and nameSet == False:
                #print("Name: ", line.split(":")[1].strip())
                cag['Group Name'] = line.split(":")[1].strip()
                nameSet = True
            elif line[0].isdigit() or line[1].isdigit():
                elems = line.split()
                for elem in elems:
                    if ":" in elem and extensionSet == False:
                        extensionSet = True
                    elif extensionSet == True and elem != " " and ":" not in elem:
                        extname = {}
                        extname['Extension'] = elem
                        extensionSet = False
                        #print("Extension", elem)
                        for station in avaya_stations:
                            if elem == station['Extension']:
                                #print(station['Name'])
                                extname['Name'] = station['Name']

                        extAndName.append(extname)
        
        index = 1
        for ext in extAndName:
            try:
                cag['Extension ' + str(index)] = ext['Extension']
                cag['Name ' + str(index)] = extname['Name']
            except:
                pass
            index = index + 1
        
        avaya_answercoverage.append(cag)
            
        # Write to a file
        pd.DataFrame(avaya_answercoverage).to_csv(raw_data_path + '/avaya_coverageanswergroup.csv', index=False)

    except:
        print("Error in processing coverage Answer group")

def processAbbreviateddial(content, directory_path, raw_data_path):
    try:
        print("In processAbbreviateddial")
        lines = content.splitlines()
        extAndName = []
        #label= False
        systemList = False
        nameSet = False
        gp = {}
        for line in lines:
            ln = line.strip()
            #extname = {}
            #print(ln)
            
            if "SYSTEM LIST" in line and systemList == False:
                gp['Group Name'] = "SYSTEM LIST"
                #print(gp['Group Name'])
                systemList = True
            elif ln and ln[0].isdigit() and systemList == True:
                extname = {}
                elems = line.split()
                labelname = ""
                label= False
                lastIndex = len(elems)
                idx = 1
                for elem in elems:
                    if ":" in elem and label == False:
                        extname['Code'] = elem.strip(":")
                    elif (":" not in elem and label == False and idx < lastIndex):
                        #print(elem.strip())
                        extname['Number'] = elem.strip()
                        label = True
                    elif ":" not in elem and label == True:
                        labelname = "".join(labelname) + " " + elem
                        extname['Label'] = labelname.strip()
                    
                    idx = idx + 1

                try:    
                    if "Number" in extname:
                        extAndName.append(extname)
                except:
                    pass

            elif "Group Name:" in line and nameSet == False:
                #print("Name: ", line.split(":")[2].strip())
                gp['Group Name'] = line.split(":")[2].strip()
                nameSet = True
            elif ln and ln[0].isdigit():
                extname = {}
                elems = line.split()
                #print(elems)
                for elem in elems:
                    if ":" in elem:
                        extname['Code'] = elem.strip(":")
                    elif elem:
                        extname['Number'] = elem.strip()
                        extname['Label'] = ""
                        #print(extname)
                        extAndName.append(extname)
                        extname = {}
                        #print(extAndName)

        index = 1
        for ext in extAndName:
            if ext:
                #print(ext)
                try:
                    gp['Code ' + str(index)] = ext['Code']
                    gp['Number ' + str(index)] = ext['Number']
                    gp['Label ' + str(index)] = ext['Label']
                except:
                    pass
                index = index + 1
        
        #print(gp)
        avaya_processAbbreviateddial.append(gp)

        # Write to a file
        pd.DataFrame(avaya_processAbbreviateddial).to_csv(raw_data_path + '/avaya_abbreviateddial.csv', index=False)

    except:
        print("Error in Abbreviated Dialing for group: ", gp['Group Name'])

def main():
    print("Starting")

    stationDir = "/Users/akgupta/Downloads/Apple-script"   ### will be removed
    groupPageDir = "/Users/akgupta/Downloads/Apple-script"   ### will be removed
    pickupGroupDir = "/Users/akgupta/Downloads/Apple-script"   ### will be removed
    huntgroupDir = "/Users/akgupta/Downloads/Apple-script"   ### will be removed
    locationDir = "/Users/akgupta/Downloads/Apple-script"   ### will be removed
    coverageanswerDir = "/Users/akgupta/Downloads/Apple-script"   ### will be removed
    abbreviatedDialingDir = "/Users/akgupta/Downloads/Apple-script"   ### will be removed

    # Define the path for the new directory
    csvDir = "/Users/akgupta/Downloads/Apple-script"
    directory_path = csvDir + "/output"
    raw_data_path = directory_path + "/raw_data"

    # Create the directory
    # Check if the directory already exists
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)
    else:
        pass
    if not os.path.exists(raw_data_path):
        os.mkdir(raw_data_path)
    else:
        pass

    # Read Location
    avaya_location_data = ""
    with open(locationDir + '/Hanover_List_Locations.txt', 'r') as file:
            avaya_location_data = file.read()  # Reads the entire file
    # Process location
    processLocation(avaya_location_data, directory_path, raw_data_path)

    # Read Station 
    avaya_station_data = ""
    with open(stationDir + '/Hanover_Display_Stations.txt', 'r') as file:
            avaya_station_data = file.read()  # Reads the entire file
    # Process Station and create WxC user, user settings, configured lines, line key assignment CSV files
    processStation(avaya_station_data, directory_path, raw_data_path)

    # Read Hunt group
    avaya_huntgroup_data = ""
    with open(huntgroupDir + '/Hanover_HuntGroups.txt', 'r') as file:
            avaya_huntgroup_data = file.read()  # Reads the entire file

    # Read Hunt Group agents
    avaya_HuntGroupAgents = ""
    with open(huntgroupDir + '/Hanover_Agents.txt', 'r') as file:
        avaya_HuntGroupAgents = file.read()  # Reads the entire file
    
    # Process Hunt Group
    processHuntgroupCallQeuue(avaya_huntgroup_data, directory_path, raw_data_path, avaya_HuntGroupAgents)

    # Read Group page
    files = os.listdir(groupPageDir)
    for file in files:
        if "Group_Page" in file and "Group_Page_List" not in file:
            #print(file)
            avaya_grouppage_data = ""
            with open(groupPageDir + '/' + file, 'r') as file:
                avaya_grouppage_data = file.read()  # Reads the entire file
                # Process Group page
                processGrouppage(avaya_grouppage_data, directory_path, raw_data_path)

    # Read Pickup group
    files = os.listdir(pickupGroupDir)
    for file in files:
        if "PickupGroup" in file:
            #print(file)
            avaya_pickupgroup_data = ""
            with open(pickupGroupDir + '/' + file, 'r') as file:
                avaya_pickupgroup_data = file.read()  # Reads the entire file
                # Process Group page
                processPickupgroup(avaya_pickupgroup_data, directory_path, raw_data_path)

    # Read coverage answer group
    files = os.listdir(coverageanswerDir)
    for file in files:
        if "CoverAnswerGroup" in file:
            #print(file)
            avaya_coverageanswergroup_data = ""
            with open(coverageanswerDir + '/' + file, 'r') as file:
                avaya_coverageanswergroup_data = file.read()  # Reads the entire file
                # Process Group page
                processCoverageAnswergroup(avaya_coverageanswergroup_data, directory_path, raw_data_path)
    
    # Read Abbreviated Dialing
    files = os.listdir(abbreviatedDialingDir)
    for file in files:
        if "AbbreviatedDial" in file:
            #print(file)
            avaya_abbreviateddialing_data = ""
            with open(abbreviatedDialingDir + '/' + file, 'r') as file:
                avaya_abbreviateddialing_data = file.read()  # Reads the entire file
                # Process Group page
                processAbbreviateddial(avaya_abbreviateddialing_data, directory_path, raw_data_path)


# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 
    
