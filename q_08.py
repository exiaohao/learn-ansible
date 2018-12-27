#!/usr/bin/env python
# encoding: utf-8

DOCUMENTATION = '''
HERE's DOCUMENTATION
'''

EXAMPLES = '''
HERE's EXAMPLES
'''

import re
import requests

from ansible.module_utils.basic import *
from bs4 import BeautifulSoup

def parse_result(html_text):
    soup = BeautifulSoup(html_text, 'lxml')
    body = soup.find('html')
    pattern = '[^\w]'
    words = []
    for item in body.find_all():
        words += re.sub(pattern, ' ', item.get_text()).split()
    words.sort()
    return len(words), ','.join(words)

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
                word_count, words = parse_result(req.text)
                module.exit_json(msg="There's {0} words, there're: {1}".format(word_count, words), failed_attempts=try_count)
                return
        except Exception as e:
            continue
    module.fail_json(msg='Maximum attempts reached: ' + str(e), failed_attempts=try_count)

main()
