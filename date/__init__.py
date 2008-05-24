# coding: iso-8859-1
"""
parserinfo classes that need to be used with the python-dateutil
library from:
    http://labix.org/python-dateutil

Pass them to the dateutil.parser.parse() function to modify the parsing 
behaviour.

Note: Versions older then 1.3 are broken when it comes to handling 
custom parser infos.
"""

from dateutil import parser

__all__ = ['GermanParserInfo', 'MultiParserInfo']

class GermanParserInfo(parser.parserinfo):
    """
    Enable german dates.
    """
    WEEKDAYS = [("Mo", "Montag"),
                ("Di", "Dienstag"),
                ("Mi", "Mittwoch"),
                ("Do", "Donnerstag"),
                ("Fr", "Freitag"),
                ("Sa", "Samstag"),
                ("So", "Sonntag")]
    MONTHS   = [("Jan", "Januar"),
                ("Feb", "Februar"),
                ("Mär", "Mrz", "März"),
                ("Apr", "April"),
                ("Mai", "Mai"),
                ("Jun", "Juni"),
                ("Jul", "Juli"),
                ("Aug", "August"),
                ("Sep", "September"),
                ("Okt", "Oktober"),
                ("Nov", "November"),
                ("Dez", "Dezember")]
    HMS = [("h", "Stunde", "Stunden"),
           ("m", "Minute", "Minuten"),
           ("s", "Sekunde", "Sekunden")]
    
    def __init__(self, dayfirst=True, yearfirst=False):
        """
        set dayfirst by default for German.
        """
        super(GermanParserInfo, self).__init__(dayfirst=dayfirst, yearfirst=yearfirst)

    def weekday(self, name):
        """
        Need to reimplement this, as German weekdays in shortform are only
        two characters long, and the superclass implementation has a hardcoded
        requirement of at least 3.
        """
        if len(name) >= 2:
            try:
                return self._weekdays[name.lower()]
            except KeyError:
                pass
        return None

class MultiParserInfo(parser.parserinfo):
    """
    Allows to combine multiple parserinfo classes, if you need/want to support
    different languages for example. Obviously, it needs to be passed as an
    instance, so you can put the parserinfo's to use in the constructor.
    Otherwise, only the default parserinfo will be used.

    Usage:
      MultiParserInfo(parsers=[FrenchParser, GermanParser()], param1, param2)

    As you can see, you can put both instances and classes in "parsers". If you
    pass a class, an instance will be created using the other parameters you
    gave to MultiParserInfo(). Some functionality, that can not reasonably be
    expanded over multiple parsers will just use the very first one, so for those
    cases order will have a limited effect.
    """
    def __init__(self, parsers=[], *args, **kwargs):
        import inspect
        self.parsers = []
        for p in parsers:
            if inspect.isclass(p): p = p(*args, **kwargs)
            self.parsers.append(p)
        super(MultiParserInfo, self).__init__(*args, **kwargs)

    # redirect dayfirst and yearfirst properties to the first parser
    def get_dayfirst(self):
        if len(self.parsers) > 0:
            return self.parsers[0].dayfirst
        return self._dayfirst
    def set_dayfirst(self, value):
        self._dayfirst = value
    dayfirst = property(get_dayfirst, set_dayfirst)
    def get_yearfirst(self):
        if len(self.parsers) > 0:
            return self.parsers[0].yearfirst
        return self._yearfirst
    def set_yearfirst(self, value):
        self._yearfirst = value
    yearfirst = property(get_yearfirst, set_yearfirst)

    def _try_all(self, method, args):
        """
        Ccall a method on all the parsers and use the first return value that
        evaluates to ``True``. Otherwise, fall back to the implementation of
        our superclass (which is the default ``parserinfo``).
        """
        for p in self.parsers:
            result = getattr(p, method)(*args)
            # do allow result==0, as this is a valid return value from tzoffset()
            if result or result == 0:
                return result
        return getattr(super(MultiParserInfo, self), method)(*args)

    def jump(self, name):
        return self._try_all("jump", [name])

    def weekday(self, name):
        return self._try_all("weekday", [name])

    def month(self, name):
        return self._try_all("month", [name])

    def hms(self, name):
        return self._try_all("hms", [name])

    def ampm(self, name):
        return self._try_all("ampm", [name])

    def pertain(self, name):
        return self._try_all("pertain", [name])

    def utczone(self, name):
        return self._try_all("utczone", [name])

    def tzoffset(self, name):
        return self._try_all("tzoffset", [name])

    def convertyear(self, year):
        # as this should always return something, it will usually
        # just use the first parser it encounters.
        return self._try_all("convertyear", [year])

    def validate(self, res):
        # in theory, we call all valdiate() methods, until we find one that
        # returns True. However, as that is usually the case (the default one
        # does, at least), most often only the first one is actually used.
        return self._try_all("validate", [res])

def parse_de_date(str):
    """
    Simple shortcut to use the dateparser with our German parserinfo class.
    Note that it tries to convert str to iso-8859-1, as this is the encoding
    the dateutil parser uses (as does this file), and it's required to match
    identifiers with special characters, like "März".
    """
    return parser.parse(str.encode('iso-8859-1', 'replace'),
        parserinfo=MultiParserInfo(parsers=[GermanParserInfo(dayfirst=True)]))