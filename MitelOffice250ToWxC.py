import re
import csv
import pandas as pd
import os
import sys
import requests
import shutil

def is_valid_mac(mac_address_string):
    """
    Checks if a string is a valid MAC address.

    Supports common formats:
    - XX:XX:XX:XX:XX:XX (colon-separated)
    - XX-XX-XX-XX-XX-XX (hyphen-separated)
    - XXXX.XXXX.XXXX (dot-separated)
    """
    # Regex for colon or hyphen separated MAC addresses
    pattern1 = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    # Regex for dot separated MAC addresses (e.g., Cisco format)
    pattern2 = re.compile(r'^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$')

    return bool(pattern1.match(mac_address_string)) or bool(pattern2.match(mac_address_string))

# Create a Mitel data workbook
# The outout file MitelDataWorkbook.csv where admin can populate email_address for the user
def prepapreMitelOffice250ToWxCCSV(directory_path, filename, condition):
    print("Starting prepapreMitelOffice250ToWxCCSV")

    try:
        os.remove(directory_path + '/MitelDataWorkbook.csv')
    except:
        pass
    try:
        mitelInput = []
        mitelOutput = []
        emailAddressPresent = False
        column = ""
        contains = ""
        index = 3
        nameOrder = "s"

        with open(directory_path + filename, 'r') as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                mitelInput.append(row)

        if 'email_address' in mitelInput:
            emailAddressPresent = True
    
        conditionElems = condition.split(";")
        for conditionElem in conditionElems:
            eachCondition = conditionElem.split(":")
            if "column" in eachCondition:
                column = eachCondition[1]
            if "contains" in eachCondition:
                try:
                    contains = eachCondition[1]  
                except:
                    pass  
            if "nameorder" in eachCondition:
                nameOrder = eachCondition[1] 

        
        for elem1 in mitelInput:
            if elem1[0] == column:
                index = 0
            elif elem1[1] == column:
                index = 1
            elif elem1[2] == column:
                index = 2
            elif elem1[3] == column:
                index = 3
            elif elem1[4] == column:
                index = 4
            elif elem1[5] == column:
                index = 5
            elif elem1[6] == column:
                index = 6
            break
        
        for elem in mitelInput:
            if elem[0] != 'DeviceType':
                miteldata = {}
                miteldata['DeviceType'] = elem[0]
                miteldata['Extension'] = elem[1]
                miteldata['Username'] = elem[2]
                miteldata['Description / Label'] = elem[3]
                miteldata['Node'] = elem[4]
                miteldata['HW / MAC / SIP Peer'] = elem[5]
                
                if emailAddressPresent:
                    miteldata['email_address'] = elem[6]
                if emailAddressPresent and (miteldata['email_address']):
                    miteldata['Notes (DO NOT modify this column)'] = str(index) + '|' + contains + '|' + nameOrder
                elif contains and contains in elem[index]:
                    miteldata['email_address'] = "Add email here"
                    miteldata['Notes (DO NOT modify this column)'] = str(index) + '|' + contains + '|' + nameOrder
                else:
                    miteldata['email_address'] = ""
                
                if "Node - Remote" in elem[0] or "Node - Local" in elem[0]:
                    miteldata['Notes (DO NOT modify this column)'] = "Replace 'Description / Label' with WxC Location"
                mitelOutput.append(miteldata)
    except:
        pass
    
    try:
        MitelDataWorkbook = pd.DataFrame(mitelOutput)
        MitelDataWorkbook.to_csv(directory_path + '/MitelDataWorkbook.csv', index=False)
    except:
        pass

