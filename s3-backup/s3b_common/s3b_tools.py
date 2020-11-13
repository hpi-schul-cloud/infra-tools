
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
