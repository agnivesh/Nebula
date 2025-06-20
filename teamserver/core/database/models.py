from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime

class UserTasks(db.Document):
    task_date_time = db.DateTimeField()
    task_user = db.StringField()
    task_process = db.StringField()


class AWSComponents(db.Document):
    aws_region = db.StringField()
    aws_user_agent = db.StringField()


class Cosmonaut(db.Document):
    cosmonaut_name = db.StringField(required=True, unique=True)
    cosmonaut_pass = db.StringField(required=True)

    def hash_password(self):
        self.cosmonaut_pass = generate_password_hash(self.cosmonaut_pass).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.cosmonaut_pass, password)

class AWSLambda(db.Document):
    aws_lambda_function_name = db.StringField(required=True, unique=True)
    aws_lambda_function_role = db.StringField()
    aws_lambda_function_runtime = db.StringField()
    aws_lambda_function_description = db.StringField()
    aws_lambda_function_state = db.StringField()
    aws_lambda_function_handler = db.StringField()
    aws_lambda_function_package_type = db.StringField()
    aws_lambda_function_repo_type = db.StringField()
    aws_lambda_function_location = db.StringField()

class AWSCredentials(db.Document):
    aws_profile_name = db.StringField(required=True, unique=True)
    aws_access_key = db.StringField(required=True)
    aws_secret_key = db.StringField()
    aws_session_token = db.StringField()
    aws_region = db.StringField()

class DigitalOceanCredentials(db.Document):
    digitalocean_profile_name = db.StringField(required=True, unique=True)
    digitalocean_access_key = db.StringField()
    digitalocean_secret_key = db.StringField()
    digitalocean_token = db.StringField()
    digitalocean_region = db.StringField()


class AZURECredentials(db.Document):
    azure_creds_name = db.StringField(required=True, unique=True)
    azure_user_id = db.StringField()
    azure_client_id = db.StringField()
    azure_client_secret = db.StringField()
    azure_client_cert = db.StringField()
    azure_creds_scope = db.ListField()
    azure_user_principal_name = db.StringField()
    azure_password = db.StringField()
    azure_has_mfa = db.BooleanField()
    azure_access_token = db.StringField()
    azure_id_token = db.StringField()
    azure_refresh_token = db.StringField()
    azure_expiration_date = db.DateTimeField()
    azure_expires_in = db.IntField()
    azure_tenant_id = db.StringField()
    azure_user_name = db.StringField()
    azure_resource = db.StringField()


class AWSPolicies(db.Document):
    aws_policy_name = db.StringField(required=True, unique=True)
    aws_policy_arn = db.StringField(required=True, unique=True)
    aws_policy_id = db.StringField(required=True, unique=True)
    aws_policy_path = db.StringField()
    aws_policy_scope = db.StringField()
    aws_policy_default_version = db.StringField()
    aws_policy_attachment_count = db.IntField()
    aws_policy_permission_boundary_usage_count = db.IntField()
    aws_policy_is_attachable = db.BooleanField()
    aws_policy_create_date = db.DateTimeField()
    aws_policy_update_date = db.DateTimeField()
    aws_policy_documents = db.ListField()


class AWSUsers(db.Document):
    aws_username = db.StringField(required=True, unique=True)
    aws_user_arn = db.StringField(required=True, unique=True)
    aws_user_id = db.StringField(required=True, unique=True)
    aws_user_path = db.StringField()
    aws_user_create_date = db.DateTimeField()
    aws_account_id = db.StringField()
    aws_user_access_to_login_profile = db.BooleanField()
    aws_user_attached_policies = db.ListField()
    aws_user_managed_attached_policies = db.ListField()
    aws_group_policies = db.ListField()
    aws_group_attached_policies = db.ListField()
    aws_user_policies = db.ListField()
    aws_user_groups = db.ListField()
    aws_user_password_last_used = db.DateTimeField()
    aws_user_permission_boundary = db.DictField()
    aws_access_key_last_used = db.DictField()
    aws_user_tags = db.ListField()
    aws_user_is_compromised = db.BooleanField()


class AWSGroups(db.Document):
    aws_groupname = db.StringField(required=True, unique=True)
    aws_group_arn = db.StringField(required=True, unique=True)
    aws_group_id = db.StringField(required=True, unique=True)
    aws_group_path = db.StringField()
    aws_group_create_date = db.DateTimeField()
    aws_group_attached_policies = db.ListField()
    aws_group_users = db.ListField()
    aws_group_policies = db.ListField()
    aws_group_tags = db.ListField()


