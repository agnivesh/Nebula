import json
import os, stat
from io import BytesIO
import zipfile

import requests

from subprocess import Popen, PIPE
import subprocess

author = {
    "name": "gl4ssesbo1",
    "twitter": "https://twitter.com/gl4ssesbo1",
    "github": "https://github.com/gl4ssesbo1",
    "blog": "https://www.pepperclipp.com/"
}

needs_creds = True

variables = {
    "SERVICE": {
        "value": "none",
        "required": "true",
        "description": "The service that will be used to run the module. It cannot be changed."
    }
}

global device_code_request_json

description = "This module will try to get as many information on the user's account on O365, based on the its privileges."
aws_command = "No cli command"

def exploit(profile, callstoprofile):
    access_token = profile['azure_access_token']

    # --------------------------------------------------
    # Get user's Info
    # --------------------------------------------------
    curdir = os.getcwd()

    try:
        azurehoundURLBulk = requests.get("https://api.github.com/repos/BloodHoundAD/AzureHound/releases/latest").json()['assets']
        for url in azurehoundURLBulk:
            if  "linux-amd64.zip" in url['browser_download_url'] and not ".sha256" in url['browser_download_url']:
                print(url['browser_download_url'])

                if not os.path.exists("./.downloads"):
                    os.mkdir("./.downloads")

                os.chdir("./.downloads")

                r = requests.get(url['browser_download_url'], stream=True)

                z = zipfile.ZipFile(BytesIO(r.content))
                z.extractall()

                os.chmod("/nebula/.downloads/azurehound", stat.S_IRWXO)

                os.environ["AZURETOKEN"] = access_token

                #azurehoundCommand = ["/nebula/.downloads/azurehound", "list", "--jwt", access_token, "--json"] # > jsondump.json"
                #azurehoundCommand = "/nebula/.downloads/azurehound list --jwt $AZURETOKEN --json -o /nebula/.downloads/jsondump.json".split() # > jsondump.json"
                #print(access_token)
                azurehoundCommand = f"/nebula/.downloads/azurehound list --jwt {access_token} --json > /nebula/.downloads/jsondump.json" #.split(" ") # > jsondump.json"


                #print(azurehoundCommand)

                result = os.popen(azurehoundCommand).read()

                #with open("") as outfile:
                #process = Popen(azurehoundCommand, stdout=PIPE, stderr=PIPE, text=True)
                #process.wait()
                #for line in iter(process.stdout.readline, ''):
                #    result += line

                #p.wait()
                #result = process.communicate()[0]

                #subprocess.call(azurehoundCommand, shell=True)

                #result = os.popen(azurehoundCommand).read()
                #print(result)
                os.chdir(curdir)

                return {
                    "Tool": {"Tool": "AzureHound", "Outcome": "Finished Successfully", "ResultFile": "/nebula/.downloads/jsondump.json"}
                }

    except Exception as e:
        os.chdir(curdir)
        return {"error": str(e)}
