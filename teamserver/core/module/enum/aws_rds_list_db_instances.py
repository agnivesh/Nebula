import sys

from mongoengine import DoesNotExist

from core.database.models import AWSRDSDBInstances

author = {
    "name": "gl4ssesbo1",
    "twitter": "https://twitter.com/gl4ssesbo1",
    "github": "https://github.com/gl4ssesbo1",
    "blog": "https://www.pepperclipp.com/"
}

needs_creds = True

variables = {
    "SERVICE": {
        "value": "rds",
        "required": "true",
        "description": "The service that will be used to run the module. It cannot be changed."
    }
}

description = "Get a list of all the RDS DB Instances."

calls = [
    'rds:DescribeDBInstances'
]

aws_command = "aws rds describe-db-instances --profile <prefix>"


def exploit(profile, callstoprofile):
    try:
        response = profile.describe_db_instances()
        all_db_instances = response['DBInstances']
        while "Marker" in all_db_instances:
            response = profile.describe_db_instances(
                Marker=response['Marker']
            )
            all_db_instances.extend(response['DBInstances'])

        if len(all_db_instances) > 0:
            for db_instance in all_db_instances['Buckets']:
                db_name = db_instance['DBInstanceIdentifier']
                del(db_instance['DBInstanceIdentifier'])
                database_data = {
                    "aws_rds_instance_identifier": db_name,
                    "aws_rds_instance_document": db_instance
                }

                try:
                    aws_user = AWSRDSDBInstances.objects.get(aws_rds_instance_identifier=database_data)
                    aws_user.modify(**database_data)
                    aws_user.save()

                except DoesNotExist:
                    AWSRDSDBInstances(**database_data).save()

                except Exception as e:
                    return {"error": "Error from module: {}".format(str(e))}, 500

        return {
           "DBInstanceIdentifier": all_db_instances
        }, 200

    except Exception as e:
        return {"error": "Error from module: {}".format(str(e))}, 500
