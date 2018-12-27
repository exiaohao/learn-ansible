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

Following Docker offical installation guide: https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce and Ansible apt module: https://docs.ansible.com/ansible/latest/modules/apt_module.html, I've make a yaml: [03-docker.yaml](03-docker.yaml)

In chinamainland sometimes there's some problem to get access to Docker offical site, ansible can set `HTTP_PROXY` and `HTTPS_PROXY` to environment variables, can help solve some problems. Sample:
```yaml
- name: some playbook
  environment:
    http_proxy: http://proxy.example.com:8080
  ...
  tasks:
    - name: some task
      apt: name=foo
        environment:
          http_proxy: http://proxy.example.com:8080
```

### Start a nginx in Docker

Ansible docker module: https://docs.ansible.com/ansible/latest/modules/docker_container_module.html

You'd install Python module **docker** at first, otherwise ansible will failed because 
> Failed to import docker or docker-py - No module named docker. Try `pip install docker` or `pip install docker-py` (Python 2.6)
> Please note that the docker-py Python module has been superseded by docker (see here for details). For Python 2.6, docker-py must be used. Otherwise, it is recommended to install the docker Python module. Note that both modules should not be installed at the same time. Also note that when both modules are installed and one of them is uninstalled, the other might no longer function and a reinstall of it is required.

create a simple nginx container:
```yaml
- name: create nginx container
  hosts: demo-host
  tasks:
  - name: Install package docker for python avoid somethings wrong
    pip:
      name: docker
  - name: Create a container called demo-nginx
    docker_container:
      name: demo-nginx
      image: nginx
```

Check nginx is started:
```bash
$ curl demo-host -v

* About to connect() to demo-host port 80 (#0)
*   Trying *.*.*.*...
* Connected to demo-host (*.*.*.*) port 80 (#0)
> GET / HTTP/1.1
> User-Agent: curl/7.29.0
> Host: demo-host
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: nginx/1.15.8
< Date: Thu, 27 Dec 2018 10:00:03 GMT
< Content-Type: text/html
< Content-Length: 612
< Last-Modified: Tue, 25 Dec 2018 09:56:47 GMT
< Connection: keep-alive
< ETag: "5c21fedf-264"
< Accept-Ranges: bytes
<
<!DOCTYPE html>
...
```

After nginx container is running, We can also add a task to check nginx's health status. I've added a module called [ansible-health-check](https://github.com/trueaccord/ansible-health-check) and a task like:
```yaml
...
- name: nginx health check
  health_check:
    url: "http://demo-host/"
    delay_between_tries: 2
    max_retries: 5
    expected_status: 200
```

See [05-nginx-with-health-check.yaml](05-nginx-with-health-check.yaml) for full config.

### Make your own module

Although there're lots of modules, you can alse make a module for yourself.

The following sample shows that a tool can fetch a specified page, if page returns HTTP 200 status, it'll return page content, otherwise it'll be exit and show you error reason after retrying specified times(the default retrying times is 5).

```python
#!/usr/bin/env python
# encoding: utf-8

DOCUMENTATION = '''
HERE's DOCUMENTATION
'''

EXAMPLES = '''
HERE's EXAMPLES
'''

import requests

from ansible.module_utils.basic import *

def main():
    module = AnsibleModule(
        argument_spec = dict(
            url = dict(required=True),
            headers = dict(required=False, type='dict', default=None),
            timeout = dict(required=False, type='int', default=5),
            max_retries = dict(required=False, type='int', default=5),
            try_delay = dict(required=False, type='int', default=3),
        )
    )

    url = module.params['url']
    headers = module.params['headers'] or {}
    timeout = module.params['timeout']
    max_retries = module.params['max_retries']
    try_delay = module.params['try_delay']

    for try_count in xrange(max_retries):
        if try_count > 0:
            time.sleep(try_delay)
        try:
            req = requests.get(url, headers=headers, timeout=timeout)
            if req.status_code == 200:
                module.exit_json(msg=req.text, failed_attempts=try_count)
                return
        except Exception as e:
            continue
    module.fail_json(msg='Maximum attempts reached: ' + str(e), failed_attempts=try_count)

main()
```

After put the module to ansible module directory, we can call it from playbook:
```yaml
- name: Test fetch page
  hosts: localhost
  tasks:
  - name: Try fetch page
    fetch_page:
      url: "http://demo-host"
```

I've trying to fetch the default page which is created by [Start a nginx in Docker](#start-a-nginx-in-docker) , the results:
```bash
TASK [Try fetch page] ************************************************************************************************************************************************************************************************************************
task path: /root/ansible/test-fetch.yaml:4
<127.0.0.1> ESTABLISH LOCAL CONNECTION FOR USER: root
<127.0.0.1> EXEC /bin/sh -c 'echo ~root && sleep 0'
<127.0.0.1> EXEC /bin/sh -c '( umask 77 && mkdir -p "` echo /root/.ansible/tmp/ansible-tmp-1545911236.21-256641403308025 `" && echo ansible-tmp-1545911236.21-256641403308025="` echo /root/.ansible/tmp/ansible-tmp-1545911236.21-256641403308025 `" ) && sleep 0'
Using module file /root/.ansible/plugins/modules/fetch_page
<127.0.0.1> PUT /root/.ansible/tmp/ansible-local-11904xnGBF2/tmpPcifCM TO /root/.ansible/tmp/ansible-tmp-1545911236.21-256641403308025/AnsiballZ_fetch_page
<127.0.0.1> EXEC /bin/sh -c 'chmod u+x /root/.ansible/tmp/ansible-tmp-1545911236.21-256641403308025/ /root/.ansible/tmp/ansible-tmp-1545911236.21-256641403308025/AnsiballZ_fetch_page && sleep 0'
<127.0.0.1> EXEC /bin/sh -c '/usr/bin/python2 /root/.ansible/tmp/ansible-tmp-1545911236.21-256641403308025/AnsiballZ_fetch_page && sleep 0'
<127.0.0.1> EXEC /bin/sh -c 'rm -f -r /root/.ansible/tmp/ansible-tmp-1545911236.21-256641403308025/ > /dev/null 2>&1 && sleep 0'
ok: [localhost] => {
    "changed": false,
    "failed_attempts": 0,
    "invocation": {
        "module_args": {
            "headers": null,
            "max_retries": 5,
            "timeout": 5,
            "try_delay": 3,
            "url": "http://demo-host"
        }
    },
    "msg": "<!DOCTYPE html>\n<html>\n<head>\n<title>Welcome to nginx!</title>\n<style>\n    body {\n        width: 35em;\n        margin: 0 auto;\n        font-family: Tahoma, Verdana, Arial, sans-serif;\n    }\n</style>\n</head>\n<body>\n<h1>Welcome to nginx!</h1>\n<p>If you see this page, the nginx web server is successfully installed and\nworking. Further configuration is required.</p>\n\n<p>For online documentation and support please refer to\n<a href=\"http://nginx.org/\">nginx.org</a>.<br/>\nCommercial support is available at\n<a href=\"http://nginx.com/\">nginx.com</a>.</p>\n\n<p><em>Thank you for using nginx.</em></p>\n</body>\n</html>\n"
}
META: ran handlers
META: ran handlers
```


