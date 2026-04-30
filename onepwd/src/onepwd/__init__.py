import base64
import json
import os
import re
import subprocess
from sys import path
import time
from uuid import uuid4
import pexpect
import argparse
import yaml
import pyotp
from shlex import quote
from getpass import getpass
# Quelle: https://github.com/lettdigital/onepassword-python/blob/master/onepassword.py

class DeletionError(Exception):
  def __init__(self, item_name, vault):
    message = f"Unable to delete item '{item_name}' from vault '{vault}'"

    super().__init__(message)
    self.message = message


class UnauthorizedError(Exception):
  pass


class MissingCredentialsError(Exception):
  def __init__(self, missing_keys: str, extra_message=None, code=None):
    message = f'Missing credentials to login to 1password: {missing_keys}{f" ({extra_message})" if extra_message else ""}'
    super().__init__(message)


class SigninError(Exception):
  pass


class UnknownResourceError(Exception):
  pass


class UnknownResourceItem(Exception):
  pass

class DuplicateItemsError(Exception):
  pass

class UnknownError(Exception):
  pass

class InvalidOnePwdVersion(Exception):
  pass


class OnePwd(object):

  def __init__(self, secret=None, service_account_token=None, shorthand=None, bin_path="", session_timeout=30):
    self.op = os.path.join(bin_path, "op")
    self.session_timeout = session_timeout
    self.session_token = None
    self.service_account_token = service_account_token
    self.use_service_account = service_account_token is not None

    if not self.use_service_account:
      self.session_dir = os.path.join(os.environ.get("HOME"), ".config/op/sessions")
      if shorthand is None:
        self.shorthand = str(uuid4())
      else:
        self.shorthand = shorthand
      self.session_file = os.path.join(self.session_dir, self.shorthand)
      self.create_session_dir()
      self.session_token = self.retrieve_cached_token()
      if self.session_token is None:
        self.session_token = self.signin(secret, shorthand=self.shorthand)
      self.cache_token()

    check_version = self.get_version()
    split_version = check_version.split(".")
    if not (int(split_version[0]) == 2 and int(split_version[1]) >= 7):
      raise InvalidOnePwdVersion("1Password CLI 2 (2.7 or higher) is required. To check version use: \"op --version\"")

  def _session_flag(self):
    self._env = os.environ
    twofact_digits=input("Enter your six-digit authentication code: ")
    child.sendline(twofact_digits)
    child.readline()
    token = child.readline().decode('UTF-8').strip()
    if token.startswith('[ERROR]'):
      raise SigninError(f'"{token}" - Please check email, password, subdomain, secret key, 2FA token, and your system time.')
    return token

  def get_version(self):
    return run_op_command_in_shell(f"{self.op} --version")


def run_op_command_in_shell(op_command:str, input:str=None, verbose:bool=False, env:dict=None) -> str:
  env = env or os.environ
  env["OP_FORMAT"] = "json"
  process = subprocess.run(op_command,
                           shell=True,
                           check=False,
                           input=input,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           env=env)

  try:
    process.check_returncode()
  except subprocess.CalledProcessError:
    if verbose:
      print(process.stderr.decode("UTF-8").strip())

    unauthorized_error_messages = ["not currently signed in",
                                   "Authentication required"]
    full_error_message = process.stderr.decode("UTF-8")
    if any(msg in full_error_message for msg in unauthorized_error_messages):
      raise UnauthorizedError()
    elif "More than one item matches" in full_error_message:
      raise DuplicateItemsError()
    elif "isn't an item" in full_error_message:
      raise UnknownResourceItem()
    else:
      raise UnknownError(full_error_message)
  return process.stdout.decode("UTF-8").strip()


def get_optional_flag(**kwargs):
  key, value = list(kwargs.items())[0]
  return (f"--{key.replace('_', '-')}='{value}'"
          if value
          else "")

def get_op_login_from_env() -> dict:
  if not os.environ.get("OP_EMAIL"):
    raise MissingCredentialsError('OP_EMAIL', extra_message="Check if env vars are set up properly")
  if not os.environ.get("OP_PASSWORD"):
    raise MissingCredentialsError('OP_PASSWORD', extra_message="Check if env vars are set up properly")
  if not os.environ.get("OP_SUBDOMAIN"):
    raise MissingCredentialsError('OP_SUBDOMAIN', extra_message="Check if env vars are set up properly")
  if not os.environ.get("OP_SECRET_KEY"):
    raise MissingCredentialsError('OP_SECRET_KEY', extra_message="Check if env vars are set up properly")

  result = {
    "email": os.environ.get("OP_EMAIL"),
    "password": os.environ.get("OP_PASSWORD"),
    "signin_address": os.environ.get("OP_SUBDOMAIN"),
    "secret_key": os.environ.get("OP_SECRET_KEY")
  }

  if os.environ.get("OP_2FA_TOKEN"):
    result["2fa_token"] = os.environ.get("OP_2FA_TOKEN")
  return result

