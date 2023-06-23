from typing import Dict
from enum import Enum
from sct_common.sctexception import SCTException

class SCT_OS(Enum):
    LINUX = 1
    WSL2 = 2
    DEVCONTAINER = 3
    WINDOWS = 4
    
class SystemTools:
    '''
    Dataclass that stores System Tools.
    '''
    def __init__(self):
        '''
        The clustername like 'sc-staging-legacy', the hostname of the API server and the port to access the k8s API.
        '''
        self.devcontainer_args = list()
        self.wsl2_args = list()
        self.linux_args = list()
        self.windows_args = list()
        self.sudo = "sudo"
        self.os = SCT_OS.LINUX


    def addArg(self, arg, os):
        # Depending on the os we use the correct parameter list
        if os == SCT_OS.LINUX:
            self.linux_args.append(arg)
        elif os == SCT_OS.WSL2:
            self.wsl2_args.append(arg)
        elif os == SCT_OS.DEVCONTAINER:
            self.devcontainer_args.append(arg)
        elif os == SCT_OS.WINDOWS:
            self.windows_args.append(arg)
        else:
            return None

    def getArgs(self, os):
        # Depending on the os we use the correct parameter list
        if os == SCT_OS.LINUX:
            return self.linux_args
        elif os == SCT_OS.WSL2:
            return self.wsl2_args
        elif os == SCT_OS.DEVCONTAINER:
            return self.devcontainer_args
        elif os == SCT_OS.WINDOWS:
            return self.windows_args
        else:
            return None
