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

# Provides the ability to upload a secret named 's3' to the vault  
# How to use in Ansible: 
# action: schulcloud.onepwd.upload_s3_secret vault=infra-dev  ACCESS_KEY=my-access-key BUCKET_NAME=my-bucket-name ACCESS_SECRET=my-access-secret

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#action-plugins
class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None, **kwargs):
        # Log into OnePassword
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)

        # Getting Vars from Ansible 
        vault = self._task.args['vault']
        try: 
            BUCKET_NAME = self._task.args['BUCKET_NAME']
            ACCESS_KEY = self._task.args['ACCESS_KEY']
            ACCESS_SECRET = self._task.args['ACCESS_SECRET']
        except: 
            print("""
            ERROR! Could't upload s3 secret.
            Please provide a BUCKET_NAME, ACCESS_KEY and ACCESS_SECRET!
            """)
        
        # # Getting Vars for local testing (using Python)
        # vault = task_vars['vault']
        # try: 
        #     BUCKET_NAME = task_vars['BUCKET_NAME']
        #     ACCESS_KEY = task_vars['ACCESS_KEY']
        #     ACCESS_SECRET = task_vars['ACCESS_SECRET']
        # except: 
        #     print("""
        #     ERROR! Could't upload s3 secret.
        #     Please provide a BUCKET_NAME, ACCESS_KEY and ACCESS_SECRET!
        #     """)

        # Hardcoded Vars
        category = 'password' 
        url = 'https://dcd.ionos.com/latest'
        title = 's3'

        # Template creation - BUCKET_NAME, ACCESS_KEY and ACCESS_SECRET
        content = f'{{"k":"string","n":"bucket_name","t":"BUCKET_NAME","v":"{BUCKET_NAME}"}},{{"k":"concealed","n":"access_key","t":"ACCESS_KEY","v":"{ACCESS_KEY}"}},{{"k":"concealed","n":"access_secret","t":"ACCESS_SECRET","v":"{ACCESS_SECRET}"}}'
        template = '{"sections":[{"fields":[' + str(content) +  ']}]}'
        encoded_item = url64.encode(template)      

        # Test if secret already exists 
        try: 
            onepwd.get_single_secret(op, item_name=title, vault=vault)
            print("Secret s3 alreay exists in the specified vault! Secret not uploaded to 1Password. You may want to create an Item with a different name or use the update_s3_secret action.")  
            return {}
        except:
            print("Secret doesn't exist yet")

        # Upload Secret
        print("Uploading secret as requested...")
        command = onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url)
        print("Secret uploaded...")

        return command

            

# When run locally with python: Use getting Vars to local ones (using python)
# ActionModule.run('schulcloud.onepwd.onepwd.OnePwd', task_vars={'secret_name': 's3as', 'vault': 'infra-dev', 'BUCKET_NAME': 'my-bucket-name', 'ACCESS_SECRET': 'my-access-secret', 'ACCESS_KEY': 'my-access-key'})


