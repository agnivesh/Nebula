package main

import (
	"io/ioutil"
	"os"
)

func readKubeTokenFile() string {
    path := "/var/run/secrets/kubernetes.io/serviceaccount/token"

	// Check if the file exists
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return "Token file does not exist"
	}

	// Read the file
	data, err := ioutil.ReadFile(path)
	if err != nil {
		return "Failed to read Token file: " + err.Error()
	}

	return string(data)
}

