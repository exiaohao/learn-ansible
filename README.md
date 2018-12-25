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

```yaml
# basic provisioning example vpc network
- name: basic provisioning example
  hosts: localhost // Run locally
  vars:
    alicloud_region: cn-huhehaote
    image: ubuntu_16_0402_32_20G_alibase_20180409.vhd
    instance_type: ecs.t5-lc2m1.nano
    vswitch_id: vsw-hp3clzscsdebbyuoebgsq
    assign_public_ip: True
    max_bandwidth_out: 1
    host_name: demo-host
    system_disk_category: cloud_efficiency
    system_disk_size: 20
    internet_charge_type: PayByTraffic
    password: H@0Dem0P@ssword~
    security_groups:
    - sg-hp3atpe87tedkilz4shx
    key_name: hao-ansible
    instance_tags:
      Group: test
      Machine: demo
    force: True
```

```yaml
...
  tasks:
    - name: launch ECS instance in VPC network
      ali_instance:
        alicloud_access_key: '{{ lookup("env", "ALICLOUD_ACCESS_KEY") }}' # '{{ alicloud_access_key }}'
        alicloud_secret_key: '{{ lookup("env", "ALICLOUD_SECRET_KEY") }}' # '{{ alicloud_secret_key }}'
        alicloud_region: '{{ alicloud_region }}'
        image: '{{ image }}'
        system_disk_category: '{{ system_disk_category }}'
        system_disk_size: '{{ system_disk_size }}'
        instance_type: '{{ instance_type }}'
        vswitch_id: '{{ vswitch_id }}'
        assign_public_ip: '{{ assign_public_ip }}'
        internet_charge_type: '{{ internet_charge_type }}'
        max_bandwidth_out: '{{ max_bandwidth_out }}'
        key_name: '{{ key_name }}'
        instance_tags: '{{ instance_tags }}'
        host_name: '{{ host_name }}'
        password: '{{ password }}'
        security_groups: '{{ security_groups }}'
```