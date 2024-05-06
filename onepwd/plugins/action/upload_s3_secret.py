from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
Provides the ability to upload a secret to a vault (if secret does not exist), and to update the values of the secret if they differ from the requested ones (set OVERWRITE=True) 
'''

EXAMPLES = """
- name: Edit S3 Credentials in 1Password
  dbildungscloud.onepwd.upload_s3_secret:
    vault: "vault"
    BUCKET_NAME: "bucket_name"
    SECRET_NAME:  "secret_name"
    ACCESS_KEY: "access-key"
    ACCESS_SECRET: "access-secret"
    OVERWRITE: True
"""

RETURN = """
If non-existent uploads credentials in item named "s3", if existent updates the s3 credentials in s3 secret"
"""

from subprocess import Popen, PIPE
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_bytes, to_text
from ansible.plugins.action import ActionBase
import os
import onepwd
import url64

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#action-plugins
class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None, **kwargs):
        # Log into OnePassword
        if 'credentials' in self._task.args:
            login_secret=onepwd.get_op_login_from_args(self._task.args.get('credentials'))
        elif 'credentials_file' in self._task.args:
            login_secret=onepwd.get_op_login_from_file(self._task.args.get('credentials_file'))
        else:
            login_secret=onepwd.get_op_login_from_env()

        session_shorthand=self._task.args.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)

        # Getting Vars from Ansible 
        # required values
        try: 
            vault = self._task.args['vault']
            BUCKET_NAME = self._task.args['BUCKET_NAME']
            SECRET_NAME = self._task.args['SECRET_NAME']
            ACCESS_KEY = self._task.args['ACCESS_KEY']
            ACCESS_SECRET = self._task.args['ACCESS_SECRET']
        except: 
            print("""
            ERROR! Couldn't upload s3 secret.
            Please provide a vault, BUCKET_NAME, SECRET_NAME, ACCESS_KEY and ACCESS_SECRET!
            OVERWRITE is optional and set to 'False' per default. Set to 'True' if you wish to overwrite. 
            """) 
            raise Exception("PLEASE_SET_REQUIRED_VALUES - vault, BUCKET_NAME, ACCESS_KEY, ACCESS_SECRET")
        # optional values
        overwrite = False
        throw_error = False
        try: 
            overwrite = self._task.args['OVERWRITE']
            if overwrite.lower()== "true":
                overwrite = True
            elif overwrite.lower()== "false":
                overwrite = False
            else:
                throw_error = True
                raise Exception()
        except: 
            if throw_error == True: 
                raise Exception("OVERWRITE_VALUE_CAN_ONLY_BE_TRUE_OR_FALSE")
            else: 
                pass

        # Hardcoded Vars 
        category = 'password'
        url = 'https://dcd.ionos.com/latest'
   
        # Test if secret already exists 
        try: 
            onepwd.get_single_secret(op, item_name=SECRET_NAME, vault=vault)
            print(f"Secret '{SECRET_NAME}' alreay exists in the specified vault!") 
            s3_secret_exists = True
            if overwrite == True: 
                print("However since overwrite is set to True, values will be overwritten if they differ")
                pass
            else: 
                print("Overwrite is NOT set to True. No action taken.")
                return {}
        except onepwd.UnknownResourceItem:
            print("Secret doesn't exist yet")
            s3_secret_exists = False

        # Template creation - BUCKET_NAME, ACCESS_KEY and ACCESS_SECRET
        json_item =f'{{"fields":[{{"id":"password","type":"CONCEALED","purpose":"PASSWORD","label":"password","value":"DUMMY_NOT_USED"}},{{"type":"string","id":"bucket_name","label":"BUCKET_NAME","value":"{BUCKET_NAME}"}},{{"type":"concealed","id":"access_key","label":"ACCESS_KEY","value":"{ACCESS_KEY}"}},{{"type":"concealed","id":"access_secret","label":"ACCESS_SECRET","value":"{ACCESS_SECRET}"}}]}}'
        
        # Upload Secret if no 's3' secret exists
        if s3_secret_exists == False: 
            print("Uploading secret as requested...")
            command = onepwd.OnePwd.create_item(op, category, json_item, title=SECRET_NAME, vault=vault, url=url)
            print("Secret uploaded")
            return {'changed': 'true',
                    'exectued' : command}

        # Overwrite wanted? Update Values   
        if overwrite == True and s3_secret_exists == True: 
            
            # Test if values are alredy configured as requested 
            # secret_value is a list with the secret fields [{'k':'string','n':'bucket_name','t':'BUCKET_NAME','v':'My-Bucket-name'}, ...]
            secret_value = onepwd.get_secret_values_list(op, item_name=SECRET_NAME, vault=vault)
            # True = nothing changed, False = Requested value is different from current value
            check_bucket = True
            check_secret = True
            check_key = True
            if BUCKET_NAME is not None: 
                check_bucket = (secret_value[2]['value'] == BUCKET_NAME)
                if secret_value[2]['value'] == BUCKET_NAME:
                    print("BUCKET_NAME already set as requested")
                else: 
                    print("BUCKET_NAME is different")
            if ACCESS_KEY is not None: 
                check_key = (secret_value[3]['value'] == ACCESS_KEY)
                if secret_value[3]['value'] == ACCESS_KEY:
                    print("ACCESS_KEY already set as requested")
                else: 
                    print("ACCESS_KEY is different")
            if ACCESS_SECRET is not None: 
                check_secret = (secret_value[4]['value'] == ACCESS_SECRET)
                if secret_value[4]['value'] == ACCESS_SECRET:
                    print("ACCESS_SECRET already set as requested")
                else: 
                    print("ACCESS_SECRET is different")

            # Update values if changes are present
            if (check_bucket and check_key and check_secret) == False:
                onepwd.OnePwd.update_s3_values(op, title=SECRET_NAME, vault=vault, BUCKET_NAME=BUCKET_NAME, ACCESS_KEY=ACCESS_KEY, ACCESS_SECRET=ACCESS_SECRET )
                print("Secret updated...") 
                return {'changed': 'true',
                'executed' : 'Secret updated'}
            else: 
                print("Nothing new to update") 
            return {}