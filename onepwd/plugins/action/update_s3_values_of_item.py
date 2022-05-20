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
import json

# Provides the ability to edit the s3 values of a secret. Will only take action if OVERWRITE is set to true.
# Conditions: 
# - The labels in the section have to exist beforehand.
# - The order of the labels always has to be: Acces Key, Access Secret, Endpoint, Url
# How to use in Ansible: 
# action: schulcloud.onepwd.upload_s3_secret vault=infra-dev BUCKET_NAME=my-bucket-name SECRET_NAME=my-s3-name ACCESS_KEY=my-access-key ACCESS_SECRET=my-access-secret ENPOINT_URL=my-endpoint-url SECTION=my-section OVERWRITE=True

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
            if overwrite in ['True', 'true', 'TRUE', True]:
                overwrite = True
            elif overwrite in ['False', 'false', 'FALSE', False]:
                overwrite = False
            elif overwrite not in ['True', 'true', 'TRUE', 'False', 'false', 'FALSE', True, False]:
                throw_error = True
                print("Error - Set OVERWRITE to True or False")
                raise Exception("OVERWRITE_VALUE_CAN_ONLY_BE_TRUE_OR_FALSE")
        except: 
            if throw_error == True: 
                raise Exception("OVERWRITE_VALUE_CAN_ONLY_BE_TRUE_OR_FALSE")
            else: 
                pass

        # Getting Vars for local testing (using Python)
        # vault = task_vars['vault']
        # try: 
        #     BUCKET_NAME = task_vars['BUCKET_NAME']
        #     SECRET_NAME = task_vars['SECRET_NAME']
        #     ACCESS_KEY = task_vars['ACCESS_KEY']
        #     ACCESS_SECRET = task_vars['ACCESS_SECRET']
        #     ENDPOINT_URL = task_vars['ENDPOINT_URL']
        #     SECTION = task_vars['SECTION']
        # except: 
        #     print("""
        #     ERROR! Could't upload s3 secret.
        #     Please provide a BUCKET_NAME, SECRET_NAME, ACCESS_KEY, ACCESS_SECRET, ENDPOINT_URL and SECTION!
        #     """)
        # # optinal values
        # overwrite = True
        # throw_error = False
        # try: 
        #     overwrite = task_vars['OVERWRITE']
        #     if overwrite in ['True', 'true', 'TRUE', True]:
        #         overwrite = True
        #     elif overwrite in ['False', 'false', 'FALSE', False]:
        #         overwrite = False
        #     elif overwrite not in ['True', 'true', 'TRUE', 'False', 'false', 'FALSE', True, False]:
        #         throw_error = True
        #         print("Error - Set OVERWRITE to True or False")
        #         return {error}
        # except: 
        #     if throw_error == True: 
        #         return {OVERWRITE_VALUE_CAN_ONLY_BE_TRUE_OR_FALSE}
        #     else: 
        #         pass
   
        # Test if secret already exists 
        try: 
            onepwd.get_single_secret(op, item_name=SECRET_NAME, vault=vault)
            print(f"Secret '{SECRET_NAME}' exists in the specified vault!") 
        except:
            raise Exception("Secret does not exist. Therefore it can't be updated.")
        
        # give feedabck on overwrite settings
        if overwrite == True: 
            print("Overwrite is set to True, values will be overwritten if they differ")
            pass
        else: 
            print("Overwrite is NOT set to True. Values will get compared but will not be updated.")
  
        # get the secrets content of specified section
        svalue = onepwd.get_secret_values_list_from_section(op, item_name=SECRET_NAME, vault=vault, section=SECTION )
        check_key = (svalue[0]['v'] == ACCESS_KEY)
        if svalue[0]['v'] == ACCESS_KEY:
            print("ACCESS_KEY already set as requested")
        else: 
            print("ACCESS_KEY is different")
        check_secret = (svalue[1]['v'] == ACCESS_SECRET)
        if svalue[1]['v'] == ACCESS_SECRET:
            print("ACCESS_SECRET already set as requested")
        else: 
            print("ACCESS_SECRET is different")
        check_endpoint_url = (svalue[2]['v'] == ENDPOINT_URL)
        if svalue[2]['v'] == ENDPOINT_URL:
            print("ENDPOINT_URL already set as requested")
        else: 
            print("ENDPOINT_URL is different")
        check_bucket = (svalue[3]['v'] == BUCKET_NAME)
        if svalue[3]['v'] == BUCKET_NAME:
            print("BUCKET_NAME already set as requested")
        else: 
            print("BUCKET_NAME is different")

        # Update Secret if changes are present
        if (check_bucket and check_key and check_secret and check_endpoint_url) == False and overwrite == True:
            if SECRET_NAME == "nextcloud": 
                onepwd.OnePwd.update_s3_values_of_nextcloud_item(op, title=SECRET_NAME, vault=vault, BUCKET_NAME=BUCKET_NAME, ACCESS_KEY=ACCESS_KEY, ACCESS_SECRET=ACCESS_SECRET, ENDPOINT_URL=ENDPOINT_URL)
            elif SECRET_NAME == "server": 
                onepwd.OnePwd.update_s3_values_of_server_item(op, title=SECRET_NAME, vault=vault, BUCKET_NAME=BUCKET_NAME, ACCESS_KEY=ACCESS_KEY, ACCESS_SECRET=ACCESS_SECRET, ENDPOINT_URL=ENDPOINT_URL)
            else: 
                raise Exception("Secret is neither the server nor the nextcloud secret. Upload function for any other secret not implemented yet")
            print("Secret updated...") 
            return {'changed': 'true',
                'executed' : 'Secret updated'}
        print("Nothing new to update") 
        return {}

# When run locally with python: Use getting Vars to local ones (using python)
# ActionModule.run('schulcloud.onepwd.onepwd.OnePwd', task_vars={ 'vault': 'infra-dev', 'SECRET_NAME': 'Aimees-Test2', 'BUCKET_NAME': 'my-bucket-name', 'ACCESS_SECRET': 'my-access-secret', 'ACCESS_KEY': 'my-access-key', 'ENDPOINT_URL': 'my-endpoint-url', 'SECTION': 'my-section'})


