import sys
import nmap
from core.database import models
import flask_mongoengine

author = {
    "name": "gl4ssesbo1",
    "twitter": "https://twitter.com/gl4ssesbo1",
    "github": "https://github.com/gl4ssesbo1",
    "blog": "https://www.pepperclipp.com/"
}

needs_creds = False

variables = {
    "SERVICE": {
        "value": "none",
        "required": "true",
        "description": "The service that will be used to run the module. It cannot be changed."
    },
    "CLUSTER": {
        "value": "",
        "required": "true",
        "description": "The cluster endpoint to check for"
    },
    "APISERVER_PORT": {
        "value": "443",
        "required": "true",
        "description": "Kubernetes API Server"
    },
    "ALTERNATIVE_APISERVER_PORT": {
        "value": "6443",
        "required": "true",
        "description": "Alternative Kubernetes API Server"
    },
    "INSECURE_APISERVER_PORT": {
        "value": "8080",
        "required": "true",
        "description": "Kubernetes API Server Insecure Port"
    },
    "MINIKUBE_APISERVER_PORT": {
        "value": "8443",
        "required": "true",
        "description": "MiniKube API Server"
    },
    "ETCD_PORT": {
        "value": "2379",
        "required": "true",
        "description": "etcd Port"
    },
    "ALTERNATIVE_ETCD_PORT": {
        "value": "6666",
        "required": "true",
        "description": "Alternative etcd Port"
    },
    "CADVISOR_PORT": {
        "value": "4194",
        "required": "true",
        "description": "cAdvisor Port"
    },
    "KUBELET_HTTPS_PORT": {
        "value": "10250",
        "required": "true",
        "description": "kubelet HTTPS API which allows full mode access"
    },
    "KUBELET_UNAUTH_PORT": {
        "value": "10255",
        "required": "true",
        "description": "kubelet Unauthenticated read-only HTTP port: pods, running pods and node state"
    },
    "KUBE_PROXY_PORT": {
        "value": "10256",
        "required": "true",
        "description": "Kube Proxy health check server"
    },
    "CALICO_FELIX_PORT": {
        "value": "9099",
        "required": "true",
        "description": "Health check server for Calico"
    },
    "WEAVE_PORT": {
        "value": "6782",
        "required": "true",
        "description": "weave metrics and endpoints"
    },
    "ALT_WEAVE_PORT": {
        "value": "6783",
        "required": "true",
        "description": "Alternative weave metrics and endpoints"
    },
    "OTHER_ALT_WEAVE_PORT": {
        "value": "6784",
        "required": "true",
        "description": "Alternative weave metrics and endpoints"
    }
}
description = "Checks for subdomains of the domain by enumerating certificates from crt.sh"

aws_command = "None"


def exploit(callstoprofile):
    try:
        APISERVER_PORT = int(variables['APISERVER_PORT']['value'])
        ALTERNATIVE_APISERVER_PORT = int(variables['ALTERNATIVE_APISERVER_PORT']['value'])
        INSECURE_APISERVER_PORT = int(variables['INSECURE_APISERVER_PORT']['value'])
        MINIKUBE_APISERVER_PORT = int(variables['MINIKUBE_APISERVER_PORT']['value'])
        ETCD_PORT = int(variables['ETCD_PORT']['value'])
        ALTERNATIVE_ETCD_PORT = int(variables['ALTERNATIVE_ETCD_PORT']['value'])
        CADVISOR_PORT = int(variables['CADVISOR_PORT']['value'])
        KUBELET_HTTPS_PORT = int(variables['KUBELET_HTTPS_PORT']['value'])
        KUBELET_UNAUTH_PORT = int(variables['KUBELET_UNAUTH_PORT']['value'])
        KUBE_PROXY_PORT = int(variables['KUBE_PROXY_PORT']['value'])
        CALICO_FELIX_PORT = int(variables['CALICO_FELIX_PORT']['value'])
        WEAVE_PORT = int(variables['WEAVE_PORT']['value'])
        ALT_WEAVE_PORT = int(variables['ALT_WEAVE_PORT']['value'])
        OTHER_ALT_WEAVE_PORT = int(variables['OTHER_ALT_WEAVE_PORT']['value'])

        cluster = variables['CLUSTER']['value']
        nm = nmap.PortScanner()
        ports = [
            # API Server
            APISERVER_PORT, # 443,
            ALTERNATIVE_APISERVER_PORT, # 6443,
            INSECURE_APISERVER_PORT, #8080,
            MINIKUBE_APISERVER_PORT, #8443,

            #etcd
            ETCD_PORT, #2379,
            ALTERNATIVE_ETCD_PORT, #6666,

            #cAdvisor
            CADVISOR_PORT, #4194,

            #kubelet
            KUBELET_HTTPS_PORT, #10250,
            KUBELET_UNAUTH_PORT, #10255,

            #kube proxy
            KUBE_PROXY_PORT, #10256,

            #calico-felix
            CALICO_FELIX_PORT, #9099,

            #weave
            WEAVE_PORT, #6782,
            ALT_WEAVE_PORT, #6783,
            OTHER_ALT_WEAVE_PORT, #6784
        ]
        ports_str = ','.join(map(str, ports))
        nm.scan(hosts=cluster, ports=ports_str)

        ports_open = {
            # API Server
            APISERVER_PORT: {
                "state": "",
                "service": "Kubernetes API Server"
            },
            ALTERNATIVE_APISERVER_PORT: {
                "state": "",
                "service": "Kubernetes API Server"
            },
            INSECURE_APISERVER_PORT: {
                "state": "",
                "service": "Kubernetes API Server Insecure Port"
            },
            MINIKUBE_APISERVER_PORT: {
                "state": "",
                "service": "MiniKube API Server"
            },

            # etcd
            ETCD_PORT: {
                "state": "",
                "service": "etcd"
            },
            ALTERNATIVE_ETCD_PORT: {
                "state": "",
                "service": "etcd"
            },

            # cAdvisor
            CADVISOR_PORT: {
                "state": "",
                "service": "cAdvisor"
            },

            # kubelet
            KUBELET_HTTPS_PORT: {
                "state": "",
                "service": "kubelet HTTPS API which allows full mode access"
            },
            KUBELET_UNAUTH_PORT: {
                "state": "",
                "service": "kubelet Unauthenticated read-only HTTP port: pods, running pods and node state"
            },

            # kube proxy
            KUBE_PROXY_PORT: {
                "state": "",
                "service": "Kube Proxy health check server"
            },

            # calico-felix
            CALICO_FELIX_PORT: {
                "state": "",
                "service": "Health check server for Calico"
            },

            # weave
            WEAVE_PORT: {
                "state": "",
                "service": "weave metrics and endpoints"
            },
            ALT_WEAVE_PORT: {
                "state": "",
                "service": "weave metrics and endpoints"
            },
            OTHER_ALT_WEAVE_PORT: {
                "state": "",
                "service": "weave metrics and endpoints"
            }
        }

        for port in ports:
            try:
                state = nm[cluster]['tcp'][port]['state']
                ports_open[port]["state"] = state

            except KeyError:
                ports_open[port]["state"] = "no info or filtered"


        database_data = {
            "kube_cluster_name": cluster,
            "kube_cluster_ports": ports_open
        }

        try:
            models.KubeCluster.objects().get(kube_cluster_name=cluster).update(**database_data)

        except flask_mongoengine.DoesNotExist:
            models.KubeCluster(**database_data).save()

        return ports_open, 200

    except Exception as e:
        return {"error": e}, 500