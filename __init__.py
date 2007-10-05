import os, sys

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

"""
    Get file name, line number, function name and
    source text of the caller's caller as 4-tuple:
    (file, line, func, text).

    The optional argument 'up' allows retrieval of
    a caller further back up into the call stack.

    Note, the source text may be None and function
    name may be '?' in the returned result.  In
    Python 2.3+ the file name may be an absolute
    path.
"""
def get_caller(up=1):
    import traceback
    try:  # just get a few frames
        f = traceback.extract_stack(limit=up+2)
        if f:
           return f[0]
    except:
        if __debug__:
           traceback.print_exc()
        pass
    # running with psyco?
    return ('', 0, '', None)

"""
    Append a path to the system path. Can take multiple arguments, in the
    same way os.path.join() does. Relative paths are considered to be relative
    to the calling module's filename.

    This is primarily useful if you want to include a module who's location
    in the filesystem you are aware of, say, two levels up.
"""
def append_sys_path(*path):
   dir = os.path.abspath(os.path.join(os.path.dirname(get_caller()[0]), *path))
   if not dir in sys.path:
     sys.path.append(dir)