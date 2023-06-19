import os, sys, pathlib
from sct_common.sctexception import SCTException
from sct_data.shellcmd import ShellCmd
import socket    

def sizeof_fmt(num, suffix='B'):
    result = None
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            result ="%3.1f%s%s" % (num, unit, suffix)
            break
        num /= 1024.0
    if result == None:
        result = "%.1f%s%s" % (num, 'Yi', suffix)
    return result

def get_absolute_path(a_file):
    '''
    Returns the given file as absolute path.

    Checks, if the given file is an absolute path. If not
    the script path is prepended.
    '''
    a_file_abs = a_file
    if not os.path.isabs(a_file):
        script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        a_file_abs = os.path.join(script_path, a_file)
    return a_file_abs

def getSystemtools():
    sct_sudo = "sudo"
    sct_hostctl: ShellCmd = ShellCmd()
    sct_windows = False
    user_home = ""
    IPAddr = "127.0.0.1"
    if sys.platform.startswith("linux"):
        # linux or wsl
        user_home = pathlib.Path.home()
        if user_home == None:
            sys.exit(1)
        rc = os.system('uname -a | grep -i microsoft 2>&1 > /dev/null')
        if rc == 0: # wsl or dev-container, booth are using MS generated Linux systems
            rc = os.system('uname -a | grep -i microsoft 2>&1 > /dev/null')
            if not os.environ.get('REMOTE_CONTAINERS'):
                sct_sudo = "gsudo.exe"
                sct_hostctl.addArg('gsudo.exe')
                sct_hostctl.addArg('hostctl.exe')
                sct_windows = True
            else:
                # Remote container
                sct_sudo = "sudo"
                sct_hostctl.addArg('sudo')
                sct_hostctl.addArg('hostctl')
                hostname = socket.gethostname()    
                IPAddr = socket.gethostbyname(hostname)
                sct_hostctl.addArg('--host-file')
                sct_hostfile = os.path.join(pathlib.Path.home(),'.hosts')
                sct_hostctl.addArg(sct_hostfile)
                sct_hostctl.addArg ('--ip')
                sct_hostctl.addArg (IPAddr)
        else:
                sct_sudo = "sudo"
                sct_hostctl.addArg('sudo')
                sct_hostctl.addArg('hostctl')
                sct_windows = False
    elif sys.platform.startswith("win32"):
        sct_sudo = "gsudo.exe"
        sct_hostctl.addArg('gsudo.exe')
        sct_hostctl.addArg('hostctl.exe')
        sct_windows = True
    return (sct_sudo, sct_hostctl, sct_windows)

def enableSudochache ():
    sct_sudo, sct_hostctl, sct_windows = getSystemtools()
    if sct_windows:
#        os.system('{} --loglevel none'.format(sct_sudo))
        os.system('{} --loglevel none cache on -d -1'.format(sct_sudo))

def disableSudochache ():
    sct_sudo, sct_hostctl, sct_windows = getSystemtools()
    if sct_windows:
#        os.system('{} config --global --reset'.format(sct_sudo))
        os.system('{} --loglevel none cache off'.format(sct_sudo))

