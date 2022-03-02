from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
'''

EXAMPLES = """
"""

RETURN = """
"""

from subprocess import Popen, PIPE
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_bytes, to_text
from ansible.plugins.action import ActionBase
import os
import onepwd
import url64


# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#action-plugins
# How to use in Ansible:{{ action('schulcloud.onepwd.onepwd.OnePwd', secret_name='my-name', vault='myvault', url='my-url', content='{"k":"string","n":"my-has-to-be-unique-internal-name","t":"my-seen-in-gui-name","v":"my-value"},{"k":"concealed","n":"password","t":"my-password","v":"random39463"}') }}
# See example for content in Docs: https://docs.hpi-schul-cloud.org/display/PROD/1Password

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None, **kwargs):
        # Log into OnePassword
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)
        # Get/Set Values

        # works local
        category = task_vars['category']
        title = task_vars['secret_name']
        vault = task_vars['vault']
        content = task_vars['content']
        # category=kwargs.get('category', 'password')
        # title=kwargs.get('secret_name', None)
        # vault=kwargs.get('vault', None)
        # content=kwargs.get('content', '')
        template = '{"fields":[],"notesPlain":"","passwordHistory":[],"sections":[{"fields":[' + str(content) +  ']}]}'
        encoded_item = url64.encode(template)      
        # Upload Secret
        # onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url)
        # print(onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url))
        command = onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault)
        # onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault)
        return command


# ActionModule.run('schulcloud.onepwd.onepwd.OnePwd', task_vars={'category': 'password', 'secret_name': 'TestIte99', 'vault': 'infra-dev', 'content': '{"k":"string","n":"Bucket-ID","t":"Bucket-id","v":"NBC-Test"},{"k":"concealed","n":"password","t":"Access-Key","v":"489570283475"},{"k":"concealed","n":"password2","t":"Access-Secret","v":"102947019"}'})

