import os
import warnings
from tqdm import tqdm
from IPython.utils import io
import re
from rich import print_json
import json
import base64
from google.oauth2.credentials import Credentials
import sys
from datetime import datetime
import random
import validators
from flask import Flask, render_template_string
import threading
import time
import smtplib
from email.mime.multipart import MIMEMultipart

# Ignore all warnings
warnings.filterwarnings("ignore")

from google.cloud import pubsub_v1
from json import loads, load, dumps
import requests
from pathlib import Path
from google.cloud.storage import Client, transfer_manager
from pygments import highlight, lexers, formatters
from IPython.display import display, HTML

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML

from prompt_toolkit.key_binding import KeyBindings

bindings = KeyBindings()

@bindings.add('up')
def _(event):
    event.app.current_buffer.auto_up()

@bindings.add('down')
def _(event):
    event.app.current_buffer.auto_down()


# REPLACE YOUR DETAILS BELOW FROM THE FIRST MESSAGE IN YOUR RAGAAS SUPPORT WEBEX SPACE - ****DO NOT REMOVE THE QUOTE MARKS '''
def readRagConfFile(confFile):

    #print("Reading RAG Conf file")
    ragConf = ""

    try:
        ragConfFile = confFile
        with open(ragConfFile, 'r') as file:
            for line in file:
                # Process each line here
                #print(line.strip())
                if ragConf:
                    ragConf = ragConf + '\n'
                ragConf = ragConf + line.strip()

        return ragConf
    except:
        pass

def extract_API_details_for_RAGAAS(api_key_string):
    """
    Parses a string containing API keys and their values into a Python dictionary

    Args:
        api_key_string (str): A string where each line contains a key-value pair
                               separated by a colon, e.g., "Key: Value".

    Returns:
        dict: A dictionary where keys are the API key names (with spaces replaced by underscores)
              and values are their corresponding string values.
    """
    #print("Starting extract_API_details_for_RAGAAS")
    try:
        api_keys_dict = {}
        lines = api_key_string.strip().split('\n') # Split the string into individual lines

    
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1) # Split only on the first colon
                
                # Clean up whitespace from the key and replace spaces with underscores
                processed_key = key.strip().replace(' ', '_').lower()
                
                # Clean up whitespace from the value
                processed_value = value.strip()
                
                api_keys_dict[processed_key] = processed_value
        return api_keys_dict
    except:
        pass


def upload_directory_with_transfer_manager(bucket_name, source_directory, credentials, workers=8):
    """Upload every file in a directory, including all files in subdirectories.

    Each blob name is derived from the filename, not including the `directory`
    parameter itself. For complete control of the blob name for each file (and
    other aspects of individual blob metadata), use
    transfer_manager.upload_many() instead.
    """

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The directory on your computer to upload. Files in the directory and its
    # subdirectories will be uploaded. An empty string means "the current
    # working directory".
    # source_directory=""

    # The maximum number of processes to use for the operation. The performance
    # impact of this value depends on the use case, but smaller files usually
    # benefit from a higher number of processes. Each additional process occupies
    # some CPU and memory resources until finished. Threads can be used instead
    # of processes by passing `worker_type=transfer_manager.THREAD`.
    # workers=8
    try: 
        #print("Uploading files")
        storage_client = Client(credentials=credentials)
        bucket = storage_client.bucket(bucket_name)

        # Generate a list of paths (in string form) relative to the `directory`.
        # This can be done in a single list comprehension, but is expanded into
        # multiple lines here for clarity.

        # First, recursively get all files in `directory` as Path objects.
        directory_as_path_obj = Path(source_directory)
        paths = directory_as_path_obj.rglob("*")

        # Filter so the list only includes files, not directories themselves.
        file_paths = [path for path in paths if path.is_file()]

        # These paths are relative to the current working directory. Next, make them
        # relative to `directory`
        # relative_paths = [path.relative_to(source_directory) for path in file_paths]
        relative_paths = [path.relative_to(source_directory) for path in file_paths if not (path.name.startswith('.') or path.name.startswith('~'))]

        # Finally, convert them all to strings.
        string_paths = [str(path) for path in relative_paths if "metadata.json" != str(path)]

        #print("Found {} files.".format(len(string_paths)))

        # Start the upload.
        results = transfer_manager.upload_many_from_filenames(
            bucket, string_paths, source_directory=source_directory, max_workers=workers
        )
    except:
        pass


