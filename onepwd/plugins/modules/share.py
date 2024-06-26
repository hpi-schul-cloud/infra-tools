# Dummy module needed by ansible-doc
DOCUMENTATION = r'''
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
  session_shorthand:
    description:
      - Session shorthand used by the 1Password CLI.
      - Must be set when running in AWX.
    type: str
    default: the USER environment variable
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

- name: Share Secret with credentials dictionary
  dbildungscloud.onepwd.share:
    vault: "vault"
    name: "name"
      credentials: 
        OP_EMAIL: <email>
        OP_PASSWORD": <password>
        OP_SUBDOMAIN": <subdomain>
        OP_SECRET_KEY": <secret-key>
        OP_2FA_TOKEN": <2fa-token>

- name: Share Secret with credentials file
  dbildungscloud.onepwd.share:
    vault: "vault"
    name: "name"
    credentials_file: path/to/file.json
'''

RETURN = r'''
link:
  description: The created share link.
  returned: always
  type: str
  sample: https://1password.eu/share-link
'''
