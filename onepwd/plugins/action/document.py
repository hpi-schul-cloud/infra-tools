from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import onepwd
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail
from ..plugin_utils._onepwd_common import get_onepwd_client

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None, **kwargs):
        op = get_onepwd_client(
            service_account_token=self._task.args.get('service_account_token'),
            credentials=self._task.args.get('credentials'),
            credentials_file=self._task.args.get('credentials_file'),
            session_shorthand=self._task.args.get('session_shorthand'),
            session_timeout=kwargs.get('session_timeout', self._task.args.get('session_timeout')),
        )

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
