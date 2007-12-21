import os, sys

__all__ = (
    'urljoin',
    'get_caller',
    'append_sys_path',
    'equal_floats',
    'setup_django',
    'strdump',
    'print_r',
)

def urljoin(*args):
    """
    Join any arbitrary strings into a forward-slash delimited list.
    Do not strip leading / from first element, nor trailing / from last element.

    From: http://coderseye.com/2006/the-best-python-url_join-routine-ever.html
    """
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

def get_caller(up=1):
    """
    Get file name, line number, function name and source text of the caller's
    caller as 4-tuple: (file, line, func, text).

    The optional argument 'up' allows retrieval of a caller further back up
    into the call stack.

    Note, the source text may be None and function name may be '?' in the
    returned result.  In Python 2.3+ the file name may be an absolute path.

    From: http://mail.python.org/pipermail/python-list/2005-February/308489.html
    """
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

def append_sys_path(*path, **kwargs):
    """
    Append a path to the system path. Can take multiple arguments, in the
    same way os.path.join() does. Relative paths are considered to be relative
    to the calling module's filename (this can be changed by the "levels"
    parameter - the default is "1" - each level is one level on the stack, to
    find the module that will be used as a base for relative filenames).

    This is primarily useful if you want to include a module who's location
    in the filesystem you are aware of, say, two levels up.
    """
    levels = kwargs.get('levels', 1)
    dir = os.path.abspath(os.path.join(os.path.dirname(get_caller(up=levels)[0]), *path))
    if not dir in sys.path:
        sys.path.append(dir)

def equal_floats(f1, f2, digits=11):
    """
    Compares two float values, and returns a boolean indicating whether they
    are the same with respect to a certain treshold/resolution/precision.

    The digits parameter takes an integer indicating the number of
    digits/decimal places/resolution you wish to use for the comparison. The
    default is 11, which seems to be the max mysql precision on my installation,
    when I was required to write this function.

    Note that this function might return True of something like f1=1e-12 and
    f2=1e-112, i.e. it does not take into account the relative difference, so
    it may or may not be for you. A different solution would possible do:
        abs(f1 - f2) < abs(f1) * 1e-6
    See this forum thread for some discussion on the topic:
        http://www.velocityreviews.com/forums/t351983-precision-for-equality-of-two-floats.html

    Good information on the subject can also be found here:
        http://www.cygnus-software.com/papers/comparingfloats/comparingfloats.htm
        http://docs.python.org/tut/node16.html
    """
    import math
    threshold = 10**-digits
    return not (math.fabs(f1 - f2) > threshold)

def setup_django(settings_path):
    """
    Very useful for setting up standalone scripts that wish to make use of
    a django environment. "settings_path" needs to be relative or absolute
    path to the directory where you're projects settings.py is located.
    Note that "relative" means in reference to the calling module.

    Note that this function would maybe better fit into "djutils". However,
    currently, that package *requires* a working django setup, so for now,
    we put it here instead.
    """
    from django.core.management import setup_environ
    # add project to path
    append_sys_path(settings_path, levels=2)
    # import project and setup
    import settings
    setup_environ(settings)

def strdump(str, filename):
    """
    Simply output a string to a file, overriding any existing content.
    Useful for debugging.
    """
    file = open(filename, 'w+')
    try:
        file.write(str)
    finally:
        file.close()

def print_r(obj, level=1, indent=' '*4):
    """
    Similar to PHP's print_r, although in it's current version it is simply
    useful for outputting dicts with a bit of formatting, indentation etc.
    """
    def out(what): sys.stdout.write("%s"%what)
    if isinstance(obj, dict):
        out("{\n")
        for key, value in obj.items():
            out(level*indent+"'%s': "%key)
            print_r(value, level+1, indent)
            out(",\n")
        out((level-1)*indent+"}")
    else:
        out("%s"%repr(obj))  # use repr() so we can output tuples
    # need a final linebreak at the very end for the root element
    if level==1: out("\n")