import os, sys
import cgi
import urlparse
import urllib


__all__ = (
    'urljoin',
    'urlarg', 'urlargs',
    'get_caller',
    'append_sys_path',
    'equal_floats',
    'setup_django',
    'strdump',
    'print_r',
    'raise_unsupported_args',
    'profileit',
)


def urljoin(*args):
    """Join any arbitrary strings into a forward-slash delimited list.

    Do not strip leading / from first element, nor trailing / from
    last element.

    From: http://coderseye.com/2006/the-best-python-url_join-routine-ever.html

    TODO: It's worth noting that this function doesn't resolve ..\, and
    thus, sucks. ``urlparse.urljoin`` seems to be nicer in pretty much
    every respect.

    With Unicode:
    >>> urljoin(u'Viva_Pi\\xf1ata_DS.html')
    u'Viva_Pi\\xf1ata_DS.html'
    """

    if len(args) == 0:
        return ""

    if len(args) == 1:
        return args[0]

    else:
        args = [arg.replace("\\", "/") for arg in args]
        work = [args[0]]
        for arg in args[1:]:
            if arg.startswith("/"):
                work.append(arg[1:])
            else:
                work.append(arg)

        joined = reduce(os.path.join, work)

    return joined.replace("\\", "/")


def urlargs(url, *queries, **changes):
    """Modify or retrieve url querystring arguments.

    ``url`` can either be a string (the url from which the querystring
    arguments are retrieved from), or a dict of querystring arguments
    in the form ``name`` => ``value``. In the latter case, instead of
    the modified url, only the querystring part will be returned.

    Modification:
    -------------

    Provide the changes you would like to make as keyword arguments -
    the url will be modified to have the query string values set
    appropriately to match the key-value pairs given.

    If the value of such a keyword argument is ``False`` or ``None``, a
    possibly existing query string parameter with that the argument's
    name will be removed instead.

    Retrieval:
    ----------

    Alternatively, instead of keyword aguments, you may pass any
    number of strings as positional arguments. The function will then
    return the appropriate values as read form the querystring.


    Querying:
    >>> print urlargs('http://example.org/', 'x')
    (None,)
    >>> urlargs('http://example.org/?x=1', 'x')
    ('1',)
    >>> urlargs('http://example.org/?x=1', 'x', 'y')
    ('1', None)

    Adding an argument:
    >>> urlargs('http://example.org/', x=5)
    'http://example.org/?x=5'

    Changing an argument:
    >>> urlargs('http://example.org/?x=1', x=5)
    'http://example.org/?x=5'

    Deleting  an argument:
    >>> urlargs('http://example.org/?x=1', x=False)
    'http://example.org/'
    >>> urlargs('http://example.org/?x=1', x=None)
    'http://example.org/'

    Delete non-existent argument:
    >>> urlargs('http://example.org/', x=None)
    'http://example.org/'

    Set to empty string does not delete:
    >>> urlargs('http://example.org/?x=3', x='')
    'http://example.org/?x='

    We can do multiple changes at once:
    >>> urlargs('http://example.org/?x=3&y=abc', x=None, y='cde', z=1)
    'http://example.org/?y=cde&z=1'

    Instead of a url, a dictionary of query parameters may be passed
    >>> urlargs({}, x=1)
    '?x=1'
    >>> urlargs({'x': '1'}, x=2)
    '?x=2'
    >>> urlargs({'x': '1'}, 'x')
    ('1',)
    >>> urlargs({'x': '1'}, x=False)
    ''

    If a trailing slash is missing, none is added:
    >>> urlargs('http://example.org/', x=5)
    'http://example.org/?x=5'

    Check various functionality when unicode is involved:
    >>> urlargs(u'http://example.org/?x=ä', x='ü')
    u'http://example.org/?x=%C3%BC'
    >>> urlargs(u'http://example.org/?x=ä', 'x')
    (u'\\xc3\\xa4',)
    >>> urlargs(u'http://example.org/?', **{'ä': 'ü'})
    u'http://example.org/?%C3%A4=%C3%BC'

    Our function takes extra care to accept unicode for both name
    and value by converting it to utf8. How much sense that actually
    makes, if webservers even accept the result or when - but be
    that as it may for now (in fact, some practical tests seem to
    indicate that most webservers won't handle utf8 encoding here
    correctly; see also Wikipedia "Percent-encoding"
    (oldid=225230345), which points to the 2005 rf3986 that suggests
    utf8 for *new* uri schemes).
    >>> urlargs(u'http://example.org/?', **{'a': u'ü'})
    u'http://example.org/?a=%C3%83%C2%BC'

    # This part is no longer supported with the new syntax, since
    # keyword args may not be unicode.
    #>>> urlargs(u'http://example.org/?', changes={u'ä': u'ü'})
    #u'http://example.org/?%C3%83%C2%A4=%C3%83%C2%BC'

    Apparently, when a querystring part (here the final "?") is
    missing, the tuple returned by urlparse() contains bytestrings
    only, even if the input was unicode. This is then also reflected
    in a non-unicode return value of our function. Not really a
    per-design behaviour or even desirable, but we'd like to know if
    it changes at some point.
    >>> urlargs(u'http://example.org/', **{})
    'http://example.org/'

    Mixing modify and query mode is an error
    >>> urlargs('http://example.org/', 'x', y=1)
    Traceback (most recent call last):
    ...
    TypeError: cannot mix query and modify mode

    If a dictionary is used, the original is not modified
    >>> a = {}
    >>> urlargs(a, x=1)
    '?x=1'
    >>> a
    {}
    """

    if queries and changes:
        raise TypeError('cannot mix query and modify mode')

    # we need the query params as a dict, if necessary parse the url
    if isinstance(url, dict):
        params = url.copy()   # we'll need to modify this locally, so copy
        url = ['', '', '', '', '', '']
    else:
        url = list(urlparse.urlparse(url))
        params = dict(cgi.parse_qsl(url[4], keep_blank_values=True))

    # query arguments
    if queries:
        return tuple([params.get(name, None) for name in queries])

    # modify arguments
    else:
        for name, value in changes.items():
            # urlencode() chokes on unicode input (exception if it
            # can't convert a key to ascii, and "encode-replaces"
            # values. So we convert to utf8 upfront.
            if isinstance(name, unicode):
                name = name.encode('utf8')
            if isinstance(value, unicode):
                value = value.encode('utf8')

            if not value in (False, None,):
                params.update({name: value})
            elif name in params:
                del params[name]
        # re-encode the url and return
        url[4] = urllib.urlencode(params, doseq=True)
        return urlparse.urlunparse(url)

