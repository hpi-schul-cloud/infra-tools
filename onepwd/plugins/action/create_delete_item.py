from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
Provides the ability to create and delete 1Password items.
'''

EXAMPLES = """
- name: Create Secret
  dbildungscloud.onepwd.create_delete_item:
    state: present
    vault: "vault"
    category: "password"
    name: "name"
"""

RETURN = """
If state is present returns the item under result.item, if state is absent deletes item.
"""

import os
import onepwd
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError, AnsibleFileNotFound, AnsibleAction, AnsibleActionFail

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None, **kwargs):
        login_secret=onepwd.get_op_login()
        session_shorthand=kwargs.get('session_shorthand', os.getenv('USER'))
        session_timeout=kwargs.get('session_timeout', 30)
        op = onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)

        # Input validation
        for arg in ['vault', 'name', 'category']:
            if arg not in self._task.args:
                raise AnsibleActionFail(f"Parameter '{arg}' is required.")
        vault = self._task.args.get('vault')
        name = self._task.args.get('name')
        category = self._task.args.get('category')
        state = self._task.args.get('state', 'present')
        if state not in ('present', 'absent'):
            raise AnsibleActionFail('State must be one of absent, present.')
        check = self._task.check_mode

        result = {}
        if state == 'present':
            result = self.run_present(op, category, name, vault, check)
        if state == 'absent':
            result = self.run_absent(op, name, vault, check)
        return result

    def run_present(self, op:onepwd.OnePwd, category, name, vault, check):
        result = {}
        item = {}
        try:
            item = op.get('item', item_name=name, vault=vault)
            result['changed'] = False
        except onepwd.UnknownResourceItem:
            if not check:
                item = op.create_empty_item(category=category, title=name, vault=vault)
            result['changed'] = True
        result['item'] = item
        # result["diff"]["after"] = item
        return result

    def run_absent(self, op:onepwd.OnePwd, name, vault, check):
        result = {}
        try:
            item = op.get('item', item_name=name, vault=vault)
            if not check:
                op.delete_item(item_name=name, vault=vault)
            result['changed'] = True
        except onepwd.UnknownResourceItem:
            result['changed'] = False
        return result
