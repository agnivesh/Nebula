package main

import (
    "strings"
    "os"
    "syscall"
)

func isPrivileged() string {
	data, err := os.ReadFile("/proc/1/status")
	if err != nil {
		return "Could not read /proc/1/status"
	}
	if strings.Contains(string(data), "CapEff:\t0000003fffffffff") {
		return "All capabilities enabled — possibly running with --privileged"
	}
	return "Not Vulnerable"
}

func hasDockerSocket() string {
	if _, err := os.Stat("/var/run/docker.sock"); err == nil {
		return "Docker Socket mounted"
	}
	return "Not Vulnerable"
}

func hasSysAdminCap() string {
	data, err := os.ReadFile("/proc/self/status")
	if err != nil {
		return "Not Vulnerable. Could not read /proc/self/status"
	}
	for _, line := range strings.Split(string(data), "\n") {
		if strings.HasPrefix(line, "CapEff:") {
			val := strings.TrimSpace(strings.TrimPrefix(line, "CapEff:"))
			if len(val) >= 8 && val[len(val)-8:] != "00000000" {
				return "Effective capabilities may include SYS_ADMIN"
			}
		}
	}
	return "Not Vulnerable"
}

func isHostPidNamespace() string {
	hostInit, _ := os.Readlink("/proc/1/ns/pid")
	selfInit, _ := os.Readlink("/proc/self/ns/pid")
	if hostInit == selfInit {
		return "Container shares host PID namespace"
	}
	return "Not Vulnerable"
}

func canAccessHostRoot() string {
	if _, err := os.Stat("/host/etc/passwd"); err == nil {
		return "/host mounted, possible host FS access"
	}
	return "Not Vulnerable"
}

func isProcWritable() string {
	err := syscall.Access("/proc/sys/kernel/randomize_va_space", syscall.O_RDWR)
	if err == nil {
		return "/proc is writable"
	}
	return "Not Vulnerable"
}

func isAppArmorUnconfined() string {
	data, err := os.ReadFile("/proc/self/attr/current")
	if err != nil {
		return "Not Vulnerable. Could not read AppArmor status"
	}
	if strings.Contains(string(data), "unconfined") {
		return "AppArmor profile is unconfined"
	}
	return "Not Vulnerable"
}

func isSELinuxDisabled() string {
	data, err := os.ReadFile("/sys/fs/selinux/enforce")
	if err != nil || string(data) == "0\n" {
		return "SELinux is disabled"
	}
	return "Not Vulnerable"
}

func isHostNetworkNamespace() string {
	hostNet, _ := os.Readlink("/proc/1/ns/net")
	selfNet, _ := os.Readlink("/proc/self/ns/net")
	if hostNet == selfNet {
		return "Container shares host network namespace"
	}
	return "Not Vulnerable"
}

func isVulnerableRunC() string {
	stat, err := os.Stat("/proc/self/exe")
	if err != nil {
		return "Not Vulnerable. Can't access /proc/self/exe"
	}
	if stat.Mode()&os.ModeSymlink != 0 {
		return "Possible CVE-2019-5736 exposure via /proc/self/exe"
	}
	return "Not Vulnerable"
}

func runAllScanners() string {
    return "Docker Scanner:\n" +
    "\tPrivileged Container" + isPrivileged() + "\n" +
    "\tDocker Socket Mount" + hasDockerSocket() + "\n" +
    "\tCAP_SYS_ADMIN" + hasSysAdminCap() + "\n" +
    "\tHost PID Namespace" + isHostPidNamespace() + "\n" +
    "\tAccess Host FS" + canAccessHostRoot() + "\n" +
    "\tWritable /proc" + isProcWritable() + "\n" +
    "\tAppArmor Status" + isAppArmorUnconfined() + "\n" +
    "\tSELinux Status" + isSELinuxDisabled() + "\n" +
    "\tHost Network NS" + isHostNetworkNamespace() + "\n" +
    "\trunc CVE-2019-5736" + isVulnerableRunC()
}