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
        place of certain tags like br, div, p etc.
    """
    result = re.sub(r'</?(div|br|p)[^>]*?>', ' ', force_unicode(text))
    return re.sub(r'<[^>]*?>', '', result)

def sanitize_whitespace(text):
    """
        * Replaces multiple space characters with a single one.
        * Removes spaces spaces in front of and at the end of a line.
    """
    def repl(match): # avoid "unmatched group" error - basically "\1\2"
        return (match.groups()[0] or '') + (match.groups()[1] or '')
    # we need to do this in two steps - first remove whitspace from line
    # beginnings and in between text, then remove whitespace from the end
    # of lines. if we combine the two regexes, consider what would happen
    # in this case:
    #    "a  \n b"
    # first, the whitespace after 'a' would be removed by the "line end" regex.
    # then, the regex would continue at the space character, which would not
    # be removed (although it should), because the character that indicates the
    # line break has already been removed by the engine. Now, there is probably
    # a different approach we could take (match both in one regex), but what we
    # have works good enough for now...
    result = sanitize_whitespace.pattern1.sub(repl, force_unicode(text))
    return sanitize_whitespace.pattern2.sub(r'\1', result)
# pattern 1 - before and within a line
sanitize_whitespace.pattern1 = re.compile(r"""(?xu)
    # spaces before a line - capture the linebreak in 2
    (^|\r\n|\r|\n)[\ \t]+ |
    # multiple spaces within a line - capture the replacement space in 3
    ([\ \t])[\ \t]+
""")
# pattern 2 - after a line
sanitize_whitespace.pattern2 = re.compile(r"""(?xu)
    # spaces after a line - capture the linebreak in 1
    [\ \t]+(\r\n|\r|\n|$)
""")