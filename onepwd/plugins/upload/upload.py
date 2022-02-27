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
from ansible.plugins.action import ActionBase
import os
import onepwd
import url64

class LookupModule(ActionBase):

    def lookup(self, variables=None, **kwargs):
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)
        secret_name=kwargs.get('secret_name', '')
        vault=kwargs.get('vault', None)
        field=kwargs.get('field', None)
        print(onepwd.get_single_secret(op, secret_name, field=field, vault=vault))
        onepwd.get_single_secret(op, secret_name, field=field, vault=vault)


    def upload(self, variables=None, **kwargs):
        # Log into OnePassword
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)
        # Get/Set values
        category=kwargs.get('category', 'login')
        title=kwargs.get('title', None)
        vault=kwargs.get('vault', None)
        url=kwargs.get('url', 'test@gmail.de')
        # CreateEncoded Item - with base64url encoding
        # encoded_item =  'eyJmaWVsZHMiOiBbeyJkZXNpZ25hdGlvbiI6ICJ1c2VybmFtZSIsIm5hbWUiOiAidXNlcm5hbWUiLCJ0eXBlIjogIlQiLCJ2YWx1ZSI6ICIifSx7ImRlc2lnbmF0aW9uIjogInBhc3N3b3JkIiwibmFtZSI6ICJwYXNzd29yZCIsInR5cGUiOiAiUCIsInZhbHVlIjogIiJ9XSwibm90ZXNQbGFpbiI6ICIiLCJwYXNzd29yZEhpc3RvcnkiOiBbXSwic2VjdGlvbnMiOiBbXX0' 
        data = '{"fields":[{"designation":"username","name":"username","type":"T","value":"asd"},{"designation":"password","name":"password","type":"P","value":"asd"}],"notesPlain":"","passwordHistory":[],"sections":[]}'
        encoded_item = url64.encode(data)        
        print(encoded_item)
        print(onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url))
        #onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url)

# Aus Ansible
# {{ upload('schulcloud.onepwd.onepwd', title='Test-1p', vault='infra-dev', url=url) }}

LookupModule.lookup('schulcloud.onepwd.onepwd', secret_name='Test1p', vault='infra-dev', field='password')
LookupModule.upload('schulcloud.onepwd.onepwd.OnePwd', category='login', title='TestItem2', vault='infra-dev', )