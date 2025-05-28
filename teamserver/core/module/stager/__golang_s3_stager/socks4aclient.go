package main

import (
    "bufio"
    "net"
    //"os"
    "strings"
)

func handleCommand(server net.Conn, mgmtserver string) {
    reader := bufio.NewReader(server)
    for {
        line, err := reader.ReadString('\n')
        if err != nil {
            return //"Server closed:" + err
        }

        parts := strings.Fields(line)
        if len(parts) != 3 || parts[0] != "FORWARD" {
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
        return //"Tunnel connect error:" + err

    }

    tunnel.Write([]byte(tunnelID + "\n"))

    remote, err := net.Dial("tcp", target)
    if err != nil {
        tunnel.Close()
        return //"Target connect error:" + err
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

func startSocks4aServer(target string, mgmtserver string) string {
    control, err := net.Dial("tcp", target)
    if err != nil {
        return "Control connect error:" + err.Error()
    }

    handleCommand(control, mgmtserver)
    return "Connected to server"
}
