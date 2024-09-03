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
        # Log into OnePassword
        if 'credentials' in kwargs:
            login_secret=onepwd.get_op_login_from_args(kwargs['credentials'])
        elif 'credentials_file' in kwargs:
            login_secret=onepwd.get_op_login_from_file(kwargs['credentials_file'])
        else:
            login_secret=onepwd.get_op_login_from_env()

        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        display.debug(u"Session shorthand is %s" % session_shorthand)
        display.debug(u"Secret name is %s" % kwargs.get('secret_name', ''))
        display.debug(u"vault is %s" % kwargs.get('vault', None))
        display.debug(u"field is %s" % kwargs.get('field', None))
        display.debug(u"OP_EMAIL is %s" % os.environ.get("OP_EMAIL"))
        display.debug(u"OP_PASSWORD is %s" % os.environ.get("OP_PASSWORD"))
        display.debug(u"OP_SUBDOMAIN is %s" % os.environ.get("OP_SUBDOMAIN"))
        display.debug(u"OP_SECRET_KEY is %s" % os.environ.get("OP_SECRET_KEY"))
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)
        secret_name=kwargs.get('secret_name', '')
        vault=kwargs.get('vault', None)
        field=kwargs.get('field', None)
        ignore_not_found=kwargs.get('ignore_not_found', False)
        values=[]
        try:
            values.append(onepwd.get_single_secret(op, secret_name, field=field, vault=vault))
        except onepwd.UnauthorizedError:
            raise AnsibleError("Unauthorized")
        except onepwd.DuplicateItemsError:
            raise AnsibleError(f"More than one item named {secret_name} in vault {vault}")
        except onepwd.UnknownResourceItem:
            if ignore_not_found:
                return None
            raise AnsibleError(f"No item named {secret_name} in vault {vault}")
        except onepwd.UnknownError as unknown_error:
            raise AnsibleError(unknown_error)
        return values
