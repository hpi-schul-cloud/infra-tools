# Dummy module needed by ansible-doc
DOCUMENTATION = r'''
---
module: item
short_description: Manage 1Password items
description:
  - Create 1Password items
  - Add and remove fields
version_added: 2.13.0
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
      - Supported properties are name, type, value, section, overwrite 
      - The overwrite on a single field only applies to that one field (useful for randomly generated password)
    type: list
    default: []
  session_shorthand:
    description:
      - Session shorthand used by the 1Password CLI.
      - Must be set when running in AWX.
    type: str
    default: the USER environment variable
  generate_password:
    description:
      - 1Password generates the password 
      - Password properties can be set (e.g. "letters,digits,symbols,32"), see https://developer.1password.com/docs/cli/create-item/#create-an-item
    type: str
  overwrite:
    description:
      - If True (default) existing items are changed if there are differences
      - If False existing items are not changed if there are differences (usefull if item should be generated only once)
    type: bool
    default: True
  credentials:
    description:
      - Allows passing credentials as dictionary
      - dict must contain keys {"OP_EMAIL", "OP_PASSWORD", "OP_SUBDOMAIN", "OP_SECRET_KEY"}
      - Key OP_2FA_TOKEN is optional
    type: dict
  credentials_file:
    description:
      - Allows passing credentials as file
      - The file must be json
      - The file must contain a dictionary with the keys {"OP_EMAIL", "OP_PASSWORD", "OP_SUBDOMAIN", "OP_SECRET_KEY"}
      - Key OP_2FA_TOKEN is optional
    type: dict
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
        overwrite: False
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

- name: Create Secret with credentials dictionary
  dbildungscloud.onepwd.item:
    vault: "vault"
    category: "password"
    name: "name"
    fields:
      - name: admin_password
        type: password
        value: password123
        overwrite: False
      credentials: 
        OP_EMAIL: <email>
        OP_PASSWORD": <password>
        OP_SUBDOMAIN": <subdomain>
        OP_SECRET_KEY": <secret-key>
        OP_2FA_TOKEN": <2fa-token>

- name: Create Document with credentials file
  dbildungscloud.onepwd.item:
    vault: "vault"
    category: "password"
    name: "name"
    credentials_file: path/to/file.json
    fields:
      - name: admin_password
        type: password
        value: password123
        overwrite: False
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
