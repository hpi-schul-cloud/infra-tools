from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
Provides the ability to set fields in 1Password items and create them if necessary.
For possible field types, see https://developer.1password.com/docs/cli/reference/management-commands/item/#item-edit
'''

EXAMPLES = """
- name: Create Secret
  dbildungscloud.onepwd.item:
    vault: "vault"
    category: "password"
    name: "name"
    fields:
      - name: admin_password
        type: password
        value: password123
      - section: Section 1
        name: username
        type: text
        value: admin
      - name: old password
        type: delete
- name: Delete Secret
  dbildungscloud.onepwd.item:
    state: absent
    vault: "vault"
    name: secret
"""

RETURN = """
Returns the updated item.
"""

import os
import onepwd
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError, AnsibleFileNotFound, AnsibleAction, AnsibleActionFail
from shlex import quote

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

        # new_task = self._task.copy()
        # new_task.args['category'] = category
        # new_task.args['state'] = 'present'

        # create_action = self._shared_loader_obj.action_loader.get('dbildungscloud.onepwd.create_delete_item',
        #                                                                 task=new_task,
        #                                                                 connection=self._connection,
        #                                                                 play_context=self._play_context,
        #                                                                 loader=self._loader,
        #                                                                 templar=self._templar,
        #                                                                 shared_loader_obj=self._shared_loader_obj)
        # create_result = create_action.run(task_vars=task_vars)
    
    def run_present(self, op:onepwd.OnePwd, category, name, vault, fields, check):
        assignment_statements = ""
        for field in fields:
            assignment_statements += " " + build_assignment_statement(field)

        result = {}
        diff = {}
        try:
            get_result = op.get('item', item_name=name, vault=vault)
            # name_or_id = get_item_result['id']
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

def build_assignment_statement(field):
    statement = ""
    if 'section' in field:
        statement += f"{field['section']}."
    statement += field['name']
    if 'type' in field:
        statement += f"[{field['type']}]"
    statement += "="
    if 'value' in field:
        statement += f"{field['value']}"
    escaped_statement = quote(statement)
    return escaped_statement

def items_equal(before, after):
    before_fields = before.get('fields', {})
    before_sections = before.get('sections', {})
    after_fields = after.get('fields', {})
    after_sections = after.get('sections', {})
    return before_fields == after_fields and before_sections == after_sections
