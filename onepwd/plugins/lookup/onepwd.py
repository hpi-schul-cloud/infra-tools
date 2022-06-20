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
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

import os
import onepwd

display = Display()

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#lookup-plugins

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)
        secret_name=kwargs.get('secret_name', '')
        vault=kwargs.get('vault', None)
        field=kwargs.get('field', None)
        display.vvvv(u"Session shorthand is %s" % session_shorthand)
        display.vvvv(u"Secret name is %s" % secret_name)
        display.vvvv(u"vault is %s" % vault)
        display.vvvv(u"field is %s" % field)
        display.vvvv(u"OP_EMAIL is %s" % os.environ.get("OP_EMAIL"))
        display.vvvv(u"OP_PASSWORD is %s" % os.environ.get("OP_PASSWORD"))
        display.vvvv(u"OP_SUBDOMAIN is %s" % os.environ.get("OP_SUBDOMAIN"))
        display.vvvv(u"OP_SECRET_KEY is %s" % os.environ.get("OP_SECRET_KEY"))
        values=[]
        values.append(onepwd.get_single_secret(op, secret_name, field=field, vault=vault))
        return values
