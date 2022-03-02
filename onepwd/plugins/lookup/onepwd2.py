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
from ansible.plugins.lookup import LookupBase
import os
import onepwd
import url64

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#lookup-plugins

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        # Log into OnePassword
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)
        # Get/Set Values
        category=kwargs.get('category', 'password')
        title=kwargs.get('secret_name', None)
        vault=kwargs.get('vault', None)
        url=kwargs.get('url')
        content=kwargs.get('content', '')
        template = '{"sections":[{"fields":[' + str(content) +  ']}]}'
        encoded_item = url64.encode(template)      
        # Upload Secret
        # onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url)
        print(onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url))
        command = onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url)
        return command


#LookupModule.run('schulcloud.onepwd.onepwd.OnePwd', secret_name='TestItem239', vault='infra-dev', url='ionos@mail.com', content='{"k":"string","n":"Bucket-ID","t":"Bucket-id","v":"NBC-Test"},{"k":"concealed","n":"password","t":"Access-Key","v":"489570283475"},{"k":"concealed","n":"password2","t":"Access-Secret","v":"102947019"}')