def get_op_login_from_args(credentials: dict) -> dict:
  if "OP_EMAIL" not in credentials:
    raise MissingCredentialsError('OP_EMAIL', extra_message="Check credential dictionary. Keys must be uppercase")
  if "OP_PASSWORD" not in credentials:
    raise MissingCredentialsError('OP_PASSWORD', extra_message="Check credential dictionary. Keys must be uppercase")
  if "OP_SUBDOMAIN" not in credentials:
    raise MissingCredentialsError('OP_SUBDOMAIN', extra_message="Check credential dictionary. Keys must be uppercase")
  if "OP_SECRET_KEY" not in credentials:
    raise MissingCredentialsError('OP_SECRET_KEY', extra_message="Check credential dictionary. Keys must be uppercase")

  result = {
    "password": credentials["OP_PASSWORD"],
    "email": credentials["OP_EMAIL"],
    "signin_address": credentials["OP_SUBDOMAIN"],
    "secret_key": credentials["OP_SECRET_KEY"]
  }

  if "OP_2FA_TOKEN" in credentials:
    result["2fa_token"] = credentials["OP_2FA_TOKEN"]
  return result

def get_op_login_from_file(file_path: str) -> dict:
  with open(file_path, 'r') as file:
    credentials = json.load(file)
    if "OP_EMAIL" not in credentials:
      raise MissingCredentialsError('OP_EMAIL', extra_message="Check credential file. Keys must be uppercase")
    if "OP_PASSWORD" not in credentials:
      raise MissingCredentialsError('OP_PASSWORD', extra_message="Check credential file. Keys must be uppercase")
    if "OP_SUBDOMAIN" not in credentials:
      raise MissingCredentialsError('OP_SUBDOMAIN', extra_message="Check credential file. Keys must be uppercase")
    if "OP_SECRET_KEY" not in credentials:
      raise MissingCredentialsError('OP_SECRET_KEY', extra_message="Check credential file. Keys must be uppercase")

    result = {
      "password": credentials["OP_PASSWORD"],
      "email": credentials["OP_EMAIL"],
      "signin_address": credentials["OP_SUBDOMAIN"],
      "secret_key": credentials["OP_SECRET_KEY"]
    }

    if "OP_2FA_TOKEN" in credentials:
      result["2fa_token"] = credentials["OP_2FA_TOKEN"]
    return result

def convert_dot_notation(key, val) -> dict:
  print(key, val)
  split_list = key.split('.')
  if  len(split_list) == 1: # no dot notation found
    return {key:val}
  split_list.reverse()
  newval = val
  item = None
  for item in split_list:
    if  item == split_list[-1]:
      return {item:newval}
    newval = {item:newval}
  return {item:newval}

def merge_dictionaries(dict1, dict2):
  for key, val in dict1.items():
    if isinstance(val, dict):
      dict2_node = dict2.setdefault(key, {})
      merge_dictionaries(val, dict2_node)
    else:
      if key not in dict2:
        dict2[key] = val
  return dict2
# See https://stackoverflow.com/a/33300001
def yaml_str_presenter(dumper, data):
  if len(data.splitlines()) > 1:  # check for multiline string
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)

# TODO this function does not work as i would expect it and is not easy to use, recommend rework
def generate_secrets_file(op, items, file, field=None, disable_empty=False, permissions=0o600):
  secrets={}
  sname=""
  secret_value=""
  for i in items:
    item=op.get('item',i['id'])
    if item["category"] in ['LOGIN', 'PASSWORD']: # Login / Password template
      sname=item["title"]
      if field is None:
        field = "password"
      for f in item["fields"]:
        if "label" in f and f["label"]==field:
          secret_value=f["value"]
    elif item["category"]=='DOCUMENT': # File template type
      sname=item["title"]
      secret_value=op.get_document(i['id'])
    elif item["category"]=='API_CREDENTIAL': # JSON Web Token
      for f in item["fields"]:
        if f["id"]=="credential":
          secret_value=f["value"]
          sname=f["id"]   # TODO: item["title"]?
    if disable_empty:
      if secret_value:
        subdict=convert_dot_notation(sname, secret_value)
        secrets=merge_dictionaries(secrets, subdict)
    else:
      subdict=convert_dot_notation(sname, secret_value)
      print(subdict)
      secrets=merge_dictionaries(secrets, subdict)

  print(secrets)

  with open(file, 'w') as f:
    yaml.add_representer(str, yaml_str_presenter)
    f.write(yaml.dump(secrets, width=1000, allow_unicode=True, default_flow_style=False).replace("\n\n","\n"))
    os.chmod(file, permissions)