def urlarg(url, name, value=None):
    """Simplified version of ``urlargs`` that can only change or query a
    single argument.

    It is kept mostly for backwards compatibility (``urlargs`` in it's
    current form was previously not available), but also differs from
    ``urlargs`` that a queried value is returned directly, rather than
    as a 1-tuple.


    Set a value
    >>> urlarg('http://example.org?x=1', 'x', 2)
    'http://example.org?x=2'

    Query a value
    >>> urlarg('http://example.org?x=1', 'x')
    '1'

    It's easy to confuse urlarg() and urlargs() like that, so try
    to prevent it:
    >>> urlarg('http://example.org?x=1', {'x': 2})
    Traceback (most recent call last):
    ValueError: name argument must be a string

    [bug] Removing an argument is not confused with querying one.
    >>> urlarg('http://example.org?x=1', 'x', False)
    'http://example.org'
    >>> urlarg('http://example.org?x=1', 'x', None)
    '1'
    """

    # see test - make it harder to confuse urlarg and urlargs
    if not isinstance(name, basestring):
        raise ValueError('name argument must be a string')

    if value is not None:
        return urlargs(url, **{name: value})
    else:
        return urlargs(url, name)[0]


def get_caller(up=1):
    """Get file name, line number, function name and source text of
    the caller's caller as 4-tuple: (file, line, func, text).

    The optional argument 'up' allows retrieval of a caller further
    back up into the call stack.

    Note, the source text may be None and function name may be '?'
    in the returned result.  In Python 2.3+ the file name may be an
    absolute path.

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
    """Append a path to the system path.

    Can take multiple arguments, in the same way os.path.join() does.

    Relative paths are considered to be relative to the calling module's
    filename (this can be changed by the "levels" parameter - the default
    is "1" - each level is one level on the stack, to find the module
    that will be used as a base for relative filenames).

    This is primarily useful if you want to include a module who's
    location in the filesystem you are aware of, say, two levels up.
    """
    levels = kwargs.get('levels', 1)
    dir = os.path.abspath(os.path.join(os.path.dirname(get_caller(up=levels)[0]), *path))
    if not dir in sys.path:
        sys.path.append(dir)


def equal_floats(f1, f2, digits=11):
    """Compares two float values, and returns a boolean indicating
    whether they are the same with respect to a certain
    treshold/resolution/precision.

    The digits parameter takes an integer indicating the number of
    digits/decimal places/resolution you wish to use for the
    comparison. The default is 11, which seems to be the max mysql
    precision on my installation, when I was required to write this
    function.

    Note that this function might return True of something like
    f1=1e-12 and f2=1e-112, i.e. it does not take into account the
    relative difference, so it may or may not be for you. A different
    solution would possible do:
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
    """Very useful for setting up standalone scripts that wish to make
    use of a Django environment.

    ``settings_path`` needs to point to the directory where you're
    project's ``settings.py`` is located, either as an absolute path,
    or as relative path in reference to the module calling this function.

    If ``settings_path`` is not specified or ``False``, a fake settings
    module will be setup. Note that while you'll then be able to work
    with certain Django modules that require this, you're environment is
    still somewhat limited - for example, we cannot put a project on the
    path in those cases, obviously.

    Note that this would probably better fit into ``djutils``. However,
    currently, that package *requires* a working django setup, so for
    now, we put it here.
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
    """Simply output a string to a file, overriding any existing
    content. Useful for debugging.
    """
    file = open(filename, 'w+')
    try:
        file.write(str)
    finally:
        file.close()


def print_r(obj, level=1, indent=' '*4):
    """Similar to PHP's print_r, although in it's current version it
    is simply useful for outputting dicts with a bit of formatting,
    indentation etc.
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


