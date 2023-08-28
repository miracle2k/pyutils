import re
from django.utils.encoding import force_unicode


__all__ = ('decode', 'smart_strip_tags', 'sanitize_whitespace',)


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
    from html.entities import name2codepoint
    if type(text) is str:
        uchr = chr
    else:
        uchr = lambda value: value > 255 and chr(value) or chr(value)

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
    r"""(?:
            # Handle comments separately, to allow nested tags
            <!--.*?-->
         |
            # A tag
            <\s*\/?\s*
                # The tag name, captured so we can act upon it
                (\w[^ />]*)?
                # Basically arbitrary text until tag end (we don't
                # care about  attributes), but we want to allow
                # '>' inside attributes.
                (?:
                    ['\"].*?['\"]
                 |
                    [^'\">]
                )*
            \/?>
        )""", re.DOTALL | re.VERBOSE)

def smart_strip_tags(text):
    """Return the given HTML with all tags stripped.

    This is a version of the same function in ``django.utils.html``,
    but attempts to insert spaces in place of certain tags like
    br, div, p etc.

    It also uses an improved regular expression (it can handle '>'
    inside attributes).

    # TODO: could this be more solid by using HTMLParser (see comment
    by Josiah Carlson: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440481)?

    Simple:
    >>> smart_strip_tags('abc<a>def<a />ghi<a></a>jkl')
    u'abcdefghijkl'

    Certain tags are replaced by whitespace:
    >>> smart_strip_tags('abc<div name="x">def<br />ghi<p />jkl')
    u'abc def ghi jkl'

    Bug: Tag name is read correcly even in certain border cases,
    like when the closing slash follows the tag name right away:
    >>> smart_strip_tags('a<br/ >b< br/>c</ br/>d< /br>e')
    u'a b c d e'

    Attributes can contain '>' characters:
    >>> smart_strip_tags('abc<img alt=">">def')
    u'abcdef'
    >>> smart_strip_tags('abc<img ">">def')
    u'abcdef'

    Attributes can be standalone:
    >>> smart_strip_tags('abc<input checked foo bar>def')
    u'abcdef'

    Attributes can be unquoted:
    >>> smart_strip_tags('abc<a b=c>def')
    u'abcdef'

    Tag contents, including attribute values, may span multiple lines:
    >>> smart_strip_tags('abc<img \\nalt=">"\\n>def')
    u'abcdef'
    >>> smart_strip_tags('abc<img alt="1\\n2">def')
    u'abcdef'
    >>> smart_strip_tags('abc<img alt=1\\n2>def')
    u'abcdef'

    Both tag and attribute values may contain non-alphabetic characters,
    like a colon (used as a namespace prefix, in XML or MSWord exports).
    >>> smart_strip_tags('abc<m:lMargin m:val="0" />def')
    u'abcdef'

    Comments are stripped as well, even if they contain tags, and even
    if they span multiple lines.
    >>> smart_strip_tags('abc<!-- hello \\n world -->def<!-- <a> \\n -->ghi')
    u'abcdefghi'

    It works even if a tag or it's attributes are not strictly valid.
    >>> smart_strip_tags('abc<a withoutvalue=>def')
    u'abcdef'
    >>> smart_strip_tags('abc<a "withoutname">def')
    u'abcdef'
    >>> smart_strip_tags('abc<a =>def')
    u'abcdef'
    >>> smart_strip_tags('abc<a b=\\'c">def')
    u'abcdef'
    >>> smart_strip_tags('abc<  a>def<  /a>ghi</  a>jkl< / a>mno')
    u'abcdefghijklmno'
    >>> smart_strip_tags('abc<"foo">def<"">ghi<>jkl')
    u'abcdefghijkl'

    # TODO: Can we somehow assert that in a case like '''<"df">''',
    the "df" is not returned as the tag name?
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
        return (match.groups()[0] or '') + (match.groups()[1] or '')

    # First, prepare the input string by removing non-breaking spaces
    # (&nbsp) - \xa0 in unicode. Handling this in the regex is much
    # more complex.
    result = force_unicode(text)
    result = result.replace('\xa0', ' ')

    result = sanitize_whitespace.pattern1.sub(repl, result)
    return sanitize_whitespace.pattern2.sub(r'\1', result)

sanitize_whitespace.pattern1 = re.compile(r"""(?xu)
    # spaces before and after a line - capture the linebreak in 1
    [\ \t]*(^|\r\n|\r|\n|$)[\ \t]* |
    # multiple spaces within a line - capture the replacement space in 2
    ([\ \t])[\ \t]+
""")
sanitize_whitespace.pattern2 = re.compile(r"""(?xu)
    # multiple linebreaks - allow max. 2 in sequence
    ((?:\r\n|\r|\n){2})(?:\r\n|\r|\n)+
""")


if __name__ == '__main__':
    import doctest
    doctest.testmod()