'''
Provides the standard exception class.
'''
class DBCMException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
