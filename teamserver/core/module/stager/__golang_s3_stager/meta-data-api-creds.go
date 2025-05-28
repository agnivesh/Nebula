package main

import (
    "net/http"
    "io"
    "fmt"
)

func awsIMDS(endpoint string) string {
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
				metaReq, _ := http.NewRequest("GET", "http://169.254.169.254/latest/meta-data/" + endpoint, nil)
				metaReq.Header.Set("X-aws-ec2-metadata-token", token)
				metaResp, err := client.Do(metaReq)
				if err == nil && metaResp.StatusCode == 200 {
					defer metaResp.Body.Close()
					body, _ := io.ReadAll(resp.Body)
		            return string(body)
				}
			}
		}
	}

	// Fallback: Try IMDSv1
	resp, err := client.Get("http://169.254.169.254/latest/meta-data/")
	if err == nil && resp.StatusCode == 200 {
		defer resp.Body.Close()
		body, _ := io.ReadAll(resp.Body)
		return string(body)
	}

	return ""
}


func gcpIMDS() string {
	url := "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return err.Error()
	}
	req.Header.Set("Metadata-Flavor", "Google")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err.Error()
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return string(body)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err.Error()
	}

	return string(body)
}

func azureIMDS(resource string) string {
	url := fmt.Sprintf("http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=%s", resource)

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return err.Error()
	}
	req.Header.Set("Metadata", "true")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err.Error()
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return string(body)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err.Error()
	}

	return string(body)
}