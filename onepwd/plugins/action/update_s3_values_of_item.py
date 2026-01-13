from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
Provides the ability to edit the s3 values of a secret. Will only take action if OVERWRITE is set to true.
# Conditions:
# - The labels in the section have to exist beforehand.
'''

EXAMPLES = """
- name: Edit S3 credentials
  dbildungscloud.onepwd.update_s3_values_of_item:
    vault: "vault"
    BUCKET_NAME: "bucket-name"
    SECRET_NAME: "secret_name"
    ACCESS_KEY: "access_key"
    ACCESS_SECRET: "access_secret"
    # provide name of the section in which s3 credentials are saved
    SECTION: "s3_credentials"
    ENDPOINT_URL: "s3_url"
    OVERWRITE: True
"""

RETURN = """
Updates the s3 credentials
"""

from subprocess import Popen, PIPE
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_bytes, to_text
from ansible.plugins.action import ActionBase
import os
import onepwd
import url64
import json

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
            ENDPOINT_URL = self._task.args['ENDPOINT_URL']
            SECTION = self._task.args['SECTION']
        except:
            print("""
            ERROR! Couldn't edit s3 secret.
            Please provide a vault, BUCKET_NAME, SECRET_NAME, ACCESS_KEY and ACCESS_SECRET, ENDPOINT_URL and SECTION!
            OVERWRITE is optional and set to 'False' per default. Set to 'True' if you wish to overwrite.
            """)
            raise Exception("PLEASE_SET_REQUIRED_VALUES - vault, BUCKET_NAME, ACCESS_KEY, ACCESS_SECRET, ENDPOINT_URL and SECTION")
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

        # Test if secret already exists
        try:
            onepwd.get_single_secret(op, item_name=SECRET_NAME, vault=vault)
            print(f"Secret '{SECRET_NAME}' exists in the specified vault!")
        except onepwd.UnknownResourceItem:
            raise Exception("Secret does not exist. Therefore it can't be updated.")

        # give feedback on overwrite settings
        if overwrite == True:
            print("Overwrite is set to True, values will be overwritten if they differ")
        else:
            print("Overwrite is NOT set to True. Values will get compared but will not be updated.")

        # get the secrets content of specified section
        secret_value = onepwd.get_secret_values_list_from_section(op, item_name=SECRET_NAME, vault=vault, section=SECTION )
        index = 0
        try:
            while not ("key" in secret_value[index]['label'].lower() and "access" in secret_value[index]['label'].lower()):
                index += 1
            if secret_value[index]['value'] == ACCESS_KEY:
                print("ACCESS_KEY already set as requested")
            else:
                print("ACCESS_KEY is different")
        except:
            raise Exception("No key value pair for ACCESS KEY found")
        check_key = (secret_value[index]['value'] == ACCESS_KEY)
        index=0
        try:
            while not ("secret" in secret_value[index]['label'].lower() and "access" in secret_value[index]['label'].lower()):
                index += 1
            if secret_value[index]['value'] == ACCESS_SECRET:
                print("ACCESS_SECRET already set as requested")
            else:
                print("ACCESS_SECRET is different")
        except:
            raise Exception("No key value pair for ACCESS SECRET found")
        check_secret = (secret_value[index]['value'] == ACCESS_SECRET)
        index=0
        try:
            while not ("endpoint" in secret_value[index]['label'].lower()):
                index += 1
            if secret_value[index]['value'] == ENDPOINT_URL:
                print("ENDPOINT already set as requested")
            else:
                print("ENDPOINT is different")
        except:
            raise Exception("No key value pair for ENDPOINT found")
        check_endpoint_url = (secret_value[2]['value'] == ENDPOINT_URL)
        index=0
        try:
            while not ("bucket" in secret_value[index]['label'].lower()):
                index += 1
            if secret_value[index]['value'] == BUCKET_NAME:
                print("BUCKET_NAME already set as requested")
            else:
                print("BUCKET_NAME is different")
        except:
            raise Exception("No key value pair for BUCKET found")
        check_bucket = (secret_value[3]['value'] == BUCKET_NAME)

        # Update Secret if changes are present
        if (check_bucket and check_key and check_secret and check_endpoint_url) == False and overwrite == True:
            onepwd.OnePwd.update_s3_values_of_standard_s3_item(op, title=SECRET_NAME, vault=vault, BUCKET_NAME=BUCKET_NAME, ACCESS_KEY=ACCESS_KEY, ACCESS_SECRET=ACCESS_SECRET, ENDPOINT_URL=ENDPOINT_URL)
            print("Secret updated...") 
            return {'changed': 'true',
                'executed' : 'Secret updated'}
        print("Nothing new to update")
        return {}