class AWSRoles(db.Document):
    aws_rolename = db.StringField(required=True, unique=True)
    aws_role_arn = db.StringField(required=True, unique=True)
    aws_role_path = db.StringField()
    aws_role_id = db.StringField(required=True, unique=True)
    aws_role_description = db.StringField()
    aws_role_create_date = db.DateTimeField()
    aws_role_last_usage_date = db.DateTimeField()
    aws_role_last_usage_region = db.StringField()
    aws_role_assume_role_policy = db.DictField()
    aws_role_account_id = db.StringField()
    aws_role_max_session_duration = db.IntField()
    aws_role_attached_policies = db.ListField()
    aws_role_policies = db.ListField()
    aws_role_tags = db.ListField()

class AWSRDSDBInstances(db.Document):
    aws_rds_instance_identifier = db.StringField(required=True, unique=True)
    aws_rds_instance_document = db.DictField()

class AWSInstances(db.Document):
    aws_instance_id = db.StringField(required=True, unique=True)
    aws_group_id = db.StringField()
    aws_owner_id = db.StringField()
    aws_instance_type = db.StringField()
    aws_instance_kernel_id = db.StringField()
    aws_instance_key_name = db.StringField()
    aws_instance_launch_rime = db.DateTimeField()
    aws_instance_monitoring_state = db.StringField()
    aws_instance_platform = db.StringField()
    aws_instance_private_dns_name = db.StringField()
    aws_instance_public_dns_name = db.StringField()
    aws_instance_private_ip_address = db.StringField()
    aws_instance_public_ip_address = db.StringField()
    aws_instance_ramdisk_id = db.StringField()
    aws_instance_state = db.StringField()
    aws_instance_placement = db.DictField()
    aws_instance_product_codes = db.ListField()
    aws_instance_state_transition_reason = db.StringField()
    aws_instance_subnet_id = db.StringField()
    aws_instance_vpc_id = db.StringField()
    aws_instance_architecture = db.StringField()
    aws_instance_block_device_mappings = db.ListField()
    aws_instance_client_group = db.StringField()
    aws_instance_ebs_optimized = db.StringField()
    aws_instance_ena_support = db.StringField()
    aws_instance_hypervisor = db.StringField()
    aws_instance_iam_instance_profile = db.DictField()
    aws_instance_lifecycle = db.StringField()
    aws_instance_elastic_gpu_associations = db.ListField()
    aws_instance_elastic_inference_accelerator_associations = db.ListField()
    aws_instance_network_interfaces = db.ListField()
    aws_instance_outpost_arn = db.StringField()
    aws_instance_root_device_name = db.StringField()
    aws_instance_security_groups = db.ListField()
    aws_instance_source_dest_check = db.BooleanField()
    aws_instance_spot_instance_request_id = db.BooleanField()
    aws_instance_sriov_net_support = db.BooleanField()
    aws_instance_state_reason = db.DictField()
    aws_instance_cpu_options = db.DictField()
    aws_instance_capacity_reservation_id = db.StringField()
    aws_instance_capacity_reservation_specification = db.DictField()
    aws_instance_hibernation_options = db.DictField()
    aws_instance_licenses = db.ListField()
    aws_instance_metadata_options = db.DictField()
    aws_instance_boot_mode = db.StringField()
    aws_instance_platform_details = db.StringField()
    aws_instance_usage_operation = db.StringField()
    aws_instance_usage_operation_update_time = db.DateTimeField()
    aws_instance_tags = db.ListField()


class AWSS3Bucket(db.Document):
    aws_s3_bucket_name = db.StringField(required=True, unique=True)
    aws_s3_bucket_owner = db.StringField()
    aws_s3_creation_date = db.DateTimeField()
    aws_s3_region = db.DateTimeField()
    aws_s3_bucket_objects = db.DictField()
    aws_s3_deleted_objects = db.DictField()
    aws_s3_bucket_policy = db.DictField()
    aws_s3_bucket_policy_status = db.StringField()
    aws_s3_bucket_acl = db.DictField()
    aws_s3_is_website = db.BooleanField()

class DigitalOceanSpace(db.Document):
    digitalocean_s3_space_name = db.StringField(required=True, unique=True)
    digitalocean_s3_space_owner = db.StringField()
    digitalocean_s3_creation_date = db.DateTimeField()
    digitalocean_s3_space_objects = db.ListField()
    digitalocean_s3_deleted_objects = db.ListField()
    digitalocean_s3_space_policy = db.DictField()
    digitalocean_s3_space_policy_status = db.StringField()
    digitalocean_s3_space_acl = db.DictField()
    digitalocean_s3_is_website = db.BooleanField()
    digitalocean_s3_cors = db.DictField()

class GCPBucket(db.Document):
    gcp_bucket_name = db.StringField(required=True, unique=True)
    gcp_bucket_owner = db.StringField()
    gcp_bucket_objects = db.DictField()
    gcp_bucket_policy = db.DictField()
    gcp_bucket_policy_status = db.StringField()
    gcp_bucket_acl = db.DictField()

