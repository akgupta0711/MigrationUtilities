import pandas as pd
import requests
import sys
from requests.auth import HTTPBasicAuth
import getpass
import xml.etree.ElementTree as ET

print("Starting .... ", '\n\n')

def initWxCSchedule(schedule):
    schedule['Name'] = ""
    schedule['Location'] = ""
    schedule['Schedule action'] = ""
    schedule['Schedule type'] = ""
    schedule['Event action'] = ""
    schedule['Event 1 name'] = ""
    schedule['Event 1 start date'] = ""
    schedule['Event 1 end date'] = ""
    schedule['Event 1 start time'] = ""
    schedule['Event 1 end time'] = ""
    schedule['Event 1 recurrence type'] = ""
    schedule['Event 1 day of recurrence by week'] = ""
    schedule['Event 1 day of yearly recurrence by day'] = ""
    schedule['Event 1 week of yearly recurrence by day'] = ""
    schedule['Event 1 month of yearly recurrence by day'] = ""
    schedule['Event 1 date of yearly recurrence by date'] = ""
    schedule['Event 1 month of yearly recurrence by date'] = ""
    schedule['Event 2 name'] = ""
    schedule['Event 2 start date'] = ""
    schedule['Event 2 end date'] = ""
    schedule['Event 2 start time'] = ""
    schedule['Event 2 end time'] = ""
    schedule['Event 2 recurrence type'] = ""
    schedule['Event 2 day of recurrence by week'] = ""
    schedule['Event 2 day of yearly recurrence by day'] = ""
    schedule['Event 2 week of yearly recurrence by day'] = ""
    schedule['Event 2 month of yearly recurrence by day'] = ""
    schedule['Event 2 date of yearly recurrence by date'] = ""
    schedule['Event 2 month of yearly recurrence by date'] = ""
    schedule['Event 3 name'] = ""
    schedule['Event 3 start date'] = ""
    schedule['Event 3 end date'] = ""
    schedule['Event 3 start time'] = ""
    schedule['Event 3 end time'] = ""
    schedule['Event 3 recurrence type'] = ""
    schedule['Event 3 day of recurrence by week'] = ""
    schedule['Event 3 day of yearly recurrence by day'] = ""
    schedule['Event 3 week of yearly recurrence by day'] = ""
    schedule['Event 3 month of yearly recurrence by day'] = ""
    schedule['Event 3 date of yearly recurrence by date'] = ""
    schedule['Event 3 month of yearly recurrence by date'] = ""
    schedule['Event 4 name'] = ""
    schedule['Event 4 start date'] = ""
    schedule['Event 4 end date'] = ""
    schedule['Event 4 start time'] = ""
    schedule['Event 4 end time'] = ""
    schedule['Event 4 recurrence type'] = ""
    schedule['Event 4 day of recurrence by week'] = ""
    schedule['Event 4 day of yearly recurrence by day'] = ""
    schedule['Event 4 week of yearly recurrence by day'] = ""
    schedule['Event 4 month of yearly recurrence by day'] = ""
    schedule['Event 4 date of yearly recurrence by date'] = ""
    schedule['Event 4 month of yearly recurrence by date'] = ""
    schedule['Event 5 name'] = ""
    schedule['Event 5 start date'] = ""
    schedule['Event 5 end date'] = ""
    schedule['Event 5 start time'] = ""
    schedule['Event 5 end time'] = ""
    schedule['Event 5 recurrence type'] = ""
    schedule['Event 5 day of recurrence by week'] = ""
    schedule['Event 5 day of yearly recurrence by day'] = ""
    schedule['Event 5 week of yearly recurrence by day'] = ""
    schedule['Event 5 month of yearly recurrence by day'] = ""
    schedule['Event 5 date of yearly recurrence by date'] = ""
    schedule['Event 5 month of yearly recurrence by date'] = ""
    schedule['Event 6 name'] = ""
    schedule['Event 6 start date'] = ""
    schedule['Event 6 end date'] = ""
    schedule['Event 6 start time'] = ""
    schedule['Event 6 end time'] = ""
    schedule['Event 6 recurrence type'] = ""
    schedule['Event 6 day of recurrence by week'] = ""
    schedule['Event 6 day of yearly recurrence by day'] = ""
    schedule['Event 6 week of yearly recurrence by day'] = ""
    schedule['Event 6 month of yearly recurrence by day'] = ""
    schedule['Event 6 date of yearly recurrence by date'] = ""
    schedule['Event 6 month of yearly recurrence by date'] = ""
    schedule['Event 7 name'] = ""
    schedule['Event 7 start date'] = ""
    schedule['Event 7 end date'] = ""
    schedule['Event 7 start time'] = ""
    schedule['Event 7 end time'] = ""
    schedule['Event 7 recurrence type'] = ""
    schedule['Event 7 day of recurrence by week'] = ""
    schedule['Event 7 day of yearly recurrence by day'] = ""
    schedule['Event 7 week of yearly recurrence by day'] = ""
    schedule['Event 7 month of yearly recurrence by day'] = ""
    schedule['Event 7 date of yearly recurrence by date'] = ""
    schedule['Event 7 month of yearly recurrence by date'] = ""
    schedule['Event 8 name'] = ""
    schedule['Event 8 start date'] = ""
    schedule['Event 8 end date'] = ""
    schedule['Event 8 start time'] = ""
    schedule['Event 8 end time'] = ""
    schedule['Event 8 recurrence type'] = ""
    schedule['Event 8 day of recurrence by week'] = ""
    schedule['Event 8 day of yearly recurrence by day'] = ""
    schedule['Event 8 week of yearly recurrence by day'] = ""
    schedule['Event 8 month of yearly recurrence by day'] = ""
    schedule['Event 8 date of yearly recurrence by date'] = ""
    schedule['Event 8 month of yearly recurrence by date'] = ""
    schedule['Event 9 name'] = ""
    schedule['Event 9 start date'] = ""
    schedule['Event 9 end date'] = ""
    schedule['Event 9 start time'] = ""
    schedule['Event 9 end time'] = ""
    schedule['Event 9 recurrence type'] = ""
    schedule['Event 9 day of recurrence by week'] = ""
    schedule['Event 9 day of yearly recurrence by day'] = ""
    schedule['Event 9 week of yearly recurrence by day'] = ""
    schedule['Event 9 month of yearly recurrence by day'] = ""
    schedule['Event 9 date of yearly recurrence by date'] = ""
    schedule['Event 9 month of yearly recurrence by date'] = ""
    schedule['Event 10 name'] = ""
    schedule['Event 10 start date'] = ""
    schedule['Event 10 end date'] = ""
    schedule['Event 10 start time'] = ""
    schedule['Event 10 end time'] = ""
    schedule['Event 10 recurrence type'] = ""
    schedule['Event 10 day of recurrence by week'] = ""
    schedule['Event 10 day of yearly recurrence by day'] = ""
    schedule['Event 10 week of yearly recurrence by day'] = ""
    schedule['Event 10 month of yearly recurrence by day'] = ""
    schedule['Event 10 date of yearly recurrence by date'] = ""
    schedule['Event 10 month of yearly recurrence by date'] = ""

