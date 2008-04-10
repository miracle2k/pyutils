import os, sys

__all__ = (
    'urljoin',
    'urlarg'
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

def urlarg(url, name, value=None):
    """
    If ``name`` and ``value`` are set, the url will be returned in modified
    form with the ``name`` query string parameter set to ``value``. If
    ``value`` is ``False``, a possibly existing ``name`` will be removed
    instead.

    If ``value` is not passed, the value of the query string parameter
    ``name`` in url is returned, or ``None`` if it doesn't exist.

    Querying:
    >>> print urlarg('http://example.org/', 'x')
    None
    >>> urlarg('http://example.org/?x=1', 'x')
    '1'

    Adding an argument:
    >>> urlarg('http://example.org/', 'x', 5)
    'http://example.org/?x=5'

    Changing an argument:
    >>> urlarg('http://example.org/?x=1', 'x', 5)
    'http://example.org/?x=5'

    Deleting  an argument:
    >>> urlarg('http://example.org/?x=1', 'x', False)
    'http://example.org/'

    Delete non-existent argument:
    >>> urlarg('http://example.org/', 'x', False)
    'http://example.org/'

    Set to empty string does not delete:
    >>> urlarg('http://example.org/?x=3', 'x', '')
    'http://example.org/?x='

    If a trailing slash is missing, none is added:
    >>> urlarg('http://example.org/', 'x', 5)
    'http://example.org/?x=5'
    """
    import cgi, urlparse, urllib
    # parse the url and the query string part
    url = [x for x in urlparse.urlparse(url)]
    params = cgi.parse_qs(url[4], keep_blank_values=True)
    # 'get' the param
    if value is None:
        result = params.get(name, None)
        return result and result[0] or None
    #'set' the param
    else:
        if value is not False: params.update({name: value})   # set
        elif name in params: del params[name]    # delete
        # re-encode the url and return
        url[4] = urllib.urlencode(params, doseq=True)
        return urlparse.urlunparse(url)

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

def setup_django(settings_path=None):
    """
    Very useful for setting up standalone scripts that wish to make use of
    a Django environment. ``settings_path`` needs to point to the directory
    where you're project's ``settings.py`` is located, either as an absolute
    path, or as relative path in reference to the module calling this function.

    If ``settings_path`` is not specified or ``False``, a fake settings module
    will be setup. Note that while you'll then be able to work with certain
    Django modules that require this, you're environment is still somewhat
    limited - for example, we cannot put a project on the path in those cases,
    obviously.

    Note that this would probably better fit into ``djutils``. However,
    currently, that package *requires* a working django setup, so for now, we
    put it here.
    """
    if settings_path:
        from django.core.management import setup_environ
        append_sys_path(settings_path, levels=2)    # add project to path
        import settings
        setup_environ(settings)
    else:
        # create a dummy module; note we cannot use ``setup_environ`` as it
        # expects a __file__ attribute on the module object.
        import os, sys, types
        settings_name = '%s_django_settings'%__name__
        sys.modules[settings_name] = types.ModuleType(settings_name)
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_name

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

# self-test
if __name__ == '__main__':
    import doctest
    doctest.testmod()