def RAGASS_ingest(csvdir, bucket_name, appKey, token_from_id, credentials, action):
    try:
        #print('\n' + "RAGASS Ingest" + '\n')
        # Upload files to bucket
        upload_directory_with_transfer_manager(bucket_name, csvdir, credentials, workers=2)

        # List all files

        # First, recursively get all files in `directory` as Path objects.
        directory_as_path_obj = Path(csvdir)
        paths = directory_as_path_obj.rglob("*")

        # Filter so the list only includes files, not directories themselves.
        file_paths = [path for path in paths if path.is_file()]

        relative_paths = [path.relative_to(csvdir) for path in file_paths if not (path.name.startswith('.') or path.name.startswith('~'))]

        # Finally, convert them all to strings.
        string_paths = [str(path) for path in relative_paths if "metadata.json" != str(path)]

        if action == 'add':
            print("Using files: " , string_paths)
        if action == 'delete':
            print("Deleting files: " , string_paths)

        current_date = datetime.now()
        formatted_date = current_date.strftime('%Y-%m-%d')

        for file in string_paths:

            docid = 'gs://' + bucket_name + '/' +  file
            doc = {
            'api_key': appKey,
            'user_id': 'akgupta',
            'action': action, # add/delete
            'content_url': docid,
            #'text': 'test text for the ingestion',
            'url': docid,
            'id': docid,
            'lastupdateddate': formatted_date, 
            'additional_metadata':{
                'title': file,
                'description': file.split('.')[0],
                'source': csvdir + '/' + file,
                'status': 'active',
                'locale': ['en_US'],
                'accesslevel': ['Employee'],
                'docversion': 1,
                'doctype': ''}
                #"stuff_prompt_msg": "<insert custom instructions here> When responding, you are to rely solely on the information presented in the text below. \n----------------\n{context}"}
            } 

            url = "https://chat-ai.cisco.com/genai-rag/ingest/v1.0/ragaas_ingest"

            payload = json.dumps(doc)
            headers = {
            'client-id': appKey,
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token_from_id
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            #print("Ingest response", response.text) 


        url = "https://chat-ai.cisco.com/genai-rag/ingest/v1.0/ragaas_ingest_status"

        payload = json.dumps({
        "api_key": appKey
        })
        headers = {
        'client-id': appKey,
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token_from_id
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        all_docs_status = json.loads(response.text)
        for each_doc in all_docs_status:
            #print("Ingest status response", each_doc)
            pass
    except:
        pass

def is_url_valid(url_string):
    """Checks if a string is a valid URL using the validators library."""
    validation_result = validators.url(url_string)
    return bool(validation_result)

def getPromptResponse():
    promptResponse = ""
    with open('temp_output.txt', 'r') as file:
        for line in file:
            if promptResponse:
                promptResponse = promptResponse + '\n'
            promptResponse = promptResponse + line.strip()
    #print(promptResponse)
    return promptResponse

# Initialize Flask and run web server
app = Flask(__name__)

@app.route('/')
def index():
    # Print line by line output on browser
    message = getPromptResponse().replace("\n", "<br />")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Python Output</title>
    </head>
    <body>
        <h4>Prompt Response:</h4>
        <p>{message}</p>
    </body>
    </html>
    """
    return render_template_string(html_content)
    
def runweb():
    app.run(use_reloader=False)

def RAGASS_Search(RAGAAS_API_details, prompt, userid, session_id ,request_id, output, promptCount):

    try:
        #print('\n' + "RAGASS Search")
        client_id = RAGAAS_API_details["search_client_id"]
        client_secret = RAGAAS_API_details["search_client_secret"]

        url = "https://id.cisco.com/oauth2/default/v1/token"

        payload = "grant_type=client_credentials"
        value = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {value}" #value can be generated using above cmd with echo
        }

        token_response = requests.request("POST", url, headers=headers, data=payload)

        token = token_response.json()["access_token"]

        url = "https://chat-ai.cisco.com/genai-rag/api/v1.0/ragaas"

        payload = json.dumps({
        "api_key": RAGAAS_API_details["search_api_key"],
        "user_id": userid,
        "query": prompt,
            # "filter_object": {"source": ["https://www.cisco.com/sample.html"]},
        "chat_session_id": session_id,
        "chat_request_id": request_id
        })

        headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        json_data_string = response.text
        #print(response.text) # Ajay need to remove

        # Load the JSON data into a Python dictionary
        json_data = json.loads(json_data_string)

        data = json_data['output_text'].split('\n')

        if output != "":
                if output == "browser":
                    if promptCount == 1:
                        try:
                            if os.path.exists(output):
                                input('\n' + "temp_output.txt exists. You can save the file. Enter to continue.")
                                os.remove(output + '/WxCVirtualLines.csv')
                        except:
                            pass
                        print("Sending output to http://127.0.0.1:5000. Open browser to see the output. Query/Response also saved in temp_output.txt.")
                        with open("temp_output.txt", "w") as file:
                            file.write('\n' + str(promptCount) + ") " + "QUERY:  " + prompt)
                            file.write('\n\n' + "RESPONSE: " + '\n')
                            for elem in data:
                                file.write(str(elem + '\n'))
                                print(elem)
                    else:
                        print("Appending output to http://127.0.0.1:5000")
                        with open("temp_output.txt", "a") as file:
                            file.write('\n' + str(promptCount) + ") " + "QUERY:  " + prompt)
                            file.write('\n\n' + "RESPONSE: " + '\n')
                            for elem in data:
                                file.write(str(elem + '\n'))
                                print(elem)
                    # Stating thread
                    flask_thread = threading.Thread(target=runweb, daemon=True)
                    flask_thread.start()
                else:
                    if promptCount == 1:
                        try:
                            if os.path.exists(output):
                                input('\n' + "Output file with same name exsits. Please save the file, otherwise it will be overwritten. Enter to continue.")
                                os.remove(output + '/WxCVirtualLines.csv')
                        except:
                            pass
                        print("Sending output to ", output)
                        with open(output, "w") as file:
                            file.write('\n' + str(promptCount) + ") " + "QUERY:  " + prompt)
                            file.write('\n\n' + "RESPONSE: " + '\n')
                            for elem in data:
                                file.write(str(elem + '\n'))
                                print(elem)
                    else:
                        print("Appending output to ", output)
                        with open(output, "a") as file:
                            file.write('\n' + str(promptCount) + ") " + "QUERY:  " + prompt)
                            file.write('\n\n' + "RESPONSE: " + '\n')
                            for elem in data:
                                file.write(str(elem + '\n'))
                                print(elem)
                    
        else:
            for elem in data:
                print(elem)
    except:
        pass


def main():

    csvdir = ""
    orgid = ""
    auth = ""
    ragConfFile = ""
    promptFile = ""
    prompts = ""
    usePrompt = False
    userid = ""
    web = False
    outputFile = ""

    # total arguments
    n = len(sys.argv)
    print('\n')

    if n == 1:
        print("Usage:")
        print("./AIGeneratedMigrationReports csvdir=<Full path to directory> orgid=<Webex org ID> auth=<Value of Authorization under ''> userid=<CEC userid> rag=<RAG configuration in a file with full path> output=browser/output=<Full path of the file to save query/response> prompt/prompt=<Read prompts from a File (full path)>")
        print('\n' + "Notes:")
        print("---------------------------")
        print("1) orgid, auth and output are optional parameters. Rest are mandatory. If no output specified then output will printed on the screen." + '\n')
        print("2) Use 'prompt' (without =<PromptFile>) option, if you want to enter prompt at command line. Enter prompt or Type 'q' or 'quit' to quit." + '\n')
        print("3) Use 'output=browser option, if you want to see output in browser at http://127.0.0.1:5000 (Sometime you may need to start browser). Sometime you need to hit Enter one time to get to prompt CLI. Enter prompt or Type 'q' or 'quit' to quit. Also, for 'output=browser option, there is a file created in local directory with all prompts/responses - temp_output.txt." + '\n')
        print('\n' + "Before you start:")
        print("'Request RAGaaS API access' at https://cisco.sharepoint.com/sites/CIRCUIT/SitePages/API-RAG-options.aspx, to get the credentials to use this tool. You can request free tier to get started with GPT model GPT-4o mini. You will get credentials in Webex space in couple of days. Copy items in bold (Starting from 'Ingest API Key' to 'Search Client Secret' in a file to be passed in 'rag' argument to this tool."  + '\n')
        sys.exit()  

    if len(sys.argv) == 8:
        param = sys.argv[1].split("=")
        if param[0] == "csvdir":
            csvdir = param[1]
        param = sys.argv[2].split("=")
        if param[0] == "orgid":
            orgid = param[1]
        param = sys.argv[3].split("=")
        if param[0] == "auth":
            auth = param[1]
        param = sys.argv[4].split("=")
        if param[0] == "userid":
            userid = param[1]
        param = sys.argv[5].split("=")
        if param[0] == "rag":
            ragConfFile = param[1]
        param = sys.argv[6].split("=")
        if param[0] == "output":
            outputFile = param[1]
        param = sys.argv[7].split("=")
        if param[0] == "prompt":
            promptFile = param[1]
    elif len(sys.argv) == 6:
        param = sys.argv[1].split("=")
        if param[0] == "csvdir":
            csvdir = param[1]
        param = sys.argv[2].split("=")
        if param[0] == "userid":
            userid = param[1]
        param = sys.argv[3].split("=")
        if param[0] == "rag":
            ragConfFile = param[1]
        param = sys.argv[4].split("=")
        if param[0] == "output":
            outputFile = param[1]
        if '=' in sys.argv[5]:
            param = sys.argv[5].split("=")
            if param[0] == "prompt":
                promptFile = param[1]
        else: 
            if sys.argv[5] == "prompt":
                usePrompt = True
                #prompts = input("Enter prompt: ")
            elif sys.argv[5] == "web":
                web = True
    elif len(sys.argv) == 5:
        param = sys.argv[1].split("=")
        if param[0] == "csvdir":
            csvdir = param[1]
        param = sys.argv[2].split("=")
        if param[0] == "userid":
            userid = param[1]
        param = sys.argv[3].split("=")
        if param[0] == "rag":
            ragConfFile = param[1]
        if '=' in sys.argv[4]:
            param = sys.argv[4].split("=")
            if param[0] == "prompt":
                promptFile = param[1]
        else: 
            if sys.argv[4] == "prompt":
                usePrompt = True
                #prompts = input("Enter prompt: ")
            elif sys.argv[4] == "web":
                web = True
    else:
        sys.exit()

    try:
        conf = readRagConfFile(ragConfFile)
        RAGAAS_API_details = extract_API_details_for_RAGAAS(conf)

        project = RAGAAS_API_details["gcp_project"]
        topic_to_publish = "projects/" + project + "/topics/" + RAGAAS_API_details["pubsub_topic"]
        bucket_name = RAGAAS_API_details["gcs_bucket"]

        appKey = RAGAAS_API_details["ingest_api_key"]
        # gcs_bucket = <>
        client_id = RAGAAS_API_details["ingest_client_id"]
        client_secret = RAGAAS_API_details["ingest_client_secret"]

        os.environ["GOOGLE_CLOUD_PROJECT"] = project
        os.environ["PYTHONWARNINGS"]="ignore"

        url = "https://id.cisco.com/oauth2/default/v1/token"

        payload = f'client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        id_response = requests.request("POST", url, headers=headers, data=payload)
        #print(id_response.text)
        token_from_id = json.loads(id_response.text)['access_token']
        #token_from_id # Ajay Need to remove

        url = f"https://chat-ai.cisco.com/ragaas-admin/api/access_token/generate?appKey={appKey}"

        payload = {}
        headers = {
        'Authorization': f'Bearer {token_from_id}'
        }

        chat_ai_response = requests.request("GET", url, headers=headers, data=payload)

        #print(chat_ai_response.text)
        chat_ai_token = json.loads(chat_ai_response.text)['access_token']
        #chat_ai_token # Ajay Need to remove

        credentials = Credentials(chat_ai_token)

        ### Upload document and Ingres data
        RAGASS_ingest(csvdir, bucket_name, appKey, token_from_id, credentials, 'add')

        session_id = userid + str(random.randint(1, 4))
        request_id = userid + str(random.randint(1, 4))

        promptCount= 1
        cli_input = []
        ### Search
        if web == True:
            runweb()
        elif usePrompt:
            
            while (prompts != "q" or prompts != "quit"):
                if prompts:
                    RAGASS_Search(RAGAAS_API_details, prompts, userid, session_id ,request_id, outputFile, promptCount)
                    promptCount = promptCount +1 
                    prompts = ""
                else:
                    completer = WordCompleter(cli_input)
                    print('\n')
                    cli = '<ansigreen>' + "Enter prompt " + str(promptCount) + ": " + '</ansigreen>'
                    prompts = prompt(HTML(cli), completer=completer, key_bindings=bindings)
                    if prompts not in cli_input and prompts != "":
                        cli_input.append(prompts)

                    #prompts = input('\n' + "Enter prompt " + str(promptCount) + ": ")
                    if prompts == "q" or prompts == "quit":
                        RAGASS_ingest(csvdir, bucket_name, appKey, token_from_id, credentials, 'delete')
                        cli_quit = '<ansigreen>' + "Save prompts from this session in prompts.txt file (Y/y) or hit any key to exit: " + '</ansigreen>'
                        savePrompts = prompt(HTML(cli_quit))
                        if savePrompts == 'y' or savePrompts == 'Y':
                            try:
                                os.remove("prompts.txt")
                            except:
                                pass
                            with open("prompts.txt", "w") as file:
                                for elem in cli_input:
                                    file.write(str(elem + '\n'))
                        # Send email
                        if outputFile != "noemail":
                            
                            summary = "AIGeneratedSummary - " + userid + ", " + "cli" + ", " + str(promptCount - 1)
                            msg = MIMEMultipart()
                            msg['Subject'] = summary
                            msg['From'] = userid + "@cisco.com"
                            msg['To'] = "akgupta@cisco.com"

                            s = smtplib.SMTP('email.cisco.com')
                            s.sendmail(msg['From'], msg['To'], msg.as_string())
                            s.quit()
                        # Exit
                        sys.exit()

                    elif prompts:
                        RAGASS_Search(RAGAAS_API_details, prompts, userid, session_id ,request_id, outputFile, promptCount)
                        promptCount = promptCount +1
                        prompts = ""
        else:
            with open(promptFile, 'r') as file:
                for line in file:
                    time.sleep(5)
                    '''
                    if prompts:
                        prompts = prompts + '\n'
                    prompts = prompts + line.strip()
                    '''
                    RAGASS_Search(RAGAAS_API_details, line, userid, session_id ,request_id, outputFile, promptCount)
                    promptCount = promptCount +1
            
            # Send email
            if outputFile != "noemail":  
                summary = "AIGeneratedSummary - " + userid + ", " + "file" + ", " + str(promptCount -1)
                msg = MIMEMultipart()
                msg['Subject'] = summary
                msg['From'] = userid + "@cisco.com"
                msg['To'] = "akgupta@cisco.com"

                s = smtplib.SMTP('email.cisco.com')
                s.sendmail(msg['From'], msg['To'], msg.as_string())
                s.quit()
        
        ### Delete document
        RAGASS_ingest(csvdir, bucket_name, appKey, token_from_id, credentials, 'delete')
    except:
        pass

# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 