class AzureServices(db.Document):
    azure_services_base_name = db.StringField(required=True, unique=True)
    azure_services_dns_list = db.DictField()

class AzureADUsage(db.Document):
    domain_name = db.StringField(required=True, unique=True)
    usage = db.StringField()
    federation_brandname = db.StringField()
    cloud_instance_name = db.StringField()
    cloud_instance_issuer_uri = db.StringField()
    tenant_id = db.StringField()
    auth_url = db.StringField()


class UserAgent(db.Document):
    user_agent_type = db.StringField()
    user_agent = db.StringField()

class Domains(db.Document):
    dn_name = db.StringField(required=True, unique=True)
    service = db.StringField()
    azureUsage = db.DictField()
    subdomains = db.ListField()
    domain_ips = db.ListField()
    federation_brandname = db.StringField()
    cloud_instance_name = db.StringField()
    cloud_instance_issuer_uri = db.StringField()
    tenant_id = db.StringField()
    auth_url = db.StringField()

class AzureUsers(db.Document):
    azure_user_email = db.StringField(required=True, unique=True)
    azure_user_domain = db.StringField()
    azure_user_has_password = db.BooleanField()
    azure_user_password = db.StringField()
    azure_user_mfa_enabled = db.BooleanField()
    azure_user_password_expired = db.BooleanField()
    azure_user_locked = db.BooleanField()
    azure_user_disabled = db.BooleanField()

class AWSSupportCases(db.Document):
    aws_support_case_id = db.StringField(required=True, unique=True)
    aws_support_display_id = db.StringField()
    aws_support_subject = db.StringField()
    aws_support_status = db.StringField()
    aws_support_service_Code = db.StringField()
    aws_support_categoryCode = db.StringField()
    aws_support_severityCode = db.StringField()
    aws_support_submittedBy = db.StringField()
    aws_support_timeCreated = db.StringField()
    aws_support_recent_communications = db.DictField()
    aws_support_language = db.StringField()
    aws_support_cc_email_addresses = db.ListField()

class WebsocketListener(db.Document):
    listener_name = db.StringField(required=True, unique=True)
    listener_host = db.StringField(required=True)
    listener_port = db.IntField(required=True)
    listener_protocol = db.StringField(required=True)
    listener_ssl_cert_path = db.StringField()
    listener_ssl_key_path = db.StringField()
    listener_status = db.StringField()
    listener_tasks = db.ListField()

class WebsocketParticle(db.Document):
    particle_id = db.StringField(required=True, unique=True)
    c2_host = db.StringField(required=True)
    c2_port = db.IntField(required=True, unique=True)
    particle_listener = db.StringField(required=True)
    particle_system = db.StringField()
    particle_env = db.StringField()
    particle_uname = db.DictField()
    particle_env_variables = db.DictField()
    particle_init = db.StringField()
    particle_docksock = db.BooleanField()
    particle_disks = db.ListField()
    particle_privileged_docker = db.BooleanField()
    particle_hostname = db.StringField()
    particle_aws_data = db.ListField()
    particle_meta_data = db.DictField()

class S3C2Listener(db.Document):
    listener_bucket_name = db.StringField(required=True, unique=True)
    listener_command_file = db.StringField(required=True)
    listener_output_file = db.StringField(required=True)
    listener_access_key = db.StringField(required=True)
    listener_secret_key = db.StringField(required=True)
    listener_region = db.StringField(required=True)
    listener_particle_access_key = db.StringField(required=True)
    listener_particle_secret_key = db.StringField(required=True)
    listener_kms_key_arn = db.StringField(required=True)

class S3C2Particle(db.Document):
    particle_key_name = db.StringField(required=True, unique=True)
    particle_listener_name = db.StringField(required=True, unique=True)

class KubeCluster(db.Document):
    kube_cluster_name = db.StringField(required=True)
    kube_cluster_ports = db.DictField()
    kube_cluster_nodes = db.ListField()
    kube_cluster_pods = db.ListField()
    kube_cluster_users = db.ListField()

class KubeCredential(db.Document):
    kube_credential_name = db.StringField(required=True)
    kube_credential_token = db.StringField()
    kube_credential_config_file = db.DictField()
    kube_credential_oidc_file = db.DictField()

class TeamserverLogs(db.Document):
    teamserver_event_time = db.DateTimeField()
    teamserver_event_user = db.StringField()
    teamserver_event_description = db.StringField()

class ReverseTunnels(db.Document):
    teamserver_reverse_tunnel_listener = db.StringField()
    teamserver_reverse_tunnel_status = db.BooleanField()
    teamserver_reverse_tunnel_socks_port = db.IntField()
    teamserver_reverse_tunnel_listening_port = db.IntField()
    teamserver_reverse_tunnel_mgmt_port = db.IntField()

