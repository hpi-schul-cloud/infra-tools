# Dummy module needed by ansible-doc
DOCUMENTATION = r'''
---
module: item
short_description: Minimal plugin to create 1Password documents
description:
  - Create 1Password documents
  - Updates the item without checking if it's different
  - Will be replaced by the item module when it can be used to upload files
version_added: 2.12.3
author: DBC SRE Team
options:
  vault:
    description:
      - Vault of the document to create.
    type: str
    required: yes
  name:
    description:
      - Name of the document to create.
    type: str
    required: yes
  path:
    description:
        - Path to the file to upload.
    type: str
    required: yes
  session_shorthand:
    description:
      - Session shorthand used by the 1Password CLI.
      - Must be set when running in AWX.
    type: str
    default: the USER environment variable
'''

EXAMPLES = r'''
- name: Create Document
  dbildungscloud.onepwd.document:
    vault: "vault"
    name: "name"
    path: /path/to/file
'''

RETURN = r'''
'''
