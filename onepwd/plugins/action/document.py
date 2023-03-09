from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import os
import onepwd
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None, **kwargs):
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)

        # Input validation
        for arg in ['vault', 'name', 'path']:
            if arg not in self._task.args:
                raise AnsibleActionFail(f"Parameter '{arg}' is required.")
        vault = self._task.args.get('vault')
        name = self._task.args.get('name')
        path = self._task.args.get('path')
        check = self._task.check_mode

        if not check:
            try:
                op.edit_document_from_file(path, name, vault)
            except onepwd.UnknownResourceItem:
                op.create_document_from_file(path, name, vault)
        return {'changed': True}
