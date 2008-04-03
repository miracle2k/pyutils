"""
Utilities for creating command line based scripts.
"""
import sys, types

def program(mainfunc):
    """
    Executes 'mainfunc' while passing sys.argv. Passes any
    return value to sys.exit, or 0 for success.

    Usage:
        if __name__ == '__main__':
            program(main)
    """
    sys.exit(mainfunc(sys.argv) or 0)

class Options(dict):
    """
    Some of the functionality in this module depends on "options", e.g. usually
    those are going to defined by script command line arguments. However, we do
    not deal with command line business, or argument parsing - do that any way
    you want. Just be sure to update these module-global options appropriately.
    
    >>> options = Options()
    >>> options.doesnotexist == None
    True
    >>> options['doesnotexist'] == None
    True
    >>> options.value = 1
    >>> print options.value
    1
    >>> options['x'] = 'abc'
    >>> print options['x']
    abc
    >>> options.update({'foo': 'bar'})
    >>> print options.foo
    bar
    >>> class MyOptions(Options): predef = 99
    >>>
    >>> myoptions = MyOptions()
    >>> print myoptions.predef
    99
    >>> print myoptions['predef']
    99
    """
    class __metaclass__(type):
        def __new__(cls, name, bases, dict):
            # convert attributes defined in the class at into dict items
            items = {}
            for name, value in dict.items():
                if not (isinstance(value, types.FunctionType) or name.startswith('__')):
                    items[name] = value
                    del dict[name]
            dict['__items__'] = items
            self = type.__new__(cls, name, bases, dict)
            return self
    def __new__(cls, *args, **kwargs):
        self = dict.__new__(cls, *args, **kwargs)
        self.update(cls.__items__)
        return self
            
    def __getitem__(self, key):
        try: return super(Options, self).__getitem__(key)
        except KeyError: return None # resolve non-existing values to ``None``
    def __setitem__(self, key, value):
        return super(Options, self).__setitem__(key, value)
    # allow access via attributes
    __getattr__ = __getitem__
    __setattr__ = __setitem__
options = Options()

"""
Common output functions - each represents a different "log level", and whether
it ends up on the screen depends on arguments like verbose, quiet, etc.

Most return a boolean indicating whether the message was printed.
"error" however returns an exit code.

We also support a header mechanism, that makes it possible to make any verbose,
message, warning or error level message depend on another message. The system
will remember whether such a header was printed, and if not, will do so once
a depending message has to be printed.
Consecutive dependencies are currently not possible.
Example:
    message('item #%s'%id, header='item') # True is possible if only one header required
    for thing in item.things:
        if thing.needs_change:
            change()
            warning('\tWas changed.', depends='item')
            warning('\tDon't forget to rsync.', depends='item')

    Here, if the message() string is not printed immediately (because
    options.quit is set, for example), it will be printed together with
    warning(), as it presumes the user to have seen the message before.
    The second warning() will not print the header again.
"""
_message_headers = {}
def support_headers(func):
    def newfunc(str, *args, **kwargs):
        depends = kwargs.pop('depends', None)
        header = kwargs.pop('header', None)
        # if this message depends on another, print that first
        if depends and depends in _message_headers:
            print _message_headers[depends]
            del _message_headers[depends]  # only print once
        # print current message
        if not func(str, *args, **kwargs):
            # if not printed and is header, then remember for later
            if header:
                _message_headers[header] = str
    return newfunc
def verbose(str):
    if options.verbose: _print(str)
    return options.verbose
verbose = support_headers(verbose)
def message(str):
    if not options.quiet: _print(str)
    return not options.quiet
message = support_headers(message)
def warning(str):
    _print(str)
    return True
warning = support_headers(warning)
def error(str):
    _print(str)
    return 1
error = support_headers(error)
def _print(s):
    if isinstance(s, str): s = unicode(s, 'ascii', 'replace')
    elif isinstance(s, basestring): pass
    else: s = u"%s"%s
    encoding = sys.stdout.encoding or "ascii"
    print s.encode(encoding, "replace")

def help(docstr, scriptname=None):
    """
    Utility function to print the help text of a script. The simpliest
    way to use this is to just ...

    strip()s the docstr, so you can easily capture the first comment
    in your script, and use it has the help text.

    Replaces %(scriptname)s in 'docstr' with what you pass in the
    'scriptname' parameter. This can either by a sequence (like
    sys.argv) or a string (like sys.argv[0]). In any case, only the
    basename() is used.
    If you don't want this replacement, explicitly pass "False", as
    in the future this might automatically try to find a missing
    scriptname via introspection.

    Returns 1, so you can pass it on as an exit code.
    """
    import os
    docstr = docstr.strip()
    if scriptname != False:
        if isinstance(scriptname, (tuple, dict, list)): scriptname = scriptname[0]
        docstr %= {'scriptname': os.path.basename(scriptname)}
    print docstr
    return 1

if __name__ == "__main__":
    import doctest
    doctest.testmod()