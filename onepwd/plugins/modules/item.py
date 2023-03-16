# Dummy module needed by ansible-doc
DOCUMENTATION = r'''
---
module: item
short_description: Manage 1Password items
description:
  - Create 1Password items
  - Add and remove fields
version_added: 2.12.3
author: DBC SRE Team
options:
  vault:
    description:
      - Vault of the item being managed.
    type: str
    required: yes
  name:
    description:
      - Name of the item being managed.
    type: str
    required: yes
  state:
    description:
      - If C(absent) the item will be deleted.
      - If C(present) the item will be created/updated.
      - Default is C(present).
    type: str
    default: present
    choices:
      - absent
      - present
  category:
    description:
      - Type of the item being managed.
      - This is ignored if an item with the right name and vault already exists.
      - Default is password.
    type: str
    default: password
  fields:
    description:
      - Fields to add/remove from the item, see https://developer.1password.com/docs/cli/reference/management-commands/item/#item-edit
      - Supported properties are name, type, value, section
    type: list
    default: []
  session_shorthand:
    description:
      - Session shorthand used by the 1Password CLI.
      - Must be set when running in AWX.
    type: str
    default: the USER environment variable
'''

EXAMPLES = r'''
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
'''

RETURN = r'''
item:
  description: The created/updated item.
  returned: When state is C(present).
  type: str
  sample:
    title: my secret
    type: PASSWORD
    fields:
      label: username
      type: STRING
      value: admin
'''