## Process Mitel data and create WxC CSV files
def generateMitelOffice250ToWxCCSV(directory_path, filename, orgid, auth):
    print("Starting generateMitelOffice250ToWxCCSV")
    try:
        base_directory_path = directory_path + filename.split('.')[0]
        #print(directory_path, filename.split('.')[0], base_directory_path)
        try:
            shutil.rmtree(base_directory_path)
        except OSError as e:
            pass
        
        try:
            os.mkdir(base_directory_path)
        except OSError as e:
            print(f"Error: {base_directory_path} : {e.strerror}")

        mitelData = []
        with open(directory_path + filename, 'r') as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                mitelData.append(row)

        #### Download User, device, Huntgroup CSV template from Webex
        url1 = "https://atlas-a.wbx2.com/admin/api/v1/csv/organizations/" + orgid + "/users/template"
        url2 = "https://admin-batch-service-r.wbx2.com/api/v1/customers/" + orgid + "/jobs/general/deviceonboard/template"
        url3 = "https://admin-batch-service-r.wbx2.com/api/v1/customers/" + orgid + "/jobs/general/huntgrouponboard/template"

        payload = None
        headers = {
            "Authorization": auth,
            "Accept": "application/json, text/plain, */*"
        }

        response1 = requests.request('GET', url1, headers=headers, data = payload)
        response2 = requests.request('GET', url2, headers=headers, data = payload)
        response3 = requests.request('GET', url3, headers=headers, data = payload)
    except:
        pass

    # User CSV Template
    try:
        os.remove(base_directory_path + '/Users_1.csv')
    except:
        pass
    
    try:
        fileUsers = base_directory_path + '/Users_1.csv'
        with open(fileUsers, 'w') as file:
            file.write(response1.text)
        Users = pd.read_csv(fileUsers)
        Users = Users.head(0)
    except:
        pass

    # Device CSV Template
    try:
        os.remove(base_directory_path + '/Devices_1.csv')
    except:
        pass
    
    try:
        fileDevices = base_directory_path + '/Devices_1.csv'
        with open(fileDevices, 'w') as file:
            file.write(response2.text)
        Devices = pd.read_csv(fileDevices)
        DevicesForUsers = Devices.head(0)
        DevicesForWorkspaces = Devices.head(0)
    except:
        pass

    # HG CSV template
    try:
        os.remove(base_directory_path + '/HG_1.csv')
    except:
        pass

    try:
        fileHG = base_directory_path + '/HG_1.csv'
        with open(fileHG, 'w') as file:
            file.write(response3.text)
        HuntGroups = pd.read_csv(fileHG)
        HuntGroups = HuntGroups.head(0)
    except:
        pass

    try:
        os.remove(base_directory_path + '/Users_1.csv')
        os.remove(base_directory_path + '/Devices_1.csv')
        os.remove(base_directory_path + '/HG_1.csv')
    except:
        pass

    try:
        deviceType = []
        nodes = []
        nodesDict = {}
        locations = []
        virtualExtensionDeviceTypeInMitel = ['Phantom Device - Off-node', 'Phone - Single Line - Off-node', 'Phone - IP/Digital - Off-node', 'Phantom Device', 'Phone - Single Line']
        virtualLines = []
        pageGroups = []
        mailboxes = []

        for elem in mitelData:
            if "Node - Remote" in elem[0] or "Node - Local" in elem[0]:
                node = {}
                node['Node Type'] = elem[0]
                node['Name'] = elem[3]
                node['Number'] = elem[4]
                nodes.append(node)
        
        for node in nodes:
            nodesDict[node['Number']] = node['Name']

        for elem in mitelData:
            # DeviceType	Extension	Username	Description / Label	Node	HW / MAC / SIP Peer
            if elem[0] not in deviceType:
                if elem[0] != 'DeviceType':
                    deviceType.append(elem[0])
                    #print(elem[0])

            # Prepare WxC User.csv
            # First Name	Last Name	Display Name	User ID/Email (Required)  Extension  Location
            delimiter = ""
            userIndex = 3
            nameOrder = "r"
            userRow = False
            try:
                #if (elem[7] and elem[7] != "Replace 'Description / Label' with WxC Location") or (elem[7] and elem[7] != "Notes (DO NOT modify this column)"):
                if elem[7] and "|" in elem[7]:
                    userRow = True
                    notes = elem[7].split("|")
                    userIndex = int(notes[0])
                    delimiter = str(notes[1])
                    nameOrder = str(notes[2])
            except:
                pass

            #if (delimiter and delimiter in elem[userIndex]) or ("@" in elem[6]):
            if(userRow):
                user = {}
                if nameOrder == "r":
                    if delimiter != "":
                        user['First Name'] = elem[userIndex].split(delimiter)[1]
                        user['Last Name'] = elem[userIndex].split(delimiter)[0]
                    else:
                        user['First Name'] = elem[userIndex].split(" ")[1]
                        user['Last Name'] = elem[userIndex].split(" ")[0]
                else:
                    if delimiter != "":
                        user['First Name'] = elem[userIndex].split(delimiter)[0]
                        user['Last Name'] = elem[userIndex].split(delimiter)[1]
                    else:
                        user['First Name'] = elem[userIndex].split(" ")[0]
                        user['Last Name'] = elem[userIndex].split(" ")[1]

                if delimiter != "":
                    user['Display Name'] = user['First Name'] + " " + user['Last Name']
                else:
                    user['Display Name'] = elem[userIndex]

                if "@" in elem[6]:
                    user['User ID/Email (Required)'] = elem[6]
                elif elem[6] == "Add email here":
                    user['User ID/Email (Required)'] = "Add email here"
                else:
                    user['User ID/Email (Required)'] = ""

                user['Extension'] = elem[1]
                user['Location'] = nodesDict[elem[4]]
                new_row = pd.DataFrame([user])
                Users = pd.concat([Users, new_row], ignore_index=True)

            # Create Device.csv for devices owned by user
            # Username	Type	Extension	Phone Number	Device Type	Model	MAC Address	Location	Calling Plan	Workspace Subscription Update Only
            userOwnedDevice = False
            #if is_valid_mac(elem[5]) and ((delimiter and delimiter in elem[userIndex]) or ("@" in elem[6])):
            if is_valid_mac(elem[5]) and userRow:
                userOwnedDevice = True
                device = {}
                if "@" in elem[6]:
                    device['Username'] = elem[6]
                elif elem[6] == "Add email here":
                    device['Username'] = elem[3] + " (Replace with email)"
                else:
                    device['Username'] = ""
                device['Type'] = "USER"
                device['Extension'] = elem[1]
                device['Phone Number'] = ""
                device['Device Type'] = "IP"
                device['Model'] = ""
                device['MAC Address'] = ""
                device['Location'] = nodesDict[elem[4]]
                device['Calling Plan'] = ""
                device['Workspace Subscription Update Only'] = ""
                new_row = pd.DataFrame([device])
                DevicesForUsers = pd.concat([DevicesForUsers, new_row], ignore_index=True)

            # Create Device.csv for workspaces
            # Username	Type	Extension	Phone Number	Device Type	Model	MAC Address	Location	Calling Plan	Workspace Subscription Update Only
            if is_valid_mac(elem[5]) and userOwnedDevice == False:
                device = {}
                device['Username'] = elem[3]
                device['Type'] = "WORKSPACE"
                device['Extension'] = elem[1]
                device['Phone Number'] = ""
                device['Device Type'] = "IP"
                device['Model'] = ""
                device['MAC Address'] = ""
                device['Location'] = nodesDict[elem[4]]
                device['Calling Plan'] = ""
                device['Workspace Subscription Update Only'] = ""
                new_row = pd.DataFrame([device])
                DevicesForWorkspaces = pd.concat([DevicesForWorkspaces, new_row], ignore_index=True)

            # Create Virtuallines.csv
            # First Name	Last Name	Display Name	Location	Phone Number	Extension
            if elem[0] in virtualExtensionDeviceTypeInMitel:
                virtualLine = {}
                virtualLine['First Name'] = elem[2]
                virtualLine['Last Name'] = elem[2]
                virtualLine['Display Name'] = elem[3]
                virtualLine['Location'] = nodesDict[elem[4]]
                virtualLine['Phone Number'] = ""
                virtualLine['Extension'] = elem[1]
                virtualLines.append(virtualLine)

            # Create Huntgroups.csv
            # Name	Extension	Location
            if 'Hunt Group' in elem[0] or 'Hunt Group - Off-node' in elem[0]:
                huntGroup = {}
                huntGroup['Name'] = elem[3]
                huntGroup['Extension'] = elem[1]
                huntGroup['Location'] = nodesDict[elem[4]]
                new_row = pd.DataFrame([huntGroup])
                HuntGroups = pd.concat([HuntGroups, new_row], ignore_index=True)

            # Create Pagegroups.csv
            # Name	Extension	Location
            if 'Page Zone' in elem[0] or 'Page Zone - Off-node' in elem[0] or 'Page Port' in elem[0]:
                pageGroup = {}
                pageGroup['Name'] = elem[3]
                pageGroup['Extension'] = elem[1]
                pageGroup['Location'] = nodesDict[elem[4]]
                pageGroups.append(pageGroup)

            # Create Voicemail.csv
            # Name	Phone Number	Extension	Location	Enabled
            if 'Mailbox - Off-node' in elem[0] or 'Application - Voice Mail - Off-node' in elem[0]:
                mailbox = {}
                if elem[3]:
                    mailbox['Name'] = elem[3]
                else:
                    mailbox['Name'] = elem[2]
                mailbox['Phone Number'] = ""
                mailbox['Extension'] = elem[1]
                mailbox['Location'] = nodesDict[elem[4]]
                mailbox['Enabled'] = ""
                mailboxes.append(mailbox)
    except:
        pass

    # Create WxCLocation.csv
    try:
        os.remove(base_directory_path + '/WxCLocations.csv')
    except:
        pass

    try:
        # Create Location.csv based on Node
        # Location ID	Location Name (Required)	Address line 1 (Required)	Address line 2	City / Town	State / Province	ZIP / Postal Code	Country (Required)	Latitude	Longitude	Preferred Language	Timezone	Notes	References
        for node in nodes:
            location = {}
            location['Location ID'] = ""
            location['Location Name (Required)'] = node['Name']
            location['Address line 1 (Required)'] = ""
            location['Address line 2'] = ""
            location['City / Town'] = ""
            location['State / Province'] = ""
            location['ZIP / Postal Code'] = ""
            location['Country (Required)'] = ""
            location['Latitude'] = ""
            location['Longitude'] = ""
            location['Preferred Language'] = ""
            location['Timezone'] = ""
            location['Notes'] = ""
            location['References'] = ""
            locations.append(location)
        WxCLocations = pd.DataFrame(locations)
        WxCLocations.to_csv(base_directory_path + '/WxCLocation.csv', index=False) 
    except:
        pass

    # Create WxCUsers.csv
    try:
        os.remove(base_directory_path + '/WxCUsers.csv')
    except:
        pass

    try:
        WxCUsers = Users
        WxCUsers.to_csv(base_directory_path + '/WxCUsers.csv', index=False) 
    except:
        pass

    # Create WxCDevicesForUsers.csv
    try:
        os.remove(base_directory_path + '/WxCDevicesForUsers.csv')
    except:
        pass

    try:
        WxCDevicesForUsers = DevicesForUsers
        WxCDevicesForUsers.to_csv(base_directory_path + '/WxCDevicesForUsers.csv', index=False) 
    except:
        pass

    # Create WxCDevicesForWorkspaces.csv
    try:
        os.remove(base_directory_path + '/WxCDevicesForWorkspaces.csv')
    except:
        pass

    try:
        WxCDevicesForWorkspaces = DevicesForWorkspaces
        WxCDevicesForWorkspaces.to_csv(base_directory_path + '/WxCDevicesForWorkspaces.csv', index=False) 
    except:
        pass

    # Create WxCVirtualLines.csv
    try:
        os.remove(base_directory_path + '/WxCVirtualLines.csv')
    except:
        pass

    try:
        WxCVirtualLines = pd.DataFrame(virtualLines)
        WxCVirtualLines.to_csv(base_directory_path + '/WxCVirtualLines.csv', index=False) 
    except:
        pass

    # Create WxCHuntGroups.csv
    try:
        os.remove(base_directory_path + '/WxCHuntGroups.csv')
    except:
        pass

    try:
        WxCHuntGroups = HuntGroups
        WxCHuntGroups.to_csv(base_directory_path + '/WxCHuntGroups.csv', index=False)
    except:
        pass

    # Create WxCPageGroups.csv
    try:
        os.remove(base_directory_path + '/WxCPageGroups.csv')
    except:
        pass

    try:
        WxCPageGroups = pd.DataFrame(pageGroups)
        WxCPageGroups.to_csv(base_directory_path + '/WxCPageGroups.csv', index=False)
    except:
        pass

    # Create WxCMailboxes.csv
    try:
        os.remove(base_directory_path + '/WxCMailboxes.csv')
    except:
        pass

    try:
        WxCMailboxes = pd.DataFrame(mailboxes)
        WxCMailboxes.to_csv(base_directory_path + '/WxCMailboxes.csv', index=False) 
    except:
        pass

