import os, sys

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
