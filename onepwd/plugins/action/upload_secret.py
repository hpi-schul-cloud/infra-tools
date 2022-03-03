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

# Provides the ability to load a secret named s3 to the vault  
# action: schulcloud.onepwd.upload_secret category='password' vault='infra-dev' secret_name='TestHello' content='{\"k\":\"string\",\"n\":\"Bucket-ID\",\"t\":\"Bucket-id\",\"v\":\"NBC-Test\"}'
# See example for content in Docs: https://docs.hpi-schul-cloud.org/display/PROD/1Password

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#action-plugins
class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None, **kwargs):
        # Log into OnePassword
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)
        # Get/Set Values

        # # Getting Vars from Ansible 
        # title = self._task.args['secret_name']
        # vault = self._task.args['vault']
        # BUCKET_NAME = self._task.args['BUCKET_NAME']
        # ACCESS_KEY = self._task.args['ACCESS_KEY']
        # ACCESS_SECRET = self._task.args['ACCESS_SECRET']
        
        # Getting Vars for local testing (Python)
        title = task_vars['secret_name']
        vault = task_vars['vault']
        BUCKET_NAME = task_vars['BUCKET_NAME']
        ACCESS_KEY = task_vars['ACCESS_KEY']
        ACCESS_SECRET = task_vars['ACCESS_SECRET']

        # Hardcoded Vars
        category = 'password' 
        url = 'https://dcd.ionos.com/latest'
        # title = 's3'

        # Template creation - BUCKET_NAME, ACCESS_KEY and ACCESS_SECRET
        content = f'{{"k":"string","n":"bucket_name","t":"BUCKET_NAME","v":"{BUCKET_NAME}"}},{{"k":"concealed","n":"access_key","t":"ACCESS_KEY","v":"{ACCESS_KEY}"}},{{"k":"concealed","n":"access_secret","t":"ACCESS_SECRET","v":"{ACCESS_SECRET}"}}'
        template = '{"sections":[{"fields":[' + str(content) +  ']}]}'
        encoded_item = url64.encode(template)      

        # test if secret already exists 
        already_exists = []
        command = ""
        try: 
            already_exists.append(onepwd.get_single_secret(op, item_name=title, vault=vault, field='name'))
        except:
            print("Secret doesn't exist yet")
        if not already_exists:
            print("Uploading secret as wished...")
            # upload Secret
            command = onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url)
            print("Secret uploaded...")
        else:
            print("Secret s3 alreay exists in the specified vault! Secret not uploaded to 1Password. You may want to create an Item with a different name or use the update action.")  

        return command

            

# When run like this set Getting Vars, to local ones
ActionModule.run('schulcloud.onepwd.onepwd.OnePwd', task_vars={'secret_name': 'Test100', 'vault': 'infra-dev', 'BUCKET_NAME': 'my-bucket-name', 'ACCESS_SECRET': 'my-access-secret', 'ACCESS_KEY': 'my-access-key'})


