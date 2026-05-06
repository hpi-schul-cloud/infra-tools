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
from ..plugin_utils._onepwd_common import get_onepwd_client

import onepwd

display = Display()

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#lookup-plugins

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        op = get_onepwd_client(
          service_account_token=kwargs.get('service_account_token'),
          credentials=kwargs.get('credentials'),
          credentials_file=kwargs.get('credentials_file'),
          session_shorthand=kwargs.get('session_shorthand'),
          session_timeout=kwargs.get('session_timeout'),
        )

        display.debug(u"Secret name is %s" % kwargs.get('secret_name', ''))
        display.debug(u"vault is %s" % kwargs.get('vault', None))
        display.debug(u"field is %s" % kwargs.get('field', None))
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
                return []
            raise AnsibleError(f"No item named {secret_name} in vault {vault}")
        except onepwd.UnknownError as unknown_error:
            raise AnsibleError(unknown_error)
        return values
