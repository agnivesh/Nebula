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
	},
	"USER-NAME": {
		"value": "",
		"required": "false",
        "description":"The IAM User to check. If you do not fill this argument, a list of users will be taken using iam:ListUsers."
	},
	"PERMISSIONS-FILE": {
		"value": "",
		"required": "true",
        "description":"The filepath of the privileges to check as <service>:<privilege>. Example: iam:ListUsers.",
		"iswordlist": True,
		"wordlistvalue": [],
	}
}
description = "Just get a user's info. This was used as a demo on BlackHat Arsenal 2024 and DEF CON Demo Labs 2024"

aws_command = ""

calls = [
	"iam:ListUsers",
	"iam:ListGroupsForUser",
	"iam:ListUserAttachedPolicies",
	"iam:ListGroupAttachedPolicies",
	"iam:ListUserPolicies",
	"iam:ListGroupPolicies",
	"iam:GetPolicyVersion",
	"iam:SimulateCustomPolicy"
]

def exploit(all_sessions, cred_prof, useragent, web_proxies, callstoprofile):
	try:
		userName = variables['USER-NAME']['value']
		SCENARIOS = variables['PERMISSIONS-FILE']['wordlistvalue']

		iamProfile = giveMeClient(
			all_sessions,
			cred_prof,
			useragent,
			web_proxies,
			"iam"
		)

		if userName == "":
			userListReq = iamProfile.list_users()['Users']
			userList = []
			for userReq in userListReq:
				userList.append(userReq['UserName'])
		else:
			userList = [userName]

		returnDict = []
		for user in userList:
			userinfo = {
				"UserName": user,
				"PermissionCheck": simulateSingleUserPolicies(iamProfile, user, SCENARIOS)
			}
			returnDict.append(userinfo)

		"""database_data = {
			"aws_username": user['UserName'],
			"aws_user_arn": user['Arn'],
			"aws_user_id": user['UserId'],
			"aws_user_create_date": user['CreateDate'],
			"aws_account_id": user['Arn'].split(":")[4]
		}

		try:
			aws_user = AWSUsers.objects.get(aws_username=user['UserName'])
			aws_user.modify(**database_data)
			aws_user.save()

		except DoesNotExist:
			AWSUsers(**database_data).save()

		except Exception as e:
			return {"error": "Error from module: {}".format(str(e))}, 500"""

		return {"UserName": returnDict}

	except Exception as e:
		return {"error": str(e)}


def simulateSingleUserPolicies(iamClient, user, SCENARIOS):
	try:
		permissionBoundary = get_user_permission_boundary(iamClient, user)
		#if permissionBoundary is not None:
		#	permissionBoundary = [json.dumps(permissionBoundary)]
		attachedUserPolicies = get_attached_user_policies(iamClient, user)
		inlineUserPolicies = get_user_inline_policies(iamClient, user)

		policylist = []
		for attupolicy in attachedUserPolicies:
			policylist.append(json.dumps(attupolicy))

		for inupolicy in inlineUserPolicies:
			policylist.append(json.dumps(inupolicy))

		userGroups = get_user_groups(iamClient, user)
		if userGroups is not None:
			for group in userGroups:
				attachedGroupPolicies = get_attached_group_policies(iamClient, group)
				inlineGroupPolicies = get_group_inline_policies(iamClient, group)
				for attupolicy in attachedGroupPolicies:
					policylist.append(json.dumps(attupolicy))

				for ingpolicy in inlineGroupPolicies:
					policylist.append(json.dumps(ingpolicy))


		validationargs = {
			"iamClient": iamClient,
			"permissionBoundaryList": permissionBoundary,
			"SCENARIOS": SCENARIOS,
			"policyDocumentList": policylist
		}

		return find_permissions_in_policy(
			**validationargs
		)
	except Exception as e:
		return {"error": str(e)}


