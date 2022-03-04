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


# Provides the ability to update one value or multiple values of a secret named 's3' in OnePassword  
# How to use in Ansible:
# action: schulcloud.onepwd.update_s3_secret vault=infra-dev  ACCESS_KEY=my-access-key BUCKET_NAME=my-bucket-name ACCESS_SECRET=my-access-secret

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#action-plugins
class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None, **kwargs):
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)

        #Getting Vars from Ansible 
        title = 's3'
        vault = self._task.args['vault']
        try: 
            BUCKET_NAME = self._task.args['BUCKET_NAME']
            print("BUCKET_NAME given")
        except:  
            BUCKET_NAME = None
        try: 
            ACCESS_KEY = self._task.args['ACCESS_KEY']
            print("ACCESS_KEY given")
        except:  
            ACCESS_KEY = None
        try: 
            ACCESS_SECRET = self._task.args['ACCESS_SECRET']
            print("ACCESS_SECRET given")
        except:  
            ACCESS_SECRET = None


        # # Getting Vars for local testing (using Python)
        # title = 's3'
        # vault = task_vars['vault']
        # try: 
        #     BUCKET_NAME = task_vars['BUCKET_NAME']
        #     print("BUCKET_NAME given")
        # except:  
        #     BUCKET_NAME = None
        #     print("BUCKET_NAME not given")
        # try: 
        #     ACCESS_KEY = task_vars['ACCESS_KEY']
        #     print("ACCESS_KEY given")
        # except:  
        #     ACCESS_KEY = None
        #     print("ACCESS_KEY not given")
        # try: 
        #     ACCESS_SECRET = task_vars['ACCESS_SECRET']
        #     print("ACCESS_SECRET given")
        # except:  
        #     ACCESS_SECRET = None
        #     print("ACCESS_SECRET not given")
        

        # Check if secret exists before proceeding
        try: 
            onepwd.get_secret_values_list(op, item_name=title, vault=vault)
        except:
            print("However - Secret with title 's3' doesn't exist yet, can't be updated. Use the upload_s3_secret action to upload a new secret. ")
            return {}

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
                print("BUCKET_NAME already set as specified")
            else: 
                print("BUCKET_NAME is different")
        if ACCESS_KEY is not None: 
            check_key = (svalue[1]['v'] == ACCESS_KEY)
            if svalue[1]['v'] == ACCESS_KEY:
                print("ACCESS_KEY already set as specified")
            else: 
                print("ACCESS_KEY is different")
        if ACCESS_SECRET is not None: 
            check_secret = (svalue[2]['v'] == ACCESS_SECRET)
            if svalue[2]['v'] == ACCESS_SECRET:
                print("ACCESS_SECRET already set as specified")
            else: 
                print("ACCESS_SECRET is different")

        # Update Secret if changes are present
        if (check_bucket and check_key and check_secret) == False:
            onepwd.OnePwd.update_item(op, title, vault=vault, BUCKET_NAME=BUCKET_NAME, ACCESS_KEY=ACCESS_KEY, ACCESS_SECRET=ACCESS_SECRET )
            print("Secret updated...") 
        else: 
            print("Nothing new to update") 
        return {}

# When run locally with python: Use getting Vars to local ones (using python)
# ActionModule.run('schulcloud.onepwd.onepwd.OnePwd', task_vars={ 'vault': 'infra-dev', 'ACCESS_SECRET': 'my-new-acccasess-secret',  'ACCESS_KEY': 'my-new-access-key', 'BUCKET_NAME': "My-Bucket-name" })


