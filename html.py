import re
from django.utils.encoding import force_unicode

# matches a character entity reference (decimal numeric,
# hexadecimal numeric, or named).
charrefpat = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?')

def decode(text):
    """Decode HTML entities in the given text.

    ``text`` should be a unicode string, as that is what we insert.

    From:
        http://zesty.ca/python/scrape.py

    A similar attempt can be found here:
        http://groups.google.com/group/comp.lang.python/msg/ce3fc3330cbbac0a
    """
    from htmlentitydefs import name2codepoint
    if type(text) is unicode:
        uchr = unichr
    else:
        uchr = lambda value: value > 255 and unichr(value) or chr(value)

    def entitydecode(match, uchr=uchr):
        entity = match.group(1)
        if entity.startswith('#x'):
            return uchr(int(entity[2:], 16))
        elif entity.startswith('#'):
            return uchr(int(entity[1:]))
        elif entity in name2codepoint:
            return uchr(name2codepoint[entity])
        else:
            return match.group(0)
    return charrefpat.sub(entitydecode, text)


re_strip_tags = re.compile(
    r"<\/?(\w+)((\s+\w+(\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)+\s*|\s*)\/?>")

def smart_strip_tags(text):
    """Return the given HTML with all tags stripped.

    This is a version of the same function in ``django.utils.html``,
    but attempts to insert spaces in place of certain tags like
    br, div, p etc.

    It also uses an improved regular expression (it can handle '>'
    inside attributes) from:
    http://kev.coolcavemen.com/2007/03/ultimate-regular-expression-for-html-tag-parsing-with-php/

    # TODO: could this be more solid by using HTMLParser (see comment
    by Josiah Carlson: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440481)?

    Simple:
    >>> smart_strip_tags('abc<a>def<a />ghi<a></a>jkl')
    u'abcdefghijkl'

    Certain tags are replaced by whitespace:
    >>> smart_strip_tags('abc<div name="x">def<br/>ghi<p />jkl')
    u'abc def ghi jkl'

    Attributes can contain '>' characters:
    >>> smart_strip_tags('abc<img alt=">">def')
    u'abcdef'

    Tags can wrap across multiple lines (but attribute values can't
    for now, btw):
    >>> smart_strip_tags('abc<img \\nalt=">"\\n>def')
    u'abcdef'
    """

    def repl(m):
        if m.groups() and m.groups()[0] in ('br', 'div', 'p'):
            return ' '
        else:
            return ''
    return re_strip_tags.sub(repl, force_unicode(text))


def sanitize_whitespace(text):
    """Remove unnecessary whitespace from ``text``.

    Replaces multiple space characters with a single one, and more than
    two linebreaks between paragraphs.
    Also removes spaces in front of and at the end of a line.

    >>> sanitize_whitespace(u'    ')
    u''
    >>> sanitize_whitespace(u'in       between')
    u'in between'
    >>> sanitize_whitespace(u'    start and end of line     ')
    u'start and end of line'
    >>> sanitize_whitespace(u'    start and end    \\n   of multiple lines     ')
    u'start and end\\nof multiple lines'
    >>> sanitize_whitespace(u'various\\r\\n\\r\\n\\r\\nmultiple\\n\\n\\n\\nempty\\r\\r\\rlines')
    u'various\\r\\n\\r\\nmultiple\\n\\nempty\\r\\rlines'
    >>> sanitize_whitespace(u'    start     and between   and at end    ')
    u'start and between and at end'
    >>> sanitize_whitespace(u'a    \\n  \\n  \\n    \\n   b')
    u'a\\n\\nb'
    >>> sanitize_whitespace('    non    unicode   \\n\\n\\n\\n  string')
    u'non unicode\\n\\nstring'
    >>> sanitize_whitespace(u'\\xa0  with    \\xa0 non-breaking spaces   \\xa0 ')
    u'with non-breaking spaces'
    """
    def repl(match):  # to avoid "unmatched group" error - basically "\1\2"
        return (match.groups()[0] or u'') + (match.groups()[1] or u'')

    # First, prepare the input string by removing non-breaking spaces
    # (&nbsp) - \xa0 in unicode. Handling this in the regex is much
    # more complex.
    result = force_unicode(text)
    result = result.replace(u'\xa0', u' ')

    result = sanitize_whitespace.pattern1.sub(repl, result)
    return sanitize_whitespace.pattern2.sub(ur'\1', result)

sanitize_whitespace.pattern1 = re.compile(ur"""(?xu)
    # spaces before and after a line - capture the linebreak in 1
    [\ \t]*(^|\r\n|\r|\n|$)[\ \t]* |
    # multiple spaces within a line - capture the replacement space in 2
    ([\ \t])[\ \t]+
""")
sanitize_whitespace.pattern2 = re.compile(ur"""(?xu)
    # multiple linebreaks - allow max. 2 in sequence
    ((?:\r\n|\r|\n){2})(?:\r\n|\r|\n)+
""")

x = sanitize_whitespace(u'    ')

if __name__ == '__main__':
    import doctest
    doctest.testmod()