def get_user_permission_boundary(iamClient, user):
	try:
		policies = iamClient.get_user(UserName=user)['User']
		policyDoc = None
		if 'PermissionsBoundary' in policies:
			policyarn = policies['PermissionsBoundary']['PermissionsBoundaryArn']
			try:
				policyVersion = iamClient.get_policy(PolicyArn=policyarn)['Policy']["DefaultVersionId"]
				policyDoc = [json.dumps(iamClient.get_policy_version(PolicyArn=policyarn, VersionId=policyVersion)['PolicyVersion']['Document'])]
			except:
				return None
		return policyDoc
	except iamClient.exceptions.NoSuchEntityException:
		return None


def get_attached_user_policies(iamClient, user):
	try:
		policies = iamClient.list_attached_user_policies(UserName=user)['AttachedPolicies']
		
		policydocs = []
		if len(policies) > 0:
			for policyarn in policies:
				# if policyarn['PolicyArn'] == "arn:aws:iam::aws:policy/AWSCompromisedKeyQuarantineV2" or \
				# policyarn['PolicyArn'] == "arn:aws:iam::aws:policy/AWSCompromisedKeyQuarantine":
				#    continue
				try:
					policyVersion = iamClient.get_policy(PolicyArn=policyarn['PolicyArn'])['Policy'][
						"DefaultVersionId"]
					policyDoc = \
					iamClient.get_policy_version(PolicyArn=policyarn['PolicyArn'], VersionId=policyVersion)[
						'PolicyVersion']['Document']
					policydocs.append(policyDoc)
				except Exception as e:
					return None
		return policydocs
	except:
		
		return None


def get_user_inline_policies(iamClient, user):
	try:
		policies = iamClient.list_user_policies(UserName=user)['PolicyNames']
		policydocs = []
		for policy in policies:
			policydocs.append(iamClient.get_user_policy(UserName=user, PolicyName=policy)['PolicyDocument'])
		return policydocs
	except:
		return None


def get_user_groups(iamClient, user):
	try:
		groups = iamClient.list_groups_for_user(UserName=user)['Groups']
		return groups
	except:
		return None


def get_attached_group_policies(iamClient, group):
	try:
		policies = iamClient.list_attached_group_policies(GroupName=group['GroupName'])['AttachedPolicies']
		policydocs = []
		if len(policies) > 0:
			for policyarn in policies:
				try:
					policyVersion = iamClient.get_policy(PolicyArn=policyarn['PolicyArn'])['Policy'][
						"DefaultVersionId"]
					policyDoc = \
					iamClient.get_policy_version(PolicyArn=policyarn['PolicyArn'], VersionId=policyVersion)[
						'PolicyVersion']['Document']
					policydocs.append(policyDoc)
				except Exception as e:
					return None
		return policydocs
	except:
		return None


def get_group_inline_policies(iamClient, group):
	policydocs = []
	try:
		policies = iamClient.list_group_policies(GroupName=group['GroupName'])['PolicyNames']
		for policy in policies:
			policydocs.append(
				iamClient.get_group_policy(GroupName=group['GroupName'], PolicyName=policy)['PolicyDocument'])
		return policydocs
	except Exception as e:
		return None


def find_permissions_in_policy(iamClient, policyDocumentList, SCENARIOS, permissionBoundaryList):
	returnDict = {}
	returnDict = {
		"allowed": [],
		"denied": []
	}
	try:
		if permissionBoundaryList is not None:
			evaluationResponse = iamClient.simulate_custom_policy(
				PolicyInputList=policyDocumentList,
				PermissionsBoundaryPolicyInputList=permissionBoundaryList,
				ActionNames=SCENARIOS
			)

		else:
			evaluationResponse = iamClient.simulate_custom_policy(
				PolicyInputList=policyDocumentList,
				ActionNames=SCENARIOS
			)

		for evaluation in evaluationResponse['EvaluationResults']:
			if evaluation['EvalDecision'] == "allowed":
				returnDict['allowed'].append(evaluation['EvalActionName'])
			else:
				returnDict['denied'].append(evaluation['EvalActionName'])

		return returnDict

	except Exception as e:
		return {"error": str(e)}

