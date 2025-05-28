import base64
import random

from termcolor import colored
import os
import botocore

def _get_proxies(self, url):
    return proxy_definitions

import boto3

def enter_credentials(service, access_key_id, secret_key, region, ua, proxy_definitions):
    args = {
        "service_name": service,
        "region_name": region,
        "aws_access_key_id": access_key_id,
        "aws_secret_access_key": secret_key
    }

    session_config_args = {}

    """if not len(proxy_definitions) == 0:
        web_proxy = random.choice(proxy_definitions)

        for key, value in web_proxy.items():
            proxy_config = {
                # "http": key.split('//')[1],
                key.split('//')[0]: key.split('//')[1]
                # key.split("//")[0]: key.split('//')[1]
            }

            with open("/tmp/cert.pem", 'w') as certfile:
                certfile.write(base64.b64decode(value.encode()).decode())

            proxy_configurations = {
                'proxy_client_cert': "/tmp/cert.pem"
            }
            session_config_args["proxies"] = proxy_config
            session_config_args["proxies_config"] = proxy_configurations
            # session_config_args["proxies"] = proxy_definitions"""

    if proxy_definitions is not None:
        #print(proxy_definitions)
        #session_config_args["proxies"] = proxy_definitions
        if "socks4" in proxy_definitions:
            os.environ['HTTP_PROXY'] = f"socks4://{proxy_definitions['socks4']}"
            #os.environ['HTTPS_PROXY'] = f"socks4://{proxy_definitions['socks4']}"

        elif "socks5" in proxy_definitions:
            os.environ['HTTP_PROXY'] = f"socks5://{proxy_definitions['socks5']}"
            #os.environ['HTTPS_PROXY'] = f"socks5://{proxy_definitions['socks5']}"

        elif "http" in proxy_definitions:
            os.environ['HTTP_PROXY'] = f"http://{proxy_definitions['http']}"
            #os.environ['HTTPS_PROXY'] = f"socks4://{proxy_definitions['socks4']}"
        # export https_proxy=socks5://127.0.0.1:50010 http_proxy=socks5://127.0.0.1:50010

        #import botocore.endpoint
        #botocore.endpoint.EndpointCreator._get_proxies = _get_proxy

    if not ua == "":
        session_config_args["user_agent"] = ua

    if not session_config_args == {}:
        session_config = botocore.config.Config(**session_config_args)
        args["config"] = session_config

    return boto3.client(**args)


def enter_credentials_with_session_token(service, access_key_id, secret_key, region, session_token, ua,
                                         proxy_definitions):
    args = {
        "service_name": service,
        "region_name": region,
        "aws_access_key_id": access_key_id,
        "aws_secret_access_key": secret_key,
        "aws_session_token": session_token
    }

    session_config_args = {}

    if not len(proxy_definitions) == 0:
        web_proxy = random.choice(proxy_definitions)

        session_config_args["proxies"] = {
            web_proxy.split(":")[0]: web_proxy
        }
        # session_config_args["proxies"] = proxy_definitions

    if not ua == "":
        session_config_args["user_agent"] = ua

    if not session_config_args == {}:
        session_config = botocore.config.Config(**session_config_args)
        args["config"] = session_config

    return boto3.client(**args)


def enter_session(session_name, region, service, ua, proxy_definitions):
    boto_session = boto3.session.Session(profile_name=session_name, region_name=region)
    args = {
        "service_name": service,
    }

    session_config_args = {}

    if not len(proxy_definitions) == 0:
        web_proxy = random.choice(proxy_definitions)

        session_config_args["proxies"] = {
            web_proxy.split(":")[0]: web_proxy
        }

    if not ua == "":
        session_config_args["user_agent"] = ua

    if not session_config_args == {}:
        session_config = botocore.config.Config(**session_config_args)
        args["config"] = session_config

    return boto_session.client(**args)


def giveMeClient(all_sessions, cred_prof, useragent, web_proxies, service):
    sess = {}
    proxy_definitions = web_proxies

    if cred_prof == "":
        return {"error": ("{}{}{}{}".format(
            colored("[*] No credentials set. Use '", 'red'),
            colored("set aws-credentials", "blue"),
            colored("' or '", "red"),
            colored("set azure-credentials", "blue"),
            colored("' to set credentials.", "red")
        ))}
    else:
        for session in all_sessions:
            if session['profile'] == cred_prof:
                sess = session
                break

        for key, value in sess.items():
            if key == 'session_token':
                continue
            elif key == 'region' and value == "":
                return {"error": ("{}{}{}".format(
                    colored("[*] No region set. Use '", 'red'),
                    colored("set region <region>", "blue"),
                    colored("' to set a region.", "red")
                ))}

            elif value == "":
                return {"error": ("{}{}{}".format(
                    colored("[*] '", 'red'),
                    colored(key, "blue"),
                    colored("' not set. Check credentials.", "red")
                ))}

        if not 'session_token' in sess:
            profile = enter_credentials(
                service,
                sess['access_key_id'],
                sess['secret_key'],
                sess['region'],
                useragent,
                proxy_definitions
            )
            return profile

        elif 'session_token' in sess and sess['session_token'] != "":
            profile = enter_credentials_with_session_token(
                service,
                sess['access_key_id'],
                sess['secret_key'],
                sess['region'],
                sess['session_token'],
                useragent,
                proxy_definitions
            )

            return profile

        else:
            return {"error": (colored("[*] Check if the session key is empty.", "yellow"))}
