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


        # # Getting Vars from Ansible 
        # title = self._task.args['secret_name']
        # vault = self._task.args['vault']
        # try: 
        #     BUCKET_NAME = self._task.args['BUCKET_NAME']
        #     print("BUCKET_NAME given - will be updated")
        # except:  
        #     BUCKET_NAME = None
        #     print("BUCKET_NAME not given")
        # try: 
        #     ACCESS_KEY = self._task.args['ACCESS_KEY']
        #     print("ACCESS_KEY given - will be updated")
        # except:  
        #     ACCESS_KEY = None
        #     print("ACCESS_KEY not given")
        # try: 
        #     ACCESS_SECRET = self._task.args['ACCESS_SECRET']
        #     print("ACCESS_SECRET given - will be updated")
        # except:  
        #     ACCESS_SECRET = None
        #     print("ACCESS_SECRET not given")


        # Getting Vars for local testing 
        title = task_vars['secret_name']
        vault = task_vars['vault']
        try: 
            BUCKET_NAME = task_vars['BUCKET_NAME']
            print("BUCKET_NAME given")
        except:  
            BUCKET_NAME = None
            print("BUCKET_NAME not given")
        try: 
            ACCESS_KEY = task_vars['ACCESS_KEY']
            print("ACCESS_KEY given")
        except:  
            ACCESS_KEY = None
            print("ACCESS_KEY not given")
        try: 
            ACCESS_SECRET = task_vars['ACCESS_SECRET']
            print("ACCESS_SECRET given")
        except:  
            ACCESS_SECRET = None
            print("ACCESS_SECRET not given")
        

        # test if config is already as specified 
        
        # if BUCKET_NAME is not None: 
        #    bucket_name = onepwd.get_single_secret(op, item_name=title, field=BUCKET_NAME, vault=vault)
        #    print("bucket name")
        #print(onepwd.get_single_secret(op, item_name=title, field=BUCKET_NAME, vault=vault))


        
        onepwd.OnePwd.update_item(op, title, vault=vault, BUCKET_NAME=BUCKET_NAME, ACCESS_KEY=ACCESS_KEY, ACCESS_SECRET=ACCESS_SECRET )
        print("Secret updated...")    

# When run like this set Getting Vars, to local ones
ActionModule.run('schulcloud.onepwd.onepwd.OnePwd', task_vars={'secret_name': 'Test100', 'vault': 'infra-dev', 'ACCESS_SECRET': 'my-new-access-secret',  'ACCESS_KEY': 'my-new-access-key', 'BUCKET_NAME': "My-Bucket-name" })