def get_single_secret(op:OnePwd, item_name:str, field=None, vault=None) -> str:
  item=op.get('item', item_name, vault=vault)
  secret_value=""
  if item["category"]=='LOGIN': # Login template type
    if field:
      for f in item["fields"]:
        if "label" in f and f["label"]==field:
          secret_value=f["value"]
  elif item["category"]=='PASSWORD': # Password template type
    if field is None:
      field = "password"
    for f in item["fields"]:
      if "label" in f and f["label"]==field and "value" in f:
        secret_value=f["value"]
  elif item["category"]=='DOCUMENT': # File template type
    document=op.get_document(item['id'])
    secret_value=document.replace("\n\n","\n")
  elif item["category"]=='API_CREDENTIAL': # JSON Web Token
    for f in item["fields"]:
      if f["id"]=="credential":
        secret_value=f["value"]
  return secret_value

# used in the ansible action 'upload_s3_secret'
def get_secret_values_list(op, item_name,  vault=None):
  item=op.get('item', item_name, vault=vault)
  secret_value=""
  if item["category"]=='LOGIN' or item["category"]=='PASSWORD': # Password or Login template type
    secret_value=item["fields"]
  else:
    raise Exception('The secret has not the password or login template type!')
  return secret_value

# used in ansible action update_s3_values_of_item
# filters for the values in a specefied section
def get_secret_values_list_from_section(op, item_name,  vault=None, section=None):
  item=op.get('item', item_name, vault=vault)
  if section is None:
    raise Exception('Section name not set! Please provide section name')
  secret_fields = []
  if item["category"]=='LOGIN' or item["category"]=='PASSWORD': # Password or Login template type
    section_exists = False
    if item['sections']:
      for s in item['sections']:
        try:
          if s['label'] == section:
            section_exists = True
            break
        except:
          pass
    if not section_exists:
      raise Exception('Section name could not be found! Please check it!')

    for f in item['fields']:
      try:
        if 'section' in f and f['section']['label'] == section:
          secret_fields.append(f)
      except:
        pass
  else:
    raise Exception('The secret has not the password or login template type!')

  return secret_fields

# Converts a string with octal numbers to integer represantion to use it as permission parameter for chmod
def oct2int(x):
  return int(x, 8)

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

def main():
  parser=argparse.ArgumentParser(description="Generate secrets yaml file")
  # secret location args
  parser.add_argument('--vault', type=str, required=True)
  parser.add_argument('--field', type=str, default=None)

  # credential args
  parser.add_argument('--subdomain', type=str)
  parser.add_argument('--email', type=str)
  parser.add_argument('--secret-key', type=str)
  parser.add_argument('--twofa-token', type=str)
  parser.add_argument('--credentials-file', type=str)
  parser.add_argument('--service-account-token', type=str)

  # output args
  parser.add_argument('--secrets-file', type=str, required=True)
  parser.add_argument('--secrets-file-permissions', type=oct2int, default=0o600, required=False)
  parser.add_argument('--session-shorthand', type=str, required=False)
  parser.add_argument('--session-timeout', type=int, default=30, required=False)
  parser.add_argument('--disable-empty', type=bool, default=False, required=False)
  parser.add_argument('--get-single-secret', type=str, required=False)

  args = parser.parse_args()

  if args.service_account_token:
    op = OnePwd(service_account_token=args.service_account_token, shorthand=args.session_shorthand, session_timeout=args.session_timeout)
  elif args.subdomain or args.email or args.secret_key or args.twofa_token:
    if not(args.subdomain) or not(args.email) or not(args.secret_key):
      print("When using argument credential login, all arguments --subdomain, --email and --secret-key are needed")
      print("Exiting...")
      exit(1)

    password = getpass(prompt='Password: ')
    credentials= {
      "OP_EMAIL": args.email,
      "OP_PASSWORD": password,
      "OP_SUBDOMAIN": args.subdomain,
      "OP_SECRET_KEY": args.secret_key,
    }
    if args.twofa_token:
      credentials["OP_2FA_TOKEN"] = args.twofa_token
    login_secret=get_op_login_from_args(credentials)
    op = OnePwd(secret=login_secret, shorthand=args.session_shorthand, session_timeout=args.session_timeout)
  elif args.credentials_file:
    login_secret=get_op_login_from_file(args.credentials_file)
    op = OnePwd(secret=login_secret, shorthand=args.session_shorthand, session_timeout=args.session_timeout)
  else:
    login_secret=get_op_login_from_env()
    op = OnePwd(secret=login_secret, shorthand=args.session_shorthand, session_timeout=args.session_timeout)
  if args.get_single_secret:
    secret_value=get_single_secret(op, args.get_single_secret, field=args.field, vault=args.vault)
    with open(args.secrets_file, 'w') as f:
      f.write(secret_value)
      os.chmod(args.secrets_file, args.secrets_file_permissions)
  else:
    items = op.list("items", args.vault)
    generate_secrets_file(op, items, args.secrets_file, args.field, args.disable_empty, args.secrets_file_permissions)
