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
	"POLICY-TYPE": {
		"value": "MANAGED",
		"required": "true",
        "description":"Set MANAGED for both AWS and Consumer Managed policies and INLINE for inline policies"
	},
	"POLICY-ID": {
		"value": "",
		"required": "true",
        "description":"The name for Inline Policies or ARN for Managed"
	},
	"USER-OR-ROLE": {
		"value": "",
		"required": "false",
        "description":"Only for Inline Policies. Set it to USER for User Inline Policy or ROLE for Role Inline Policy"
	},
	"IDENTITY-NAME": {
		"value": "",
		"required": "false",
        "description":"The name of the identity to get the policy from. If not set, the current identity name will be used"
	}
}
description = "Just get a user's info. This was used as a demo on BlackHat Arsenal 2024 and DEF CON Demo Labs 2024"

aws_command = ""

def exploit(all_sessions, cred_prof, useragent, web_proxies, callstoprofile):
	try:
		policyName = variables['POLICY-ID']['value']
		policyType = variables['POLICY-TYPE']['value']
		userOrRole = variables['USER-OR-ROLE']['value']
		idName = variables['IDENTITY-NAME']['value']

		if policyType != "MANAGED" and policyType != "INLINE":
			return {"error": "POLICY-TYPE should be MANAGED or INLINE"}


		iamProfile = giveMeClient(
			all_sessions,
			cred_prof,
			useragent,
			web_proxies,
			"iam"
		)

		if policyType == "MANAGED":
			policyDict = iamProfile.get_policy(
				PolicyArn=policyName
			)
			DefaultVersionId = policyDict['DefaultVersionId']

			policyDoc = iamProfile.get_policy_version(
				PolicyArn=policyName,
				VersionId=DefaultVersionId
			)
			return_dict = {
				"PolicArn": policyName,
				"Document": policyDoc['PolicyVersion']['Document'],
				'VersionId': policyDoc['PolicyVersion']['VersionId'],
				'IsDefaultVersion': policyDoc['PolicyVersion']['IsDefaultVersion']
			}

			return {"PolicArn": return_dict}

		elif policyType == "INLINE":
			if idName == "":
				stsProfile = giveMeClient(
					all_sessions,
					cred_prof,
					useragent,
					web_proxies,
					"sts"
				)
				gci = stsProfile.get_caller_identity()
				arn = gci['Arn']
				if arn.split(":").strip()[5].split("/")[0] == "user":
					idName = arn.split(":").strip()[5].split("/")[1]
					userOrRole = "USER"
				elif arn.split(":")[5].strip().split("/")[0] == "assumed-role":
					idName = arn.split(":")[5].strip().split("/")[1]
					userOrRole = "ROLE"
				else:
					return {"error": "Not user or Role"}

			if userOrRole != "USER" and userOrRole != "ROLE":
				return {"error": "USER-OR-ROLE should be either USER or ROLE"}

			elif userOrRole == "USER":
				policyDoc = iamProfile.get_user_policy(
					PolicyArn=policyName,
					UserName=idName
				)
			else:
				policyDoc = iamProfile.get_role_policy(
					PolicyArn=policyName,
					RoleName=idName
				)

				return {"PolicName": policyDoc}

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



	except Exception as e:
		return {"error": str(e)}
