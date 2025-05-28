package main

import (
    "bufio"
    "fmt"
    "net"
    "os"
    "strings"
)

func handleCommand(server net.Conn, mgmtserver string) {
    reader := bufio.NewReader(server)
    for {
        line, err := reader.ReadString('\n')
        if err != nil {
            fmt.Println("Server closed:", err)
            return
        }

        parts := strings.Fields(line)
        if len(parts) != 3 || parts[0] != "FORWARD" {
            fmt.Println("Invalid command:", line)
            continue
        }

        tunnelID := parts[1]
        target := parts[2]

        go establishTunnel(tunnelID, target, mgmtserver)
    }
}

func establishTunnel(tunnelID, target string, mgmtserver string) {
    tunnel, err := net.Dial("tcp", mgmtserver) // Replace with real server IP
    if err != nil {
        fmt.Println("Tunnel connect error:", err)
        return
    }

    tunnel.Write([]byte(tunnelID + "\n"))

    remote, err := net.Dial("tcp", target)
    if err != nil {
        fmt.Println("Target connect error:", err)
        tunnel.Close()
        return
    }

    go proxy(tunnel, remote)
    go proxy(remote, tunnel)
}

func proxy(dst, src net.Conn) {
    defer dst.Close()
    defer src.Close()
    buf := make([]byte, 4096)
    for {
        n, err := src.Read(buf)
        if err != nil {
            return
        }
        if _, err := dst.Write(buf[:n]); err != nil {
            return
        }
    }
}

func startSocks4aServer(target string, mgmtserver string) {
    control, err := net.Dial("tcp", target)
    if err != nil {
        fmt.Println("Control connect error:", err)
        os.Exit(1)
    }

    fmt.Println("Connected to server")
    handleCommand(control, mgmtserver)
}
