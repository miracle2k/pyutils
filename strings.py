import re

__all__ = (
    'hextable',
    'strtr',
    'ex2u',
    'safmtb',
    'safmt',
)

_hextable_filter =\
    ''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def hextable(src, length=8):
    """
    Return the incoming byte stream in a table hex format known from hex
    viewers/editors. ``length``determines the number of bytes per line.

    From:
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/142812
    """
    N=0; result=''
    while src:
       s,src = src[:length],src[length:]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       s = s.translate(FILTER)
       result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
       N+=length
    return result

def strtr(dict, text):
    """
    Replace in 'text' all occurences of any key in the given dictionary by
    its corresponding value. Returns the new string.

    From:
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81330
    """
    # Create a regular expression  from the dictionary keys
    regex = re.compile(u"(%s)" % "|".join(map(re.escape, dict.keys())))
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

def ex2u(exception):
    """
    Python exceptions (min. up to 2.5) have trouble with Unicode messages, see:
        http://bugs.python.org/issue2517

    This can make exception handling very tedious, if you cannot know what to
    except: An exception object may contain a bytestring message, a unicode
    message, or possibly no message at all (when passed multiple arguments).
    Special exception classes may also choose to implement custom __str__ or
    __unicode__ methods.

    In fact, there doesn't appear to be a single way to access a unicode
    message inside an exception by only converting the exception itself:
    >> e = Exception(u'\xe4')
    >> e.__str__()
    <type 'exceptions.UnicodeEncodeError'> 'ascii' codec can't encode ...
    >> e.__unicode__()
    <type 'exceptions.AttributeError'> ...


    This function attempts to help by trying a couple different ways to convert
    the exception passed in to a unicode string - but is careful not to be too
    liberal. You will still run into errors if you are using non-ascii
    bytestrings, for example.

    >>> ex2u(Exception('abc'))
    u'abc'
    >>> ex2u(Exception(u'abc'))
    u'abc'
    >>> ex2u(Exception(u'\xe4'))
    u'\\xe4'
    """
    try:
        return unicode(exception)
    except UnicodeEncodeError, e:
        if hasattr(exception, 'message'):
            return unicode(exception.message)
        # we had our shot
        raise e


"""
The following is an advanced string format implementation
From:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/534139
"""

# Match any % formatting stanza
# Any character is allowed in names, unicode names work in python 2.2+
# The name can be an empty string
safmt_pat = re.compile(r'''
    %                     # Start with percent,
    (?:\( ([^()]*) \))?   # optional name in parens (do not capture parens),
    [-+ #0]*              # zero or more flags
    (?:\*|[0-9]*)         # optional minimum field width
    (?:\.(?:\*|[0-9]*))?  # optional dot and length modifier
    [EGXcdefgiorsux%]     # type code (or [formatted] percent character)
    ''', re.VERBOSE)

def safmtb(template, args=(), kw=None, savepc=0, verb=0):
    """
    Safe and augmented "%" string interpolation:
    - preserve % stanzas in case of missing argument or key
    - allow mixed positional and named arguments
    Note: TypeError exceptions can still happen, e.g. safmt("%d", "abc")
    Function arguments:
      template: a string containing "%" format specifiers
      args    : sequence arguments for format string
      kw      : mapping arguments for format string
      savepc  : optionally preserve "escaped percent" stanzas
                (parameterised positional stanzas always eat args)
      verb    : verbose execution, prints debug output to stdout
    """
    if verb:
        print "safmt(%r)" % (template,)

    if kw is None:
        kw = {}

    ret = []
    last = i = 0
    d = {}
    di = 0
    pat = safmt_pat
    while 1:
        mo = pat.search(template, i)

        if not mo:
            # End of string
            ret.append(template[last:])
            break

        i = mo.end(0)
        if verb: print mo.start(), mo.group(0, 1),

        stanza, name = mo.group(0, 1)
        if name is not None:
            # str[-1]=='x' is faster than str.endswith('x'),
            # and stanza is always non-empty here so slice will never fail
            if stanza[-1] == "%":
                if savepc:
                    if verb: print 'saving stanza'
                    continue
                # Workaround weird behaviour in python2.1-2.5: a named
                # argument that is just a percent escape still raises
                # KeyError, even though a positional escaped percent eats
                # no args and is happy with an empty sequence.
                # Workaround: provide a dummy key which never gets used.
                dat = stanza % {name: None}
            else:
                try:
                    dat = stanza % kw
                except KeyError:
                    if verb: print 'ignore missing key'
                    continue
            if verb: print "fmt %r" % dat
        else:
            # %<blah>% does not use up arguments, but "%*.*%" does
            numargs = stanza[-1] != "%"
            if verb: print "args=%s" % numargs,
            # Allow for "*" parameterisation (uses up to 2)
            numargs += mo.group(0).count("*")
            if verb: print "args=%s" % numargs,

            p = args[di: di + numargs]
            di += numargs
            if verb: print "p=%s" % (p,),
            if len(p) != numargs:
                if verb: print "not enough pos args"
                continue
            if savepc and stanza[-1] == "%":
                if verb: print 'saving stanza'
                continue
            dat = stanza % p
            if verb: print "fmt %r" % dat

        ret.append(template[last:mo.start()])
        ret.append(dat)
        last = i

    return ''.join(ret)
# Wrapper to allow e.g. safmt("%blah", 10, 20, spam='eggs')
# First argument must be the template
def safmt(*args, **kw):
    return safmtb(args[0], args[1:], kw)

if __name__ == '__main__':
    import doctest
    doctest.testmod()