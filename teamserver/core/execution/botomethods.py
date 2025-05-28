from termcolor import colored
def execute_boto_method(all_sessions, cred_prof, useragent, web_proxies, callstoprofile, terraform, methodname, args, service):
    if terraform:
        useragent = f"APN/1.0 HashiCorp/1.0 Terraform/1.8.5 (+https://www.terraform.io) terraform-provider-aws/5.57.0 (+https://registry.terraform.io/providers/hashicorp/aws) aws-sdk-go-v2/1.30.1 os/linux lang/go#1.22.4 md/GOOS#linux md/GOARCH#amd64 api/{service}#1.30.1"

    profile = giveMeClient(
		all_sessions,
		cred_prof,
		useragent,
		web_proxies,
		service
	)

    methods = dir(profile)

    if methodname not in methods:
        print(
            colored(f"[*] Boto does not contain a method: {methodname}", "red")
        )
        return None

    try:
        if terraform:
            useragent = "APN/1.0 HashiCorp/1.0 Terraform/1.8.5 (+https://www.terraform.io) terraform-provider-aws/5.57.0 (+https://registry.terraform.io/providers/hashicorp/aws) aws-sdk-go-v2/1.30.1 os/linux lang/go#1.22.4 md/GOOS#linux md/GOARCH#amd64 api/sts#1.30.1"
            stsprofile = giveMeClient(
                all_sessions,
                cred_prof,
                useragent,
                web_proxies,
                "sts"
            )
            stsprofile.get_caller_identity()

        return getattrs(profile, methodname), (*args)

    except Exception as e:
        return {"error": str(e)}