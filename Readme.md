# Ansible in 15 Minutes
Very basic introduction to Ansible in form of Lightningtalk within NT

## Content
* Why Ansible
* Preconditions
* Ad-Hoc Commands
* Inventories
* Group Variables
* Ansible Vault
* Playbooks
* Roles

## Goals

## Why Ansible

https://www.ansible.com/overview/it-automation  
https://medium.com/@darioems/why-ansible-and-not-others-configuration-manage-tools-909179b5d2b

## Ansible installation

### Native Installation
* Mac & linux
  *  Install [Ansible](https://ansible-tips-and-tricks.readthedocs.io/en/latest/ansible/install/)
* Windows
  * Use Ubuntu subsytem and go back to Linux Installation. No subsystem in place? VirtualBox? No VirtualBox?   
  Do jobs manually on each host :)
* Verification
```bash
ansible --version
ansible 2.5.1
  config file = None
  configured module search path = [u'<user-home>/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/local/lib/python2.7/site-packages/ansible
  executable location = /usr/local/bin/ansible
  python version = 2.7.15 (default, Oct  2 2018, 11:42:04) [GCC 4.2.1 Compatible Apple LLVM 10.0.0 (clang-1000.11.45.2)]
```

### Install via virtualenv
* Ensure virtualenv is installed https://virtualenv.pypa.io/en/stable/installation/
* Run the following command
```bash
# Install Ansible, boto and boto3 in new python3 virtualenv
$ source setup/setupEnvironment.rc
# Check installation
(venv)$ which ansible
<your-dir>/ansible-in-15-minutes/venv/bin/ansible
```

### Localhost preparation
Populate AWS credentials to ansible
* Environment variables
```bash
$ export AWS_ACCESS_KEY_ID=************
$ export AWS_SECRET_ACCESS_KEY=************
```
* Credentials file
```bash
$ cat <home-dir>.aws/credentials
[default]
aws_access_key_id=************
aws_secret_access_key=************

```
### AWS Host Preparation
Now we need some AWS hosts to play with.
* Create hosts manually in AWS console
    * Ensure that
    * Port 22 is reachable
    * Python2 or Python3 is installed
* Use Ansible to create the hosts 
    Don't think about the command yet, will be much clearer at the end of the walkthrough.  
    **IMPORTANT: Each run of this playbook will create new instances**
    ```bash
     ansible-playbook  create-aws-environment.yml
    ```

### Ad-Hoc Commands
Ad-Hoc commands are used to do things once, which are not save for later
By default ansible requires python2 on host machines. If python 2 is not available you can use "-e  ansible_python_interpreter=/usr/bin/python3" to use python3

* Install pip3 on all hosts
```bash
# Install
ansible all -i <ip-host-1>,<ip-host-2>  -u ubuntu --private-key=~/.ssh/ansible-15.pem -b -m raw -a "apt-get update && apt-get install -y python3-pip" 
# Verify
ansible all -i <ip-host-1>,<ip-host-2>  -u ubuntu --private-key=~/.ssh/ansible-15.pem  -b -m raw -a "which python" 

```
* Show diskspace from a single server
```bash
ansible all -i <ip-host-1>,  -u ubuntu --private-key=~/.ssh/ansible-15.pem -m shell -a "df -h" -e  ansible_python_interpreter=/usr/bin/python3 -e  ansible_python_interpreter=/usr/bin/python3
```

* Show diskspace from multiple servers
```bash
ansible all -i <ip-host-1>,<ip-host-2>  -u ubuntu --private-key=~/.ssh/ansible-15.pem -m shell -a "df -h"  -e ansible_python_interpreter=/usr/bin/python3
```

* Copy a file to multiple servers
```bash
# Copy
ansible all -i <ip-host-1>,<ip-host-2>  -u ubuntu --private-key=~/.ssh/ansible-15.pem -m copy -a "src=files/copy_to_host.txt dest=/home/ubuntu/copied.txt" -e  ansible_python_interpreter=/usr/bin/python3
# Read
ansible all -i <ip-host-1>,<ip-host-2>  -u ubuntu --private-key=~/.ssh/ansible-15.pem -m shell -a "cat /home/ubuntu/copied.txt" -e ansible_python_interpreter=/usr/bin/python3
```

