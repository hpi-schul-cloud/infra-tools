import os
import onepwd


def get_onepwd_client(
    service_account_token=None,
    credentials=None,
    credentials_file=None,
    session_shorthand=None,
    session_timeout=30,
):
    if service_account_token:
      return onepwd.OnePwd(service_account_token)
    else:
      #Log into OnePassword
      if credentials:
        login_secret=onepwd.get_op_login_from_args(credentials)
      elif credentials_file:
        login_secret=onepwd.get_op_login_from_file(credentials_file)
      else:
        login_secret=onepwd.get_op_login_from_env()
      if session_shorthand is None:
        session_shorthand = os.getenv('USER')

      return onepwd.OnePwd(secret=login_secret, shorthand=session_shorthand, session_timeout=session_timeout)
