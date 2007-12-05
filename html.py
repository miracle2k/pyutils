import re
from django.utils.encoding import force_unicode

# matches a character entity reference (decimal numeric, hexadecimal numeric, or named).
charrefpat = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?')
def decode(text):
    """
        Decode HTML entities in the given text.
        text should be a unicode string, as that is what we insert.

        This is from:
            http://zesty.ca/python/scrape.py
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

def smart_strip_tags(text):
    """
        Return the given HTML with all tags stripped. This is a version of the
        same function in django.utils.html, but attempts to insert spaces in
        place of certain tags like br, div, p and the likes.
    """
    result = re.sub(r'</?(div|br|p)[^>]*?>', ' ', force_unicode(text))
    return re.sub(r'<[^>]*?>', '', result)

def sanitize_whitespace(text):
    """
        * Replaces multiple space characters with a single one.
        * Removes spaces spaces in front of and at the end of a line.
    """
    def repl(match): # avoid "unmatched group" error
        g = match.groups()
        # basically "\1\2\3"
        return (g[0] or '') + (g[1] or '') + (g[2] or '')
    return sanitize_whitespace.pattern.sub(repl, force_unicode(text))
sanitize_whitespace.pattern = re.compile(r"""(?mxu)
    # spaces before a line - capture the linebreak in 1
    (^)[\ \t]+   |
    # spaces after a line - capture the linebreak in 2
    [\ \t]+($)   |
    # multiple spaces within a line - capture the replacement space in 3
    ([\ \t])[\ \t]+
""")