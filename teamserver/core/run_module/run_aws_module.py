import sys

from termcolor import colored
import os
import boto3, botocore
from inspect import signature

def setupProxy(botoSession):
    session = requests.Session()
    session.mount("http://", SOCKSAdapter())
    return SOCKSProxyManager(proxy, **kwargs)

def enter_credentials(service, access_key_id, secret_key, region, ua, proxy_definitions):
    args = {
        "service_name": service,
        "region_name": region,
        "aws_access_key_id": access_key_id,
        "aws_secret_access_key": secret_key
    }

    session_config_args = {}
    if proxy_definitions is not None:
        session_config_args["proxies"] = proxy_definitions

    if not ua == "":
        session_config_args["user_agent"] = ua
        session_config = botocore.config.Config(**session_config_args)
        args["config"] = session_config


    client = boto3.client(**args)
    return client

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

    if not proxy_definitions == None:
        session_config_args["proxies"] = proxy_definitions

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

    if not proxy_definitions == None:
        session_config_args["proxies"] = proxy_definitions

    if not ua == "":
        session_config_args["user_agent"] = ua

    if not session_config_args == {}:
        session_config = botocore.config.Config(**session_config_args)
        args["config"] = session_config

    return boto_session.client(**args)

def run_aws_module(imported_module, all_sessions, cred_prof, useragent, web_proxies, workspace, callstoprofile):
    sig = signature(imported_module.exploit)

    if len(sig.parameters) == 1 or len(sig.parameters) == 2:
        return run_aws_module_one_service(imported_module, all_sessions, cred_prof, useragent, web_proxies, workspace)
    elif len(sig.parameters) == 5:
        return imported_module.exploit(all_sessions, cred_prof, useragent, web_proxies, callstoprofile)

def run_aws_module_one_service(imported_module, all_sessions, cred_prof, useragent, web_proxies, workspace):
    service = imported_module.variables['SERVICE']['value']
    sess = {}

    if useragent != "":
        if os.path.exists(f"{os.environ.get('VIRTUAL_ENV')}/lib/python3.10/site-packages/botocore/session.py"):
            useragentfile = f"{os.environ.get('VIRTUAL_ENV')}/lib/python3.10/site-packages/botocore/.user-agent"
        elif os.path.exists(f"/usr/lib/python{sys.version.split('.')[0]}.{sys.version.split('.')[1]}/dist-packages/botocore/session.py"):
            useragentfile = f"/usr/lib/python{sys.version.split('.')[0]}.{sys.version.split('.')[1]}/dist-packages/botocore/.user-agent"
        elif os.path.exists(f"/usr/local/lib/python3.10/site-packages/botocore/session.py"):
            useragentfile = f"/usr/local/lib/python3.10/site-packages/botocore/.user-agent"
        else:
            useragentfile = None

        if useragentfile is not None:
            with open(useragentfile, "w") as uafile:
                uafile.write(useragent)
                uafile.close()

    proxy_definitions = {}

    if not web_proxies == []:
        for proxy in web_proxies:
            proxy_definitions[proxy.split(":")[0]] = proxy
    else:
        proxy_definitions = None

    if imported_module.needs_creds:
        c = 0
        if cred_prof == "":
            print("{}{}{}{}".format(
                colored("[*] No credentials set. Use '", 'red'),
                colored("set aws-credentials", "blue"),
                colored("' or '", "red"),
                colored("set azure-credentials", "blue"),
                colored("' to set credentials.", "red")
            ))
            c = 1
        else:
            for session in all_sessions:
                if session['profile'] == cred_prof:
                    sess = session

                for key, value in sess.items():
                    if key == 'session_token':
                        continue
                    elif key == 'region' and value == "":
                        print("{}{}{}".format(
                            colored("[*] No region set. Use '", 'red'),
                            colored("set region <region>", "blue"),
                            colored("' to set a region.", "red")
                        ))
                        c = 1
                    elif value == "":
                        print("{}{}{}".format(
                            colored("[*] '", 'red'),
                            colored("", "blue"),
                            colored("' not set. Check credentials.", "red")
                        ))
                        c = 1

            if c == 0:
                env_aws = {
                    "AWS_ACCESS_KEY": "",
                    "AWS_SECRET_KEY": "",
                    "AWS_SESSION_TOKEN": "",
                    "AWS_REGION": ""
                }
                if os.environ.get('AWS_ACCESS_KEY'):
                    env_aws['AWS_ACCESS_KEY'] = os.environ.get('AWS_ACCESS_KEY')
                    del os.environ['AWS_ACCESS_KEY']
                os.environ['AWS_ACCESS_KEY_ID'] = sess['access_key_id']
                os.environ['AWS_ACCESS_KEY'] = sess['access_key_id']

                if os.environ.get('AWS_SECRET_KEY'):
                    env_aws['AWS_SECRET_KEY'] = os.environ.get('AWS_SECRET_KEY')
                    del os.environ['AWS_SECRET_KEY']
                os.environ['AWS_SECRET_ACCESS_KEY'] = sess['secret_key']
                os.environ['AWS_SECRET_KEY'] = sess['secret_key']

                if os.environ.get('AWS_SESSION_TOKEN'):
                    if 'session_token' in sess and sess['session_token'] != "":
                        del os.environ['AWS_SESSION_TOKEN']
                    os.environ['AWS_SESSION_TOKEN'] = sess['session_token']
                    os.environ['AWS_SESSION_TOKEN'] = sess['session_token']

                if os.environ.get('AWS_REGION'):
                    env_aws['AWS_REGION'] = os.environ.get('AWS_REGION')
                    del os.environ['AWS_REGION']
                os.environ['AWS_DEFAULT_REGION'] = sess['region']
                os.environ['AWS_REGION'] = sess['region']
                if not 'session_token' in sess:
                    profile_v = enter_credentials(service,
                                                  sess['access_key_id'],
                                                  sess['secret_key'],
                                                  sess['region'],
                                                  useragent,
                                                  proxy_definitions
                                                  )
                    return imported_module.exploit(profile_v, workspace)


                elif 'session_token' in sess and sess['session_token'] != "":
                    profile_v = enter_credentials_with_session_token(service,
                                                                     sess['access_key_id'],
                                                                     sess['secret_key'],
                                                                     sess['region'],
                                                                     sess['session_token'],
                                                                     useragent,
                                                                     proxy_definitions
                                                                     )
                    return imported_module.exploit(profile_v, workspace)

                else:
                    print(colored("[*] Check if the session key is empty.", "yellow"))

                del os.environ['AWS_ACCESS_KEY']
                del os.environ['AWS_SECRET_KEY']
                del os.environ['AWS_REGION']

                del os.environ['AWS_ACCESS_KEY_ID']
                del os.environ['AWS_SECRET_ACCESS_KEY']
                del os.environ['AWS_DEFAULT_REGION']
                if os.environ.get('AWS_SESSION_TOKEN'):
                    del os.environ['AWS_SESSION_TOKEN']

                if env_aws:
                    os.environ['AWS_ACCESS_KEY'] = env_aws['AWS_ACCESS_KEY']
                    os.environ['AWS_SECRET_KEY'] = env_aws['AWS_SECRET_KEY']
                    os.environ['AWS_REGION'] = env_aws['AWS_REGION']
                    if 'AWS_SESSION_TOKEN' in env_aws:
                        os.environ['AWS_SESSION_TOKEN'] = env_aws['AWS_SESSION_TOKEN']

                del env_aws

    else:
        return imported_module.exploit(workspace)
