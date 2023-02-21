from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
---
name: share
short_description: Create 1Password item share links
description:
  - Share existing 1Password items with links.
  - Supports link expiry, view once and restriction to certain emails
version_added: 2.12.3
author: DBC SRE Team
options:
  vault:
    description:
      - Vault of the item to share.
    type: str
    required: yes
  name:
    description:
      - Name of the item to share.
    type: str
    required: yes
  emails:
    description:
      - List of email addresses to share with.
    type: list
    default: []
  expiry:
    description:
      - Link expiring after the specified duration in (s)econds, (m)inutes, or (h)ours.
    type: str
    default: 7h
  view_once:
    description:
      - Expire link after a single view.
    type: bool
    default: false
'''

EXAMPLES = """
- name: Share Secret
  dbildungscloud.onepwd.share:
    vault: "vault"
    name: "name"
- name: Share with email
  dbildungscloud.onepwd.item:
    vault: "vault"
    name: secret
    emails:
      - email@example.com
    expiry: 24h
"""

RETURN = """
Returns the share link.
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
        emails = self._task.args.get('emails', [])
        expiry = self._task.args.get('expiry', None)
        view_once = self._task.args.get('view_once', '')
        if not isinstance(view_once, bool):
            if view_once.lower() in ['true', 'false']:
                view_once = view_once.lower() == 'true'
            else:
                raise AnsibleActionFail('View once must be a boolean')
        # if view_once_raw not in ['true', 'false']:
        #     raise AnsibleActionFail('View_once must be one of true, false.')
        # view_once = view_once_raw == 'true'
        if view_once and expiry != None:
            raise AnsibleActionFail("View_once and expiry can be used simultaneously.")
        check = self._task.check_mode

        result = {}
        result['changed'] = True
        share_result = {}
        if check:
            share_result['link'] = 'dummy-link'
        else:
            share_result = op.share(name, vault=vault, emails=emails, expiry=expiry, view_once=view_once)
        result['link'] = share_result['link']
        return result
