from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
Provides the ability to set fields in 1Password items and create them if necessary.
For possible field types, see https://developer.1password.com/docs/cli/reference/management-commands/item/#item-edit
'''

EXAMPLES = """
- name: Update Secret
  dbildungscloud.onepwd.update_item:
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
"""

RETURN = """
Returns the updated item.
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
        check = self._task.check_mode
        
        new_task = self._task.copy()
        new_task.args['category'] = category
        new_task.args['state'] = 'present'

        create_action = self._shared_loader_obj.action_loader.get('dbildungscloud.onepwd.create_delete_item',
                                                                        task=new_task,
                                                                        connection=self._connection,
                                                                        play_context=self._play_context,
                                                                        loader=self._loader,
                                                                        templar=self._templar,
                                                                        shared_loader_obj=self._shared_loader_obj)
        create_result = create_action.run(task_vars=task_vars)

        assignment_statements = ""
        for field in fields:
            assignment_statements += " " + build_assignment_statement(field)

        dry_run_result = op.edit_item(name, assignment_statements, vault=vault, dry_run=True)
        diff = {}
        diff['before'] = create_result['item']
        diff['after'] = dry_run_result
        changed = not items_equal(create_result['item'], dry_run_result)

        if not check and changed :
            run_result = op.edit_item(name, assignment_statements, vault=vault)
            diff['after'] = run_result

        result = {}
        result['diff'] = diff
        result['changed'] = changed
        result['item'] = result['diff']['after']
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
    return statement

def items_equal(before, after):
    before_fields = before.get('fields', {})
    before_sections = before.get('sections', {})
    after_fields = after.get('fields', {})
    after_sections = after.get('sections', {})
    return before_fields == after_fields and before_sections == after_sections
