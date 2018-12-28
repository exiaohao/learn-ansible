Purpose: This test is designed to test the DevOps candidates’s scripting skills

Use Ansible/terraform to automate the process of creating an AWS/Aliyun EC2 instance and complete the following tasks.

#### 1. Provision a t2.micro instance, with an OS of your own choice.
#### 2. Change the security group of of the instance to ensure it’s security level.

[01-start-aliyun-ecs-instance.yaml](01-start-aliyun-ecs-instance.yaml)

#### 3. Change the OS/Firewall settings of the started instance to further enhance it’s security level.

[02-firewall-rules.yaml](02-firewall-rules.yaml)

#### 4. Install Docker CE.

[03-docker.yaml](03-docker.yaml)

#### 5. Deploy and start an nginx container in docker.

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

#### 6. Run a command to test the healthiness of the  nginx container. 

[05-nginx-with-health-check.yaml](05-nginx-with-health-check.yaml)

#### 7.Fetch the output of the nginx container’s default http page.
#### 8.Stipe all the html tags, grep and count all the words in the fetched html, then print the result in the following manner, sort the result in alphabet order

Module: fetch_page [q_08.py](q_08.py)

Playbook:
```yaml
- name: Test fetch page
  hosts: localhost
  tasks:
  - name: Try fetch page
    fetch_page:
      url: "http://demo-host"
```

Result: [q_08.txt](q_08.txt)

or use shell to do:
```bash
curl http://demo-host | sed -r 's/[\<][\/]?[a-zA-Z0-9\=\"\-\#\.\& ]+[\/]?[\>]//g' $1 | tr " " "\n"
```

#### 9. Logs the resource usage of the container every 10 seconds.

Module: container_usage [q_09.py](q_09.py)

Playbok: [q_09.yaml](q_09.yaml)

Result: [q_09.txt](q_09.txt)

