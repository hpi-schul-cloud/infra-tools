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
'''

RETURN = r'''
link:
  description: The created share link.
  returned: always
  type: str
  sample: https://1password.eu/share-link
'''
