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
from shlex import quote

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

class DuplicateItems(Exception):
    pass

class UnknownError(Exception):
    pass

class InvalidOnePwdVersion(Exception):
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
            
        check_version = self.get_version()
        split_version=check_version.split(".")
        if not(int(split_version[0]) == 2 and int(split_version[1])>=7):
            raise InvalidOnePwdVersion("1Password CLI 2 (2.7 or higher) is required. To check version use: \"op --version\"")
        

    def list(self, resource, vault=None):
        vault_flag = get_optional_flag(vault=vault)
        op_command = f"{self.op} {resource} list {vault_flag} --session={self.session_token}"
        try:
            return json.loads(run_op_command_in_shell(op_command))
        except json.decoder.JSONDecodeError:
            raise UnknownResource(resource)

    def create_item(self, category, json_item, title, vault=None, url=None):
        vault_flag = get_optional_flag(vault=vault)
        url_flag = get_optional_flag(url=url)

        command = f"""
            {self.op} item  create --category={category} - \
            --title='{title}' \
            --session={self.session_token} \
            {vault_flag} {url_flag}
        """
        return json.loads(run_op_command_in_shell(command, input=json_item.encode()))

    def create_item_string(self, category, title, assignment_statements:str, vault=None, url=None, dry_run=False):
        vault_flag = get_optional_flag(vault=vault)
        url_flag = get_optional_flag(url=url)
        dry_run_flag = get_optional_flag(dry_run=dry_run)

        command = f"""
            {self.op} item  create --category={category} - \
            --title='{title}' \
            --session={self.session_token} \
            {vault_flag} {url_flag} \
            {assignment_statements} {dry_run_flag}
        """
        return json.loads(run_op_command_in_shell(command))

    # used in the ansible action 'upload_s3_secret'
    def update_s3_values(self, title, vault=None, ACCESS_KEY=None, ACCESS_SECRET=None, BUCKET_NAME=None ):
        fields_to_change = ""
        if ACCESS_KEY is not None:
            fields_to_change += f"ACCESS_KEY={ACCESS_KEY} "
        if ACCESS_SECRET is not None:
            fields_to_change += f"ACCESS_SECRET={ACCESS_SECRET} "
        if BUCKET_NAME is not None:
            fields_to_change += f"BUCKET_NAME={BUCKET_NAME} "
        return self.edit_item(title, fields_to_change, vault)

    # used in ansible action update_s3_values_of_item
    def update_s3_values_of_server_item(self, title, vault=None, ACCESS_KEY=None, ACCESS_SECRET=None, BUCKET_NAME=None, ENDPOINT_URL=None):
        fields_to_change = ""
        if ACCESS_KEY is not None:
            fields_to_change += f"FILES_STORAGE__S3_ACCESS_KEY_ID={ACCESS_KEY} "
        if ACCESS_SECRET is not None:
            fields_to_change += f"FILES_STORAGE__S3_SECRET_ACCESS_KEY={ACCESS_SECRET} "
        if BUCKET_NAME is not None:
            fields_to_change += f"FILES_STORAGE__S3_BUCKET={BUCKET_NAME} "
        if ENDPOINT_URL is not None:
            fields_to_change += f"FILES_STORAGE__S3_ENDPOINT={ENDPOINT_URL} "
        return self.edit_item(title, fields_to_change, vault)

    # used in ansible action update_s3_values_of_item used by nextcloud and ionos-s3-password-backup
    def update_s3_values_of_standard_s3_item(self, title, vault=None, ACCESS_KEY=None, ACCESS_SECRET=None, BUCKET_NAME=None, ENDPOINT_URL=None):
        fields_to_change = ""
        if ACCESS_KEY is not None:
            fields_to_change += f"s3_access_key={ACCESS_KEY} "
        if ACCESS_SECRET is not None:
            fields_to_change += f"s3_access_secret={ACCESS_SECRET} "
        if BUCKET_NAME is not None:
            fields_to_change += f"s3_bucket_name={BUCKET_NAME} "
        if ENDPOINT_URL is not None:
            fields_to_change += f"s3_endpoint_url={ENDPOINT_URL} "
        return self.edit_item(title, fields_to_change, vault)

    def edit_item(self, title, assignment_statements:str, vault=None, dry_run=False):
        vault_flag = get_optional_flag(vault=vault)
        dry_run_flag = get_optional_flag(dry_run=dry_run)
        command = f""" {self.op} item edit '{title}' --session={self.session_token} {vault_flag} {dry_run_flag} {assignment_statements} """
        return json.loads(run_op_command_in_shell(command))

    def delete_item(self, item_name, vault=None):
        vault_flag = get_optional_flag(vault=vault)
        op_command = f"{self.op} item delete '{item_name}' {vault_flag} --session={self.session_token}"
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
        op_command = f"{self.op} {resource} get '{item_name}' {vault_flag} --session={self.session_token}"
        try:
            return json.loads(run_op_command_in_shell(op_command))
        except subprocess.CalledProcessError:
            raise UnknownResourceItem(f"{resource}: {item_name}")

    def get_document(self, item_name):
        op_command = f"{self.op} document get '{item_name}' --session={self.session_token}"
        try:
            return run_op_command_in_shell(op_command)
        except subprocess.CalledProcessError:
            raise UnknownResourceItem(f"document: {item_name}")
    
    def share(self, item_name, vault=None, emails=[], expiry=None, view_once=False):
        vault_flag = get_optional_flag(vault=vault)
        emails_list = ",".join(emails)
        emails_flag = get_optional_flag(emails=emails_list)
        view_once_flag = "--view-once" if view_once else ""
        
        op_command = f"{self.op} item share '{item_name}' {vault_flag} {emails_flag} {view_once_flag} --session={self.session_token}"
        return run_op_command_in_shell(op_command)


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
        child = pexpect.spawn(f"{self.op} account add --signin --address {secret['signin_address']} --email {secret['email']} --secret-key {secret['secret_key']} --raw --shorthand={shorthand} {session_flag}",
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


def run_op_command_in_shell(op_command:str, input:str=None, verbose:bool=False) -> str:
    os.environ["OP_FORMAT"] = "json"
    process = subprocess.run(op_command,
                             shell=True,
                             check=False,
                             input=input,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=os.environ)

    try:
        process.check_returncode()
    except subprocess.CalledProcessError:
        if verbose:
            print(process.stderr.decode("UTF-8").strip())

        unauthorized_error_messages = ["not currently signed in",
                          "Authentication required"]
        full_error_message = process.stderr.decode("UTF-8")
        if any(msg in full_error_message for msg in unauthorized_error_messages):
            raise Unauthorized()
        elif "More than one item matches" in full_error_message:
            raise DuplicateItems()
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
             "email": os.environ.get("OP_EMAIL"),
             "signin_address": os.environ.get("OP_SUBDOMAIN"),
             "secret_key": os.environ.get("OP_SECRET_KEY"),
             "2fa_token": twofact_token}

def convert_dot_notation(key, val) -> dict:
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
    secret_value=""
    for i in items:
        item=op.get('item',i['id'])
        if item["category"]=='PASSWORD': # Password template type
            sname=item["title"]
            if field is None:
                field = "password"
            for f in item["fields"]:
                if f["label"]==field:
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
            secrets=merge_dictionaries(secrets, subdict)

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
                if f["label"]==field:
                    secret_value=f["value"]
    elif item["category"]=='PASSWORD': # Password template type
        if field is None:
            field = "password"
        for f in item["fields"]:
                if f["label"]==field and "value" in f:
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
