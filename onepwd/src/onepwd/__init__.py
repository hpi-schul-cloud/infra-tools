import base64
import json
import os
import re
import subprocess
from sys import path
import time
from uuid import uuid4
import sys
import pexpect
import argparse
import yaml
import pyotp

# Quelle: https://github.com/lettdigital/onepassword-python/blob/master/onepassword.py

class DeletionFailure(Exception):
    def __init__(self, item_name, vault):
        message = f"Unable to delete item '{item_name}' from vault '{vault}'"

        super().__init__(message)
        self.message = message


class Unauthorized(Exception):
    pass


class MissingCredentials(Exception):
    pass


class SigninFailure(Exception):
    pass


class UnknownResource(Exception):
    pass


class UnknownResourceItem(Exception):
    pass


class UnknownError(Exception):
    pass


class OnePwd(object):

    def __init__(self, secret=None, shorthand=None, bin_path="", session_timeout=30):
        self.op = os.path.join(bin_path, "op")
        self.session_timeout=session_timeout
        self.session_token=None
        self.session_dir=os.path.join(os.environ.get("HOME"),".config/op/sessions")
        if shorthand is None:
            self.shorthand = str(uuid4())
        else:
            self.shorthand=shorthand
        self.session_file=os.path.join(self.session_dir, self.shorthand)
        if secret is not None:
            self.create_session_dir()
            self.session_token = self.retrieve_cached_token()
            if self.session_token is None:
                self.session_token = self.signin(secret, shorthand=self.shorthand)
            self.cache_token()
        else:
            raise MissingCredentials()

    def list(self, resource, vault=None):
        vault_flag = get_optional_flag(vault=vault)
        op_command = f"{self.op} list {resource} {vault_flag} --session={self.session_token}"
        try:
            return json.loads(run_op_command_in_shell(op_command))
        except json.decoder.JSONDecodeError:
            raise UnknownResource(resource)

    def create_item(self, category, encoded_item, title, vault=None, url=None):
        vault_flag = get_optional_flag(vault=vault)
        url_flag = get_optional_flag(url=url)

        command = f"""
            {self.op} create item {category} '{encoded_item}' \
            --title='{title}' \
            --session={self.session_token} \
            {vault_flag} {url_flag}
        """
        return json.loads(run_op_command_in_shell(command))

    def delete_item(self, item_name, vault=None):
        vault_flag = get_optional_flag(vault=vault)
        op_command = f"{self.op} delete item {item_name} {vault_flag} --session={self.session_token}"
        try:
            run_op_command_in_shell(op_command)
        except subprocess.CalledProcessError:
            raise DeletionFailure(item_name, vault)
        except UnknownError as e:
            error_message = str(e)
            if "multiple items found" in error_message:
                multiple_uuids = []
                rg = re.compile(f"\s*for the item {item_name} in vault {vault}: (.*)")
                for line in error_message.split("\n"):
                    match = rg.match(line)
                    if match:
                        multiple_uuids.append(match.group(1))

                return {"multiple_uuids": multiple_uuids}
            if "no item found" in error_message:
                return "not found"
        return "ok"

    def get(self, resource, item_name, vault=None):
        vault_flag = get_optional_flag(vault=vault)
        op_command = f"{self.op} get {resource} '{item_name}' {vault_flag} --session={self.session_token}"
        try:
            return json.loads(run_op_command_in_shell(op_command))
        except subprocess.CalledProcessError:
            raise UnknownResourceItem(f"{resource}: {item_name}")

    def get_document(self, item_name):
        op_command = f"{self.op} get document '{item_name}' --session={self.session_token}"
        try:
            return run_op_command_in_shell(op_command)
        except subprocess.CalledProcessError:
            raise UnknownResourceItem(f"document: {item_name}")

    def create_session_dir(self):
        try:
            os.makedirs(self.session_dir, mode=0o700, exist_ok=True)
        except OSError:
            print ("Creation of the directory %s failed" % self.session_dir)

    def retrieve_cached_token(self):
        try:
            file_mod_time = os.stat(self.session_file).st_mtime
            now  = time.time()
            if now-file_mod_time > self.session_timeout*60:
                return None
            with open(self.session_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def cache_token(self):
        with open(self.session_file, 'w') as f:
            f.write(self.session_token)
        os.chmod(self.session_file, 0o600)

    def signin(self, secret, shorthand):
        if not os.environ.get("OP_DEVICE"):
            os.environ["OP_DEVICE"] = base64.b32encode(os.urandom(16)).decode().lower().rstrip("=")
        session_flag=get_optional_flag(session=self.session_token)
        child = pexpect.spawn(f"{self.op} signin {secret['signin_address']} {secret['username']} {secret['secret_key']} --output=raw --shorthand={shorthand} {session_flag}",
                              env=os.environ)
        child.expect("Enter the password for")
        child.sendline(secret['password'])
        # Wrapped expected input with own input as child.readline() does not work here
        child.expect("Enter your six-digit authentication code: ")
        twofact_digits=""
        if secret["2fa_token"]:
            totp = pyotp.TOTP(secret["2fa_token"])
            twofact_digits=totp.now()
        else:
            twofact_digits=input("Enter your six-digit authentication code: ")
        child.sendline(twofact_digits)
        child.readline()
        token = child.readline().decode('UTF-8').strip()
        if token.startswith('[ERROR]'):
            raise SigninFailure(f'"{token}" - Please check email, password, subdomain, secret key, 2FA token, and your system time.')
        return token

    def get_version(self):
        return run_op_command_in_shell(f"{self.op} --version")

def run_op_command_in_shell(op_command, verbose=False):
    process = subprocess.run(op_command,
                             shell=True,
                             check=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=os.environ)
    try:
        process.check_returncode()
    except subprocess.CalledProcessError:
        if verbose:
            print(process.stderr.decode("UTF-8").strip())

        error_messages = ["not currently signed in",
                          "Authentication required"]
        full_error_message = process.stderr.decode("UTF-8")
        if any(msg in full_error_message for msg in error_messages):
            raise Unauthorized()
        else:
            raise UnknownError(full_error_message)
    return process.stdout.decode("UTF-8").strip()


def get_optional_flag(**kwargs):
    key, value = list(kwargs.items())[0]
    return (f"--{key}='{value}'"
            if value
            else "")

def get_op_login():
    if not os.environ.get("OP_EMAIL"):
        sys.exit("Please define OP_EMAIL environment variable")
    if not os.environ.get("OP_PASSWORD"):
        sys.exit("Please define OP_PASSWORD environment variable")
    if not os.environ.get("OP_SUBDOMAIN"):
        sys.exit("Please define OP_SUBDOMAIN environment variable")
    if not os.environ.get("OP_SECRET_KEY"):
        sys.exit("Please define OP_SECRET_KEY environment variable")
    twofact_token=os.environ.get("OP_2FA_TOKEN", "")
    return {"password": os.environ.get("OP_PASSWORD"),
             "username": os.environ.get("OP_EMAIL"),
             "signin_address": os.environ.get("OP_SUBDOMAIN"),
             "secret_key": os.environ.get("OP_SECRET_KEY"),
             "2fa_token": twofact_token}

def convert_dot_notation(key, val):
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

def generate_secrets_file(op, items, file, field=None, disable_empty=False, permissions=0o600):
    secrets={}
    sname=""
    svalue=""
    for i in items:
        item=op.get('item',i['uuid'])
        if item["templateUuid"]=='005': # Password template type
            sname=item["overview"]["title"]
            svalue=item["details"]["password"]
            if field and item["details"]["sections"] and item["details"]["sections"][0] and item["details"]["sections"][0]["fields"]:
                for f in item["details"]["sections"][0]["fields"]:
                    if f["t"]==field:
                        svalue=f["v"]
        if item["templateUuid"]=='006': # File template type
            document=op.get_document(i['uuid'])
            sname=item["overview"]["title"]
            svalue=document
        if item["templateUuid"]=='112': # JSON Web Token
            for s in item["details"]["sections"]:
              for f in s["fields"]:
                if f["n"]=="credential":
                  sname=f["n"]
                  svalue=f["v"]
        if disable_empty:
            if svalue:
                subdict=convert_dot_notation(sname, svalue)
                secrets=merge_dictionaries(secrets, subdict)
        else:
            subdict=convert_dot_notation(sname, svalue)
            secrets=merge_dictionaries(secrets, subdict)

    with open(file, 'w') as f:
         yaml.add_representer(str, yaml_str_presenter)
         f.write(yaml.dump(secrets, width=1000, allow_unicode=True, default_flow_style=False).replace("\n\n","\n"))
         os.chmod(file, permissions)

def get_single_secret(op, item_name, field=None, vault=None):
    item=op.get('item', item_name, vault=vault)
    svalue=""
    if item["templateUuid"]=='001': # Login template type
        if field:
          if field=="password":
            for f in item["details"]["fields"]:
                if f["name"]==field:
                    svalue=f["value"]
          elif item["details"]["sections"] and item["details"]["sections"][0] and item["details"]["sections"][0]["fields"]:
            for f in item["details"]["sections"][0]["fields"]:
                if f["t"]==field:
                    svalue=f["v"]
    elif item["templateUuid"]=='005': # Password template type
        svalue=item["details"]["password"]
        if field and item["details"]["sections"] and item["details"]["sections"][0] and item["details"]["sections"][0]["fields"]:
            for f in item["details"]["sections"][0]["fields"]:
                if f["t"]==field:
                    svalue=f["v"]
    elif item["templateUuid"]=='006': # File template type
        document=op.get_document(item['uuid'])
        svalue=document.replace("\n\n","\n")
    elif item["templateUuid"]=='112': # JSON Web Token
        for s in item["details"]["sections"]:
          for f in s["fields"]:
            if f["n"]=="credential":
              svalue=f["v"]
    return svalue

# Converts a string with octal numbers to integer represantion to use it as permission parameter for chmod
def oct2int(x):
   return int(x, 8)

def main():
    parser=argparse.ArgumentParser(description="Generate secrets yaml file")
    parser.add_argument('--vault', type=str, required=True)
    parser.add_argument('--field', type=str, default=None)
    parser.add_argument('--secrets-file', type=str, required=True)
    parser.add_argument('--secrets-file-permissions', type=oct2int, default=0o600, required=False)
    parser.add_argument('--session-shorthand', type=str, required=False)
    parser.add_argument('--session-timeout', type=int, default=30, required=False)
    parser.add_argument('--disable-empty', type=bool, default=False, required=False)
    parser.add_argument('--get-single-secret', type=str, required=False)
    args = parser.parse_args()
    login_secret=get_op_login()
    op = OnePwd(secret=login_secret, shorthand=args.session_shorthand, session_timeout=args.session_timeout)
    if args.get_single_secret:
        secret_value=get_single_secret(op, args.get_single_secret, field=args.field, vault=args.vault)
        with open(args.secrets_file, 'w') as f:
            f.write(secret_value)
            os.chmod(args.secrets_file, args.secrets_file_permissions)
    else:
        items = op.list("items", args.vault)
        generate_secrets_file(op, items, args.secrets_file, args.field, args.disable_empty, args.secrets_file_permissions)
