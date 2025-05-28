import datetime
import json
from mongoengine import DoesNotExist
from core.database.models import AWSUsers
from core.createSession.giveMeClient import giveMeClient

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
	}
}
description = "Just get a user's info. This was used as a demo on BlackHat Arsenal 2024 and DEF CON Demo Labs 2024"

aws_command = "aws iam get-user --user-name <user>  --region <region> --profile <profile>"

calls = [
	"iam:GetUser"
]

def exploit(all_sessions, cred_prof, useragent, web_proxies, callstoprofile):
	try:
		iamProfile = giveMeClient(
			all_sessions,
			cred_prof,
			useragent,
			web_proxies,
			"iam"
		)
		ctProfile = giveMeClient(
			all_sessions,
			cred_prof,
			useragent,
			web_proxies,
			"cloudtrail"
		)

		userlist = iamProfile.list_users()
		users = userlist['Users']

		while userlist['IsTruncated']:
			userlist = iamProfile.list_users(Marker=userlist['Marker'])
			users.extend(userlist['Users'])


		compromisedUsers = []

		for user in users:
			attached_policies = iamProfile.list_attached_user_policies(UserName=user['UserName'])
			for attached_policy in attached_policies['AttachedPolicies']:
				if "AWSCompromisedKeyQuarantine" == attached_policy['PolicyName'] \
				or "AWSCompromisedKeyQuarantineV2" == attached_policy['PolicyName'] \
				or "AWSCompromisedKeyQuarantineV3" == attached_policy['PolicyName']:
					compromisedUsers.append({
						"UserName": user['UserName'],
						"UserArn": user['Arn'],
						"QuarantinePolicy": attached_policy['PolicyName']
					})

					database_data = {
						"aws_username": user['UserName'],
						"aws_user_arn": user['Arn'],
						"aws_user_id": user['UserId'],
						"aws_user_create_date": user['CreateDate'],
						"aws_account_id": user['Arn'].split(":")[4],
						"aws_user_is_compromised": True
					}

					try:
						aws_user = AWSUsers.objects.get(aws_username=user['UserName'])
						aws_user.modify(**database_data)
						aws_user.save()

					except DoesNotExist:
						AWSUsers(**database_data).save()

					except Exception as e:
						return {"error": "Error from module: {}".format(str(e))}, 500

		logscompromised = findUsersByLogs(ctProfile)

		if logscompromised is not None:
			for loguser in logscompromised:
				check = 0
				for founduser in compromisedUsers:
					if loguser == founduser['UserName']:
						check = 1
						continue
				if check == 0:
					userinfo = iamProfile.get_user(UserName=loguser)
					database_data = {
						"aws_username": userinfo['UserName'],
						"aws_user_arn": userinfo['Arn'],
						"aws_user_id": userinfo['UserId'],
						"aws_user_create_date": userinfo['CreateDate'],
						"aws_account_id": userinfo['Arn'].split(":")[4],
						"aws_user_is_compromised": True
					}

					try:
						aws_user = AWSUsers.objects.get(aws_username=userinfo['UserName'])
						aws_user.modify(**database_data)
						aws_user.save()

					except DoesNotExist:
						AWSUsers(**database_data).save()

					except Exception as e:
						return {"error": "Error from module: {}".format(str(e))}, 500
		return {"UserName": compromisedUsers}

	except Exception as e:
		return {"error": str(e)}


def findUsersByLogs(ctProfile):
	startTime = datetime.datetime.now() - datetime.timedelta(days=90)
	try:
		response = ctProfile.lookup_events(
			LookupAttributes=[
				{
					'AttributeKey': 'EventName',
					'AttributeValue': 'AttachUserPolicy'
				}
			],
			StartTime=startTime
		)
		logs = response['Events']

		while "NextToken" in response:
			response = ctProfile.lookup_events(
				LookupAttributes=[
					{
						'AttributeKey': 'EventName',
						'AttributeValue': 'AttachUserPolicy'
					}
				],
				StartTime=startTime,
				NextToken=response["NextToken"]
			)
			logs.extend(response['Events'])

		importantEvents = []
		for event in logs:
			user = ""
			policy = ""
			username = event['Username']
			eventData = json.loads(event['CloudTrailEvent'])
			if "errorCode" in eventData and "errorMessage" in eventData:
				if (
						(eventData['errorCode'] == "AccessDenied") and
						(username in eventData['errorMessage'].split(":")[9]) and
						(eventData['sourceIPAddress'] == "AWS Internal") and
						(eventData['sourceIPAddress'] == "AWS Internal")
				):
					importantEvents.append(username)
			else:
				for resource in event['Resources']:
					if resource['ResourceType'] == "AWS::IAM::User":
						user = resource['ResourceName']
					elif resource['ResourceType'] == "AWS::IAM::Policy":
						policy = resource['ResourceName']

				if (user == username and
						(policy == "arn:aws:iam::aws:policy/AWSCompromisedKeyQuarantineV2" or
						 policy == "arn:aws:iam::aws:policy/AWSCompromisedKeyQuarantineV3" or
						 policy == "arn:aws:iam::aws:policy/AWSCompromisedKeyQuarantine") and
						(eventData['sourceIPAddress'] == "AWS Internal") and
						(eventData['sourceIPAddress'] == "AWS Internal")
				):
					importantEvents.append(username)

		return list(set(importantEvents))

	except:
		return None