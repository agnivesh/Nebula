import sys

from mongoengine import DoesNotExist

from core.database.models import AWSS3Bucket

author = {
    "name": "gl4ssesbo1",
    "twitter": "https://twitter.com/gl4ssesbo1",
    "github": "https://github.com/gl4ssesbo1",
    "blog": "https://www.pepperclipp.com/"
}

needs_creds = True

variables = {
    "SERVICE": {
        "value": "s3",
        "required": "true",
        "description": "The service that will be used to run the module. It cannot be changed."
    }
}

description = "Check all the versions of the objects of a bucket or a list of buckets and find deleted files. Then, you can use exploit/aws_s3_get_object to download the files. The module is based of the RedBoto script: aws_s3_list_deleted_files.py"

calls = [
    's3:ListAllMyBuckets'
]

aws_command = "aws s3api list-buckets --profile <prefix>"


def exploit(profile, callstoprofile):
    return_dict = {
        "Name": []
    }

    try:
        response = profile.list_buckets()
        all_buckets = response['Buckets']
        while "ContinuationToken" in all_buckets:
            response = profile.list_buckets(
                ContinuationToken=response['ContinuationToken']
            )
            all_buckets.extend(response['Buckets'])

        if len(all_buckets) > 0:
            for bucket in all_buckets:
                database_data = {
                    "aws_s3_bucket_name": bucket['Name'],
                    "aws_s3_creation_date": bucket['CreationDate'],
                    "aws_s3_region": bucket['BucketRegion']
                }
                return_dict["Name"].append(bucket)

                try:
                    aws_user = AWSS3Bucket.objects.get(aws_s3_bucket_name=bucket['Name'])
                    aws_user.modify(**database_data)
                    aws_user.save()

                except DoesNotExist:
                    AWSS3Bucket(**database_data).save()

                except Exception as e:
                    return {"error": "Error from module: {}".format(str(e))}, 500

        return {
                   "Name": return_dict
               }, 200


    except Exception as e:
        return {"error": "Error from module: {}".format(str(e))}, 500
