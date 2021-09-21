'''
Provides the standard exception class.
'''
class SCTException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
