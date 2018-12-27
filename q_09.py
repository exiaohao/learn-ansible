#!/usr/bin/env python
# encoding: utf-8

DOCUMENTATION = '''
HERE's DOCUMENTATION
'''

EXAMPLES = '''
HERE's EXAMPLES
'''

import commands
import json
import time

from ansible.module_utils.basic import *

def main():
    module = AnsibleModule(
        argument_spec = dict(
            containers = dict(required=False),
            interval = dict(required=False, type='int', default=10),
        )
    )
    containers = module.params['containers']
    interval = module.params['interval']
    if not isinstance(containers, list):
        if containers == 'all':
            containers = []
        else:
            return module.fail_json(msg='Bad containers list')

    while True:
        stat, result = commands.getstatusoutput("docker stats --no-stream --format '{{json .}}'")
        if stat == 0:
            status_msg = "Docker containers:\n"
            for container_result in result.split('\n'):
                if containers:
                    c = json.loads(container_result)
                    if c['Container'] not in containers:
                        continue
                status_msg += container_result
            module.exit_json(msg=status_msg)
        else:
            return module.fail_json(msg='Exited({0}) {1}'.format(stat, result))
        time.sleep(interval)

main()
