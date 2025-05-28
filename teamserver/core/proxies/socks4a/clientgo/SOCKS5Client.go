// agent.go
package main

import (
	//"encoding/binary"
	//"fmt"
	"io"
	"log"
	"net"
	"strings"
)

func main() {
	ctrlConn, err := net.Dial("tcp", "127.0.0.1:9000")
	if err != nil {
		log.Fatal(err)
	}
	defer ctrlConn.Close()

	for {
		buf := make([]byte, 1024)
		n, err := ctrlConn.Read(buf)
		if err != nil {
			log.Println("Lost connection to server:", err)
			break
		}

		parts := strings.SplitN(string(buf[:n]), " ", 3)
		if len(parts) < 3 || parts[0] != "FORWARD" {
			log.Println("Invalid command")
			continue
		}

		connID := parts[1]
		target := parts[2]
		go handleTunnel(ctrlConn, connID, target)
	}
}

func handleTunnel(ctrlConn net.Conn, connID, target string) {
	local, err := net.Dial("tcp", target)
	if err != nil {
		log.Println("Failed to connect to target:", err)
		return
	}

	// Start data connection to server for this tunnel
	dataConn, err := net.Dial("tcp", "your.server.ip:9001")
	if err != nil {
		log.Println("Data channel connection failed:", err)
		return
	}

	// Send tunnel ID
	dataConn.Write([]byte(connID + "\n"))

	go io.Copy(local, dataConn)
	io.Copy(dataConn, local)
}
