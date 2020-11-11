'''
Provides the standard exception class.
'''
class S3bException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