def raise_unsupported_args(kw):
    """Raises a ``TypeError`` if there are values in ``kw``, with a nice
    message listing all the keys.

    Use this if you have a function that takes a fixed number of allowed
    arguments through the ``**kwargs`` syntax, which is often useful if
    you also have ``*args``, but do not want to specify your keyword
    arguments first.

    Usage:
        def delete(*files, **kwargs)::
            recursive = kwargs.pop('recursive', True)
            raise_unsupported_args(kwargs)

    >>> raise_unsupported_args({})
    >>> raise_unsupported_args({'a': 1})
    Traceback (most recent call last):
    TypeError: function got unexpected keyword arguments: 'a'
    >>> raise_unsupported_args({'a': 1, 'b': True})
    Traceback (most recent call last):
    TypeError: function got unexpected keyword arguments: 'a', 'b'
    """
    if kw:
        raise TypeError("function got unexpected keyword arguments: '%s'" %
            "', '".join(kw.keys()))


def profileit(printlines=1):
    """Profile the decorated callable.

    From:
        http://www.biais.org/blog/index.php/2007/01/20/18-python-profiling-decorator
    """
    import hotshot, hotshot.stats
    def _my(func):
        def _func(*args, **kargs):
            prof = hotshot.Profile("profiling.data")
            res = prof.runcall(func, *args, **kargs)
            prof.close()
            stats = hotshot.stats.load("profiling.data")
            stats.strip_dirs()
            stats.sort_stats('time', 'calls')
            print ">>>---- Begin profiling print"
            stats.print_stats(printlines)
            print ">>>---- End profiling print"
            return res
        return _func
    return _my


if __name__ == '__main__':
    import doctest
    doctest.testmod()