#####################     
#### Main ###########
def main():
    print("Starting")

    try: 
        #csvdir = "/Users/akgupta/Downloads" 
        csvdir = ""
        mitelExtract = ""
        mitelWorkbook = ""
        mitelExtractFinal = '/MitelExtract_final.csv'
        orgid = ""
        auth = ""
        type = "generate"
        condition = ""
        columns = []

        # total arguments
        n = len(sys.argv)
        print("Total arguments passed:", n - 1)
        #print("Commad = ", sys.argv)
        print('\n')

        if n == 1:
            print("Usage:")
            print("1) First prepare migration workbook using:" + '\n')
            print("./MitelOffice250ToWxC prepare csvdir=<Full path to directory where extract csv file is kept> extract=<Extract file after romoving all columns except columns with real data> usercondition=<which colum to use to determine user, condition and name order>")
            print('\n' + "Command arguments:")
            print("------------------")
            print("a) csvdir - Full path to directory where extract csv file is kept" + '\n')
            print("b) extract - this is extrated CSV file from Mitel MiVoice Office 250 with admin removing following columns:")
            print("i) empty columns")
            print("ii) columns with these names -  All Extensions, DeviceType,Extension,Username,Description / Label, Node,HW / MAC / SIP Peer")
            print("iii) Last 2 columns with dates and page")
            print("AND adding a row one top (first row) with following columns - DeviceType,Extension, Username, Description / Label, Node, HW / MAC / SIP Peer")
            print('\n' + "c) usercondition - This is a mandatory parameter. It has following sub-parameters which should be separated by ';'. sub-parameter is name-value pair separated by ':' e.g. usercondition='column:Description / Label;contains:,;nameorder:s'")
            print("i)   column -> column to use to determine user name. This is a mandatory sub-parameter. e.g. column:Description / Label")
            print("ii)  contains -> delimeter to be used to determine user. This is a mandatory parameter (contains could be empty - contains:;, if email_address is present in extract file and those rows could be considered as user row). e.g. contains:,")
            print("iii) nameorder -> 's' - name is in <First name> <Last name> format (e.g. John Doe) OR 'r' - reverse (<Last name> delimiter <First name>) (e.g. Doe, John). Option e.g. - nameorder:s OR nameorder:r.")
            print('\n' + "This command will generate MitelDataWorkbook.csv in csvdir directory. Make correction/update in the workbook and then generate WxCalling CSVs using workbook. 'Notes' column in the output workbook must't be touched.")
            print('\n' + "d) columns - This is optional field. Default - 'DeviceType,Extension,email_address,Description / Label,Node,HW / MAC / SIP Peer,Username'. e.g. - columns='DeviceType,Extension,email_address,Description / Label,Node,HW / MAC / SIP Peer,Username'.")
            print('\n' + "2) Generate WxC CSV files:" + '\n')
            print("./MitelOffice250ToWxC generate csvdir=<CSV file dir> orgid=<Webex org ID> auth=<Bearer token> workbook=<workbook name>")
            print('\n' + "Command arguments:")
            print("------------------")
            print("a) csvdir - Full path to directory where extract csv file is kept")
            print("b) orgid - Webex org ID")
            print("c) auth - Bearer token (you can get it from https://developer.webex.com/). e.g. auth='Bearer MzY1NGRjN2QtZjMzZS00ZmUxLWFhYWEtNTU4MmEzMjlhNmI0OTk2M2U2MGEtZDVl_PC75_fe316f99-b864-4bdd-984f-45e143b3da68'")
            print("d) workbook - workbook file name")
            print('\n' + "This will create WxC CSV files under MitelDataWorkbook directory under csvdir." + '\n')

        if sys.argv[1] == "prepare":
            param = sys.argv[2].split("=")
            if param[0] == "csvdir":
                csvdir = param[1]
            param = sys.argv[3].split("=")
            if param[0] == "extract":
                mitelExtract = param[1]
            try:
                param = sys.argv[4].split("=")
                if param[0] == "usercondition":
                    condition = param[1]
            except:
                pass
            try:
                param = sys.argv[5].split("=")
                if param[0] == "columns":
                    columns = param[1].split(",")
            except:
                pass
            type = "prepare"
        elif len(sys.argv) == 4 and sys.argv[1] == "generate":
            param = sys.argv[2].split("=")
            if param[0] == "csvdir":
                csvdir = param[1]
            param = sys.argv[3].split("=")
            if param[0] == "orgid":
                orgid = param[1]
            param = sys.argv[4].split("=")
            if param[0] == "auth":
                auth = param[1]
            param = sys.argv[5].split("=")
            if param[0] == "extract":
                mitelExtract = param[1]
        elif len(sys.argv) == 6 and sys.argv[1] == "generate":
            param = sys.argv[2].split("=")
            if param[0] == "csvdir":
                csvdir = param[1]
            param = sys.argv[3].split("=")
            if param[0] == "orgid":
                orgid = param[1]
            param = sys.argv[4].split("=")
            if param[0] == "auth":
                auth = param[1]
            param = sys.argv[5].split("=")
            if param[0] == "extract":
                mitelExtract = param[1]
            elif param[0] == "workbook":
                mitelWorkbook = param[1]
                mitelWorkbook = '/' + mitelWorkbook
                # Process Mitel data and create WxC CSVs
                if orgid != "" and auth != "":
                    #print(orgid, auth)
                    generateMitelOffice250ToWxCCSV(csvdir, mitelWorkbook, orgid, auth)
                    print('\n' + "WxC CSV files created under MitelDataWorkbook directory under csvdir.")
                sys.exit()
        else:
            sys.exit()
    except:
        pass

    try:
        os.remove(csvdir + '/MitelExtract_final.csv')
    except:
        pass

    try:
        with open(csvdir + '/' + mitelExtract, 'r', newline='') as infile, \
        open(csvdir + mitelExtractFinal, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            # headers

            header = ["DeviceType", "Extension",	"Username",	"Description / Label",	"Node",	"HW / MAC / SIP Peer"]
            if columns:
                newColumns = []
                for elem in columns:
                    if elem == "DeviceType":
                        newColumns.append(elem)
                        break
                for elem in columns:
                    if elem == "Extension":
                        newColumns.append(elem)
                        break
                for elem in columns:
                    if elem == "Username":
                        newColumns.append(elem)
                        break
                for elem in columns:
                    if elem == "Description / Label":
                        newColumns.append(elem)
                        break
                for elem in columns:
                    if elem == "Node":
                        newColumns.append(elem)
                        break
                for elem in columns:
                    if elem == "HW / MAC / SIP Peer":
                        newColumns.append(elem)
                        break
                for elem in columns:
                    if elem == "email_address":
                        newColumns.append(elem)
                        break
                header = newColumns

            writer.writerow(header)

            index = 1
            for row in reader:
                if index % 2 == 0:
                    writer.writerow(row)
                else:
                    writer.writerow(row[6:]) 
                index = index + 1

        # Process Mitel data and create WxC CSVs
        if type == "generate":
            generateMitelOffice250ToWxCCSV(csvdir, mitelExtractFinal, orgid, auth)
        if type == "prepare":
            prepapreMitelOffice250ToWxCCSV(csvdir, mitelExtractFinal, condition)
            
            try:
                os.remove(csvdir + '/' + mitelExtractFinal)
            except:
                pass
            
            print('\n' + "MitelDataWorkbook.csv created in csvdir directory.")
            
    except:
        pass
 
# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 
