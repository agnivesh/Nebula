import json
import sys
import requests
import random
import string
from flask_mongoengine import DoesNotExist
import datetime

from core.database.models import AZURECredentials

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
    },
    "USER-ID-OR-UPN": {
        "value": "",
        "required": "true",
        "description": "The ID of the user to add or its User Principal Name."
    },
    "GROUP-ID": {
        "value": "",
        "required": "true",
        "description": "The service that will be used to run the module. It cannot be changed."
    }

}

description = "This module will to add a user to a group in AzureAD"
aws_command = "No cli command"

def exploit(profile, callstoprofile):
    access_token = profile['azure_access_token']

    user_id_or_upn = variables['USER-ID-OR-UPN']['value']
    group_id = variables['GROUP-ID']['value']

    try:

        data = {
            "@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/{}".format(user_id_or_upn)
        }

        output = requests.post("https://graph.microsoft.com/v1.0/groups/{}/members/$ref".format(group_id),
                           headers={
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer {}'.format(access_token),
                                },
                                json=data
                                )

        if output.status_code == 204:
            return {"error": "Done"}

        else:
            return {"error": output.text}

    except Exception as e:
        return {"error": str(e)}
