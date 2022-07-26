from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
Provides the ability to create a dummy secret in a specified vault (if secret does not already exist), filled with a s3_credentials section. 
This is needed to automate the user and bucket creation process.   
'''

EXAMPLES = """
- name: Create dummy S3 secret in 1Password
  dbildungscloud.onepwd.create_s3_secret:
    vault: "vault"
    SECRET_NAME: "my-new-item"
    USER_EMAIL: "my-user-email"
    LOGIN_URL: "my-login-url"
"""

RETURN = """
If non-existent creates a new secret  with specified name. Does nothing if secret already exists.
Note: If secret already exists and it should be used to save s3_credentials and bucket name, please add the s3_credentials section manually to the secret. 
"""

from subprocess import Popen, PIPE
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_bytes, to_text
from ansible.plugins.action import ActionBase
import os
import onepwd
import url64
import secrets

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#action-plugins
class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None, **kwargs):
        # Log into OnePassword
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)

        # Getting Vars from Ansible 
        # Required values
        try: 
            vault = self._task.args['vault']
            SECRET_NAME = self._task.args['SECRET_NAME']
            USER_EMAIL = self._task.args['USER_EMAIL']
            LOGIN_URL = self._task.args['LOGIN_URL']
        except: 
            pass
            print("""
            ERROR! Couldn't create item.
            Please provide a vault, the USER_EMAIL, SECRET_NAME and LOGIN_URL!
            """) 
            raise Exception("PLEASE_SET_REQUIRED_VALUES - vault, USER_EMAIL, SECRET_NAME and LOGIN_URL")

        # Hardcoded Vars 
        category = 'login'
        USER_PASSWORD = secrets.token_urlsafe(22)

        # Test if secret already exists 
        try: 
            onepwd.get_single_secret(op, item_name=SECRET_NAME, vault=vault)
            print(f"Secret '{SECRET_NAME}' alreay exists in the specified vault!") 
            print("No action to be taken.")
            return {}
        except:
            print(f"SECRET with the name of '{SECRET_NAME}' does not exist yet. Will create it with dummy data")

        # Template creation 
        template = '{ "fields": [ { "designation": "username", "name": "username", "type": "T", "value": "' + str(USER_EMAIL) + '" }, { "designation": "password", "name": "password", "type": "P", "value": "' + str(USER_PASSWORD) + '"} ], "notesPlain": "", "passwordHistory": [], "sections": [ { "fields": [ { "k": "concealed", "n": "internal_name_s3_access_key", "t": "s3_access_key", "v": "s3_access_key" }, { "k": "concealed", "n": "internal_name_s3_access_secret", "t": "s3_access_secret", "v": "s3_access_secret" }, { "k": "string", "n": "internal_name_s3_endpoint_url", "t": "s3_endpoint_url", "v": "s3_endpoint_url" }, { "k": "string", "n": "internal_name_bucket_name", "t": "s3_bucket_name", "v": "s3_bucket_name" } ], "name": "section_name_s3_credentials", "title": "s3_credentials" } ] }'
        encoded_item = url64.encode(template)   
        
        print("Uploading secret as requested...")
        command = onepwd.OnePwd.create_item(op, category, encoded_item, title=SECRET_NAME, vault=vault, url=LOGIN_URL)
        print("Secret uploaded")
        return {'changed': 'true',
                'exectued' : command}