def main():

    unityHost = ""
    username = ""
    password = ""
    outputFilePath = ""
    
    # total arguments
    n = len(sys.argv)
    print("Total arguments passed:", n - 1)

    if n == 1:
        print("Usage: " + '\n' + "python UnityScheduleToWxCSchedule.py unityHost=<see below> outputFilePath=<see below> username=<see below>" + '\n' +
        "Also, enter Unity admin password when prompted as next step" + '\n')
        print("unityHost=<Unity server hostname / IP address>")
        print("outputFilePath=<WxC Schedule CSV filename with path>")
        print("username=<Admin username>" + '\n')
        exit()

    # Arguments passed
    print("\nName of Python script:", sys.argv[0])
    print("Argument passed are:")

    for i in range(1, n):
        #print(sys.argv[i])
        param = sys.argv[i].split("=")
        print(param[0] + " = " + param[1])
        if param[0] == "unityHost":
            csvDir = param[1]
        if param[0] == "outputFilePath":
            userList = param[1]
        if param[0] == "username":
            insightDir = param[1]
    if i > 1 and username != "":
        password = getpass.getpass('Unity admin password=')
    print('\n')


    ###### Retrive ScheduleSets from Unity
    response = requests.get(
    'https://' + unityHost + '/vmrest/schedulesets', 
    auth=HTTPBasicAuth(username, password), verify=False)

    element = ET.XML(response.text)
    ET.indent(element)
    print(ET.tostring(element, encoding='unicode'))

    f = open("UnitySchedules.xml", "w")
    f.write(ET.tostring(element, encoding='unicode'))
    f.close()

    root = ET.parse("UnitySchedules.xml").getroot()

    done = False
    # Process Schedules

    schedules = []

    while done == False:

        scheduleSets = []
        
        for x in root.iter():

            tagVal1 = {}
            if x.tag == 'DisplayName':
                tagVal1['DisplayName'] = x.text
            if x.tag == 'ScheduleSetMembersURI':
                tagVal1['ScheduleSetMembersURI'] = x.text
            if len(tagVal1) != 0:
                scheduleSets.append(tagVal1)

        #print('\n\n', scheduleSets, '\n')

        ssElemCount = 0
        while ssElemCount < len(scheduleSets):
            try: 
                if list(scheduleSets[ssElemCount].keys())[0] == 'DisplayName':
                    schedule = {}
                    initWxCSchedule(schedule)
                    schedule['Name'] = scheduleSets[ssElemCount]['DisplayName']
                    schedule['Schedule action'] = "ADD"
                    schedule['Schedule type'] = "TIME"
                    
                    # Retrive Schedule Members
                    url = 'https://' + unityHost + scheduleSets[ssElemCount + 1]['ScheduleSetMembersURI']
                    response2 = requests.get( 
                        url,
                        auth=HTTPBasicAuth(username, password), verify=False)
                    
                    element2 = ET.XML(response2.text)
                    ET.indent(element2)
                    print(ET.tostring(element2, encoding='unicode'))

                    f = open("UnitySchedules.xml", "w")
                    f.write(ET.tostring(element2, encoding='unicode'))
                    f.close()

                    root2 = ET.parse("UnitySchedules.xml").getroot()
                    
                    for x2 in root2.iter():
                        if x2.tag == 'ScheduleURI':

                            # Retrive Schedule
                            url3 = 'https://' + unityHost + x2.text
                            response3 = requests.get( 
                                url3,
                                auth=HTTPBasicAuth(username, password), verify=False)
                    
                            element3 = ET.XML(response3.text)
                            ET.indent(element3)
                            print(ET.tostring(element3, encoding='unicode'))

                            f = open("UnitySchedules.xml", "w")
                            f.write(ET.tostring(element3, encoding='unicode'))
                            f.close()

                            root3 = ET.parse("UnitySchedules.xml").getroot()
                    
                            for x3 in root3.iter():
                                
                                if x3.tag == 'IsHoliday' and x3.text == "true":
                                    schedule['Schedule type'] = "HOLIDAY"
                                    
                                if x3.tag == 'ScheduleDetailsURI':

                                    # Retrive Schedule Details
                                    url4 = 'https://' + unityHost + x3.text
                                    response4 = requests.get( 
                                        url4,
                                        auth=HTTPBasicAuth(username, password), verify=False)
                    
                                    element4 = ET.XML(response4.text)
                                    ET.indent(element4)
                                    print(ET.tostring(element4, encoding='unicode'))

                                    f = open("UnitySchedules.xml", "w")
                                    f.write(ET.tostring(element4, encoding='unicode'))
                                    f.close()

                                    root4 = ET.parse("UnitySchedules.xml").getroot()
                                    
                                    startDate = ""
                                    for sd in root4.iter():
                                        if sd.tag == 'StartDate' and sd.text != "":
                                            startDate = ((sd.text).split(" ")[0]).replace("-","/")
                                    
                                    EndDate = ""
                                    for ed in root4.iter():
                                        if ed.tag == 'EndDate' and ed.text != "":
                                            EndDate = ((ed.text).split(" ")[0]).replace("-","/")
                                            
                                    startTime = ""
                                    for st in root4.iter():
                                        if st.tag == 'StartTime' and int(st.text):
                                            h = int(st.text)//60
                                            m = int(st.text)%60
                                            startTime = str(h) + ':' + str(m)   
                                    EndTime = ""
                                    for et in root4.iter():
                                        if et.tag == 'EndTime' and int(et.text):
                                            h = int(et.text)//60
                                            m = int(et.text)%60
                                            EndTime = str(h) + ':' + str(m)
                                    
                                    indx = 1
                                    for x4 in root4.iter():
                                        schedule['Event action'] = "ADD"
                                        if x4.tag == 'IsActiveMonday' and x4.text == "true":
                                            schedule['Event ' + str(indx) + ' name'] = "Monday 1"
                                            schedule['Event ' + str(indx) + ' start date'] = startDate
                                            schedule['Event ' + str(indx) + ' end date'] = EndDate
                                            schedule['Event ' + str(indx) + ' start time'] = startTime
                                            schedule['Event ' + str(indx) + ' end time'] = EndTime
                                            schedule['Event ' + str(indx) + ' recurrence type'] = "WEEKLY"
                                            schedule['Event ' + str(indx) + ' day of recurrence by week'] = "MONDAY"
                                            indx = indx + 1
                                        if x4.tag == 'IsActiveTuesday' and x4.text == "true":
                                            schedule['Event ' + str(indx) + ' name'] = "Tuesday 1"
                                            schedule['Event ' + str(indx) + ' start date'] = startDate
                                            schedule['Event ' + str(indx) + ' end date'] = EndDate
                                            schedule['Event ' + str(indx) + ' start time'] = startTime
                                            schedule['Event ' + str(indx) + ' end time'] = EndTime
                                            schedule['Event ' + str(indx) + ' recurrence type'] = "WEEKLY"
                                            schedule['Event ' + str(indx) + ' day of recurrence by week'] = "TUESDAY"
                                            indx = indx + 1
                                        if x4.tag == 'IsActiveWednesday' and x4.text == "true":
                                            schedule['Event ' + str(indx) + ' name'] = "Wednesday 1"
                                            schedule['Event ' + str(indx) + ' start date'] = startDate
                                            schedule['Event ' + str(indx) + ' end date'] = EndDate
                                            schedule['Event ' + str(indx) + ' start time'] = startTime
                                            schedule['Event ' + str(indx) + ' end time'] = EndTime
                                            schedule['Event ' + str(indx) + ' recurrence type'] = "WEEKLY"
                                            schedule['Event ' + str(indx) + ' day of recurrence by week'] = "WEDNESDAY"
                                            indx = indx + 1
                                        if x4.tag == 'IsActiveThursday' and x4.text == "true":
                                            schedule['Event ' + str(indx) + ' name'] = "Thursday 1"
                                            schedule['Event ' + str(indx) + ' start date'] = startDate
                                            schedule['Event ' + str(indx) + ' end date'] = EndDate
                                            schedule['Event ' + str(indx) + ' start time'] = startTime
                                            schedule['Event ' + str(indx) + ' end time'] = EndTime
                                            schedule['Event ' + str(indx) + ' recurrence type'] = "WEEKLY"
                                            schedule['Event ' + str(indx) + ' day of recurrence by week'] = "THURSDAY"
                                            indx = indx + 1
                                        if x4.tag == 'IsActiveFriday' and x4.text == "true":
                                            schedule['Event ' + str(indx) + ' name'] = "Friday 1"
                                            schedule['Event ' + str(indx) + ' start date'] = startDate
                                            schedule['Event ' + str(indx) + ' end date'] = EndDate
                                            schedule['Event ' + str(indx) + ' start time'] = startTime
                                            schedule['Event ' + str(indx) + ' end time'] = EndTime
                                            schedule['Event ' + str(indx) + ' recurrence type'] = "WEEKLY"
                                            schedule['Event ' + str(indx) + ' day of recurrence by week'] = "FRIDAY"
                                            indx = indx + 1
                                        if x4.tag == 'IsActiveSaturday' and x4.text == "true":
                                            schedule['Event ' + str(indx) + ' name'] = "Saturday 1"
                                            schedule['Event ' + str(indx) + ' start date'] = startDate
                                            schedule['Event ' + str(indx) + ' end date'] = EndDate
                                            schedule['Event ' + str(indx) + ' start time'] = startTime
                                            schedule['Event ' + str(indx) + ' end time'] = EndTime
                                            schedule['Event ' + str(indx) + ' recurrence type'] = "WEEKLY"
                                            schedule['Event ' + str(indx) + ' day of recurrence by week'] = "SATURDAY"
                                            indx = indx + 1
                                        if x4.tag == 'IsActiveSunday' and x4.text == "true":
                                            schedule['Event ' + str(indx) + ' name'] = "Sunday 1"
                                            schedule['Event ' + str(indx) + ' start date'] = startDate
                                            schedule['Event ' + str(indx) + ' end date'] = EndDate
                                            schedule['Event ' + str(indx) + ' start time'] = startTime
                                            schedule['Event ' + str(indx) + ' end time'] = EndTime
                                            schedule['Event ' + str(indx) + ' recurrence type'] = "WEEKLY"
                                            schedule['Event ' + str(indx) + ' day of recurrence by week'] = "SUNDAY"
                                            indx = indx + 1

                    schedules.append(schedule)
            except:
                print("Error in Schedule Sets ")
                
            ssElemCount = ssElemCount + 2
            
        done = True

    scheduleDF = pd.DataFrame(schedules)
    scheduleDF.to_csv(outputFilePath, index=False)

    print('\n\n', "Completed. Please check Schedules.csv at", outputFilePath)

# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 
