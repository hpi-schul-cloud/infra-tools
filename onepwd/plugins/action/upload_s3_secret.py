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
# action: schulcloud.onepwd.upload_s3_secret vault=infra-dev  ACCESS_KEY=my-access-key BUCKET_NAME=my-bucket-name ACCESS_SECRET=my-access-secret OVERWRITE=False/True

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#action-plugins
class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None, **kwargs):
        # Log into OnePassword
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)

        # Getting Vars from Ansible 
        # required values
        try: 
            vault = self._task.args['vault']
            BUCKET_NAME = self._task.args['BUCKET_NAME']
            ACCESS_KEY = self._task.args['ACCESS_KEY']
            ACCESS_SECRET = self._task.args['ACCESS_SECRET']
        except: 
            print("""
            ERROR! Couldn't upload s3 secret.
            Please provide a vault, BUCKET_NAME, ACCESS_KEY and ACCESS_SECRET!
            OVERWRITE is optional and set to 'False' per default. Set to 'True' if you wish to overwrite. 
            """) 
            return PLEASE_SET_REQUIRED_VALUES
        # optional values
        overwrite = False
        try: 
            overwrite = eval(self._task.args['OVERWRITE'])
        except: 
            pass

        # Getting Vars for local testing (using Python)
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
        # # optinal values
        # overwrite = False
        # try: 
        #     overwrite = eval(task_vars['OVERWRITE'])
        # except: 
        #     pass


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
            print("Secret s3 alreay exists in the specified vault!") 
            s3_secret_exists = True
            if overwrite == True: 
                print("However since overwrite is set to 'True', values will be overwritten if they differ")
                pass
            else: 
                print("Overwrite is set to 'False'. No action taken.")
                return {}
        except:
            print("Secret doesn't exist yet")
            s3_secret_exists = False

        # Overwrite values      
        if overwrite == True and s3_secret_exists == True: 
            # Test if values are alredy configured as requested
            # svalue is a list with the secret fields [{'k':'string','n':'bucket_name','t':'BUCKET_NAME','v':'My-Bucket-name'}, ...]
            svalue = onepwd.get_secret_values_list(op, item_name=title, vault=vault)
            # True = nothing changed, False = Requested value is different from current value
            check_bucket = True
            check_secret = True
            check_key = True
            if BUCKET_NAME is not None: 
                check_bucket = (svalue[0]['v'] == BUCKET_NAME)
                if svalue[0]['v'] == BUCKET_NAME:
                    print("BUCKET_NAME already set as requested")
                else: 
                    print("BUCKET_NAME is different")
            if ACCESS_KEY is not None: 
                check_key = (svalue[1]['v'] == ACCESS_KEY)
                if svalue[1]['v'] == ACCESS_KEY:
                    print("ACCESS_KEY already set as requested")
                else: 
                    print("ACCESS_KEY is different")
            if ACCESS_SECRET is not None: 
                check_secret = (svalue[2]['v'] == ACCESS_SECRET)
                if svalue[2]['v'] == ACCESS_SECRET:
                    print("ACCESS_SECRET already set as requested")
                else: 
                    print("ACCESS_SECRET is different")

            # Update Secret if changes are present
            if (check_bucket and check_key and check_secret) == False:
                onepwd.OnePwd.update_item(op, title, vault=vault, BUCKET_NAME=BUCKET_NAME, ACCESS_KEY=ACCESS_KEY, ACCESS_SECRET=ACCESS_SECRET )
                print("Secret updated...") 
                return {'changed': 'true',
                'exectued' : 'update item command'}
            else: 
                print("Nothing new to update") 
            return {}


        # Upload Secret if no s3_secret exists
        if s3_secret_exists == False: 
            print("Uploading secret as requested...")
            command = onepwd.OnePwd.create_item(op, category, encoded_item, title, vault=vault, url=url)
            print("Secret uploaded")

            return {'changed': 'true',
                    'exectued' : command}

            
# When run locally with python: Use getting Vars to local ones (using python)
# ActionModule.run('schulcloud.onepwd.onepwd.OnePwd', task_vars={'secret_name': 's3as', 'vault': 'infra-dev', 'BUCKET_NAME': 'my-bucket-name', 'ACCESS_SECRET': 'my-access-secret', 'ACCESS_KEY': 'my-access-key'})


