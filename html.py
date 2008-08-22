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
    """Replaces multiple space characters with a single one.

    Also removes spaces spaces in front of and at the end of a line.
    """
    def repl(match): # avoid "unmatched group" error - basically "\1\2"
        return (match.groups()[0] or '') + (match.groups()[1] or '')
    return sanitize_whitespace.pattern.sub(repl, force_unicode(text))
sanitize_whitespace.pattern = re.compile(r"""(?xu)
    # spaces before and after a line - capture the linebreak in 1
    [\ \t]*(^|\r\n|\r|\n|$)[\ \t]* |
    # multiple spaces within a line - capture the replacement space in 2
    ([\ \t])[\ \t]+
""")


if __name__ == '__main__':
    import doctest
    doctest.testmod()