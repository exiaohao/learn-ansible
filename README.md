# Ansible get started

Before start, I have registered a Aliyun account and prepaid some balance. All of demos in this document was written under Aliyun service.

Get your AK/SK from Aliyun and set it to environment variables:
```bash
export ALICLOUD_ACCESS_KEY='YOUR-AK'
export ALICLOUD_SECRET_KEY='YOUR-SK'
```

Install [Ansible](https://docs.ansible.com/ansible/devel/installation_guide/intro_installation.html), Python, [Aliyun ansible-provider](https://github.com/alibaba/ansible-provider) and [Aliyun-cli](https://github.com/aliyun/aliyun-cli)

Make sure the following commands are available: `ansible`, `ansible-playbook`, `aliyuncli`. Configure your aliyuncli with your AK/SK and region, it's easily get some resources like OS image.

Ansible's offical doc has Alibaba Cloud Compute Service Guide, see https://docs.ansible.com/ansible/devel/scenario_guides/guide_alicloud.html

### Provision a aliyun instance with an OS of your own choice.

Create a yaml named **basic provisioning example**: [01-start-aliyun-ecs-instance.yaml](01-start-aliyun-ecs-instance.yaml)

We'll create a instance w/ Ubuntu 16.04 and preseted network and security groups. `vars` defined variables can be used in `tasks`, `tasks` shows which tasks will be proceeded. 

| -- Variable key -- | -- Description -- |
| --- | --- |
| alicloud_region | Regions. see https://help.aliyun.com/document_detail/40654.html |
| image | OS images or your template. use command `aliyuncli ecs DescribeImages` to get details |
| instance_type | Define instance type |
| vswitch_id | Virtual switch ID, find it from VPC |
| assign_public_ip | Assign Public IP ? |
| max_bandwidth_out | Max bandwidth |
| host_name | VM Hostname |
| system_disk_category | `cloud`: slowest disk max capacity: 2000G<br />`cloud_efficiency`: quickly disk, max capacity: 32T, <br />`cloud_ssd` SSD disk, max capacity: 32T |
| system_disk_size | literal meaning |
| internet_charge_type | `PayByTraffic` Default, Pay by traffic<br />`PayByBandwidth` pay by fixed bandwidth |
| password | instance root password |
| security_groups | Security groups ID, see related settings |
| key_name | which SSH key will be installed, see key settings | 
| instance_tags | set some tags |
| force | Whether the current operation needs to be execute forcibly |

See https://github.com/alibaba/ansible-provider/blob/master/lib/ansible/modules/cloud/alicloud/ali_instance.py#L27-L177 for more detailed documentation.

Run `ansible-playbook 01-start-aliyun-ecs-instance.yaml` and results like following text:
```
PLAY [basic provisioning example] ************************************************************************************************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************************************************************************************************
ok: [localhost]

TASK [launch ECS instance in VPC network] ****************************************************************************************************************************************************************************************************
changed: [localhost]

PLAY RECAP ***********************************************************************************************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0
```

### Change the OS/Firewall settings of the started instance to further enhance it’s security level.

After creating aliyun instance and append security groups, ansible has ***ufw*** package can apply ufw rules quickly:
```bash
ansible demo-host -s -m ufw -a "state=enabled policy=allow"         # Enable ufw
ansible demo-host -s -m ufw -a "rule=allow name=OpenSSH"            # Enable OpenSSH, otherwise it will out of control
ansible demo-host -s -m ufw -a "direction=incoming policy=deny"     # Deny all another incoming traffic
```

Also can use ansible-playbook to apply it, see [02-firewall-rules.yaml](02-firewall-rules.yaml)

ufw status:
```bash
# ufw status verbose

Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp (OpenSSH)           ALLOW IN    Anywhere
22/tcp (OpenSSH (v6))      ALLOW IN    Anywhere (v6)
```

### Install Docker CE.

Following Docker offical installation guide: https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce and Ansible apt module: https://docs.ansible.com/ansible/latest/modules/apt_module.html, I've make a yaml:


