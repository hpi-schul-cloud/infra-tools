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


# action: schulcloud.onepwd.update  vault='infra-dev' secret_name='TestHello' BUCKET_NAME='my_new_bucket_name'
# See example for content in Docs: https://docs.hpi-schul-cloud.org/display/PROD/1Password

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#action-plugins
class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None, **kwargs):
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)

        # Getting Vars from Ansible 
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


        # # Getting Vars for local testing 
        # title = s3
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
        

        # Chek if secret exists before proceeding
        try: 
            onepwd.get_secret_object(op, item_name=title, vault=vault)
        except:
            print(f"Secret with title '{title}' doesn't exist yet, can't be updated")
            return None

        # Test if values are alredy configured as wanted
        # svalue is a list with the secret fields [{'k':'string','n':'bucket_name','t':'BUCKET_NAME','v':'My-Bucket-name'}, ...]
        svalue = onepwd.get_secret_values_list(op, item_name=title, vault=vault)
        print(svalue)
        if BUCKET_NAME is not None: 
            if svalue[0]['v'] == BUCKET_NAME:
                print("BUCKET_NAME already set as specified")
        if ACCESS_KEY is not None: 
            if svalue[1]['v'] == ACCESS_KEY:
                print("ACCESS_KEY already set as specified")
        if ACCESS_SECRET is not None: 
            if svalue[2]['v'] == ACCESS_SECRET:
                print("ACCESS_SECRET already set as specified")

        # Update Secret
        onepwd.OnePwd.update_item(op, title, vault=vault, BUCKET_NAME=BUCKET_NAME, ACCESS_KEY=ACCESS_KEY, ACCESS_SECRET=ACCESS_SECRET )
        print("Secret updated...")    

# When run locally with python: Use getting Vars to local ones
# ActionModule.run('schulcloud.onepwd.onepwd.OnePwd', task_vars={ 'vault': 'infra-dev', 'ACCESS_SECRET': 'my-new-access-secret',  'ACCESS_KEY': 'my-new-access-key', 'BUCKET_NAME': "My-Bucket-name" })