* Template a file to multiple servers
```bash
# Template and add custom var
ansible all -i 18.197.186.42,54.93.102.30  -u ubuntu --private-key=~/.ssh/ansible-15.pem -m template -a "src=files/copy_to_host.txt dest=/home/ubuntu/copied.txt" -e "my_param='Gerda Gardine'"  -e ansible_python_interpreter=/usr/bin/python3
# Check Content
ansible all -i <ip-host-1>,<ip-host-2>  -u ubuntu --private-key=~/.ssh/ansible-15.pem -m shell -a "cat /home/ubuntu/copied.txt"  -e ansible_python_interpreter=/usr/bin/python3    
```

* Delete file
```bash
ansible all -i <ip-host-1>,<ip-host-2>  -u ubuntu --private-key=~/.ssh/ansible-15.pem -m file -a "dest=/home/ubuntu/copied.txt state=absent" -e ansible_python_interpreter=/usr/bin/python3
```

## Inventories
Inventories are used to build groups of hosts. Inventories are available in 2 flavours: Static and Dynamic
We'll define an inventory with 2 groups grafana (containing all instances) and grafana-db (with 1 instance) 

### Static inventories
Docu: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html  
In this example we'll use the INI file format to define our inventory
```INI
hostIp-1
hostIp-2

[grafana]
hostIp-1
hostIp-2

[grafana-db]
hostIp-1
```
We provide a basic playbook to create a static inventory file.  
The inventory is created here: **inventories/static/static**
```bash
# Create static inventory
ansible-playbook  create-static-inventory.yml
```

Now we can work with groups in our Ansible commands
```bash
 ansible grafana -i inventories/static  -u ubuntu --private-key=~/.ssh/ansible-15.pem -m shell -a "hostname" 
```

### Dynamic Inventories
Documentation: https://docs.ansible.com/ansible/latest/user_guide/intro_dynamic_inventory.html  
Now we'll create a dynamic inventory for AW instances

```ÌNI
#Empty Groups required by playbooks -> Groups are filled by with children from ec2.py dynamic inventory
[ansible_demo]
[grafana]
[grafana_db]

#The groups defined by aws tags
[tag_grafana_true]
[tag_grafana_db_true]
[tag_ansible_demo_true]

#Include the aws tagged hosts to the static groups used in playbooks
[ansible_demo:children]
tag_ansible_demo_true

[grafana:children]
tag_grafana_true

[grafana_db:children]
tag_grafana_db_true

#Add group containing all instances
[dynamic:children]
grafana
grafana_db
ansible_demo

[dynamic:vars]
ansible_python_interpreter=/usr/bin/python3
````

Check Grafana group
```bash
ansible grafana -i inventories/dynamic  -u ubuntu --private-key=~/.ssh/ansible-15.pem -m shell -a "hostname" 
```

## Group Variables
Documentation: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html
TBD
```INI
grafana_version: 6.0.2
mysql_user: "mysql"
mysql_pw: "{{ vault_mysql_pw }}"
mysql_root_pw: "{{ vault_mysql_pw }}"
```

## Ansible Vault
Documentation: https://docs.ansible.com/ansible/latest/user_guide/vault.html
````bash
# Create a new vault
ansible-vault create group_vars/all/vault
# Edit vault
ansible-vault edit group_vars/all/vault
# Add the following entries to the vault
vault_mysql_pw: mysql
vault_aws_access_key: *****
vault_aws_secret_key: *****
````

## Playbooks
Documentation: https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html  
Create a playbook to install docker and docker-py on each host  
Ansible needs docker-py to interact with the docker daemon

```bash
# Prepare hosts
ansible-playbook -i inventories/dynamic  -u ubuntu --private-key=~/.ssh/ansible-15.pem -b --ask-vault-pass  prepare-hosts.yml  

# Install Docker on all hosts
ansible-playbook -i inventories/dynamic  -u ubuntu --private-key=~/.ssh/ansible-15.pem -b install-docker.yml   

# Install Monitoring Components (Influx and cadvisor on all hosts)
ansible-playbook -i inventories/dynamic  -u ubuntu --private-key=~/.ssh/ansible-15.pem -b install-monitoring.yml   

```

## Roles
Documentation: https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html

```bash
ansible-playbook -i inventories/dynamic -u ubuntu --private-key=~/.ssh/ansible-15.pem --ask-vault-pass install-grafana.yml
```

Check: http://host-ip-1:3000 and http://host-ip-2:3000 if grafana is operational

### Destroy AWS Environment
```bash
ansible-playbook -i inventories/dynamic -u ubuntu --private-key=~/.ssh/ansible-15.pem --ask-vault-pass stop-aws-environment.yml
```