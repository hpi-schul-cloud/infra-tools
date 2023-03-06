from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

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
        for arg in ['vault', 'name']:
            if arg not in self._task.args:
                raise AnsibleActionFail(f"Parameter '{arg}' is required.")
        vault = self._task.args.get('vault')
        name = self._task.args.get('name')
        category = self._task.args.get('category', 'password')
        fields = self._task.args.get('fields', [])
        if not isinstance(fields, list):
            raise AnsibleActionFail("Fields must be a list.")
        for field in fields:
            validate_field(field)
        state = self._task.args.get('state', 'present')
        if state not in ('present', 'absent'):
            raise AnsibleActionFail('State must be one of absent, present.')
        check = self._task.check_mode

        result = {}
        if state == 'present':
            result = self.run_present(op, category, name, vault, fields, check)
        if state == 'absent':
            result = self.run_absent(op, name, vault, check)
        return result
    
    def run_present(self, op:onepwd.OnePwd, category, name, vault, fields, check):
        assignment_statements = ""
        for field in fields:
            assignment_statements += " " + onepwd.build_assignment_statement(field)

        result = {}
        diff = {}
        try:
            get_result = op.get('item', item_name=name, vault=vault)
            edit_result = op.edit_item(name, assignment_statements, vault=vault, dry_run=check)
            changed = not items_equal(get_result, edit_result)
            if changed:
                if not check:
                    edit_result = op.edit_item(name, assignment_statements, vault=vault)
                diff['before'] = get_result
                diff['after'] = edit_result
                result['item'] = edit_result
            else:
                result['item'] = get_result
        except onepwd.UnknownResourceItem:
            create_result = op.create_item_string(category, name, assignment_statements, vault=vault, dry_run=check)
            diff['before'] = {}
            diff['after'] = create_result
            result['item'] = create_result
            changed = True

        result['diff'] = diff
        result['changed'] = changed
        return result

    def run_absent(self, op:onepwd.OnePwd, name, vault, check):
        result = {}
        try:
            op.get('item', item_name=name, vault=vault)
            if not check:
                op.delete_item(item_name=name, vault=vault)
            result['changed'] = True
        except onepwd.UnknownResourceItem:
            result['changed'] = False
        return result

def validate_field(field):
    if not isinstance(field, dict):
        raise AnsibleActionFail("Fields must be a list of dictionaries.")
    for key in ['name']:
        if key not in field:
            raise AnsibleActionFail(f"Key {key} is required in {field}.")
    for key in ['name', 'type', 'section', 'value']:
        if not isinstance(key, str):
            raise AnsibleActionFail(f"{key} must be a string.")

def items_equal(before, after):
    before_fields = before.get('fields', {})
    before_sections = before.get('sections', {})
    after_fields = after.get('fields', {})
    after_sections = after.get('sections', {})
    return before_fields == after_fields and before_sections == after_sections
