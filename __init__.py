import os

"""
    Join any arbitrary strings into a forward-slash delimited list.
    Do not strip leading / from first element, nor trailing / from last element.
    
    From: http://coderseye.com/2006/the-best-python-url_join-routine-ever.html
"""
def urljoin(*args):
    if len(args) == 0:
        return ""
    
    if len(args) == 1:
        return str(args[0])
    
    else:
        args = [str(arg).replace("\\", "/") for arg in args]
        work = [args[0]]
        for arg in args[1:]:
            if arg.startswith("/"):
                work.append(arg[1:])
            else:
                work.append(arg)
    
        joined = reduce(os.path.join, work)
    
    return joined.replace("\\", "/")