import os, sys, pathlib
from sct_common.sctexception import SCTException
from sct_data.systemtools import SystemTools, SCT_OS
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
    sct_systemtools: SystemTools = SystemTools()
    ip_addr = "127.0.0.1"
    user_home = pathlib.Path.home()
    if user_home == None:
        sys.exit(1)
    if sys.platform.startswith("linux"):
        # linux or wsl
        rc = os.system('uname -a | grep -i microsoft 2>&1 > /dev/null')
        if rc == 0: # wsl or dev-container, booth are using MS generated Linux systems
            rc = os.system('uname -a | grep -i microsoft 2>&1 > /dev/null')
            if not os.environ.get('REMOTE_CONTAINERS'):
                # WSL
                sct_systemtools.sudo = "gsudo.exe"
                sct_systemtools.addArg('gsudo.exe', SCT_OS.WSL2)
                sct_systemtools.addArg('hostctl.exe', SCT_OS.WSL2)
                sct_systemtools.os = SCT_OS.WSL2
            else:
                # Remote container
                # This will modify the mounted hosts file in WSL2
                sct_systemtools.sudo = "sudo"
                sct_systemtools.addArg('sudo', SCT_OS.WSL2)
                sct_systemtools.addArg('hostctl', SCT_OS.WSL2)
                hostname = socket.gethostname()    
                ip_addr = socket.gethostbyname(hostname)
                sct_systemtools.addArg('--host-file', SCT_OS.WSL2)
                sct_hostfile = os.path.join(pathlib.Path.home(),'.hosts')
                sct_systemtools.addArg(sct_hostfile, SCT_OS.WSL2)
                sct_systemtools.addArg ('--ip', SCT_OS.WSL2)
                sct_systemtools.addArg (ip_addr, SCT_OS.WSL2)
                sct_systemtools.os = SCT_OS.DEVCONTAINER
                # Setting the host entry also inside the devcontainer
                sct_systemtools.addArg('sudo', SCT_OS.DEVCONTAINER)
                sct_systemtools.addArg('hostctl', SCT_OS.DEVCONTAINER)
        else:
            # Plain Linux
            sct_systemtools.sudo = "sudo"
            sct_systemtools.addArg('sudo', SCT_OS.LINUX)
            sct_systemtools.addArg('hostctl', SCT_OS.LINUX)
            sct_systemtools.os = SCT_OS.LINUX
    elif sys.platform.startswith("win32"):
        # WIndows
        sct_systemtools.sudo = "gsudo.exe"
        sct_systemtools.addArg('gsudo.exe', SCT_OS.WINDOWS)
        sct_systemtools.addArg('hostctl.exe', SCT_OS.WINDOWS)
        sct_systemtools.os = SCT_OS.WINDOWS
    else:
        return None
    return sct_systemtools

def enableSudochache ():
    sct_systemtools = getSystemtools()
    if sct_systemtools.os == SCT_OS.WINDOWS:
#        os.system('{} --loglevel none'.format(sct_sudo))
        os.system('{} --loglevel none cache on -d -1'.format(sct_systemtools.sudo))

def disableSudochache ():
    sct_systemtools = getSystemtools()
    if sct_systemtools.os == SCT_OS.WINDOWS:
#        os.system('{} config --global --reset'.format(sct_sudo))
        os.system('{} --loglevel none cache off'.format(sct_systemtools.sudo))

