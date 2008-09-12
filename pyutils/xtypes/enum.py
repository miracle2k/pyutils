"""
Python emumeration implementations.
"""

class EnumMetaclass(type):
    """
    This implementation requires (or allows) the user to assign a value to each
    enum identifer manually. Example:

    >>> class Color(ValueEnum):
    ...     red = 1
    ...     green = 2
    ...     blue = 3

    Those enumerations cannot be instantiated; however they can be subclassed:

    >>> class ExtendedColor(Color):
    ...     white = 0
    ...     orange = 4
    ...     yellow = 5
    ...     purple = 6
    ...     black = 7

    Examples:

    >>> print Color.red
    1
    >>> print Color.red == Color.red
    True
    >>> print Color.red == Color.blue
    False
    >>> print Color.red == 1
    True
    >>> print Color.red == 2
    False
    >>> print Color.red == ExtendedColor.red
    True
    >>> print int(Color.red)
    1
    >>> l = [int(x) for x in Color]
    >>> l.sort()
    >>> l
    [1, 2, 3]
    >>> Color.red.belongs(Color)
    True
    >>> Color.has(Color.red)
    True
    >>> Color.red.name()
    'Color.red'
    >>> Color.red.name(True)
    'red'
    >>> print Color.by_name('red')
    1
    >>> print Color.by_name('Color.red')
    1
    >>> print Color.by_name('grey')
    None
    >>> print Color.by_name('grey', Color.red)
    1


    Based on code from:
        http://svn.python.org/projects/python/trunk/Demo/newmetaclasses/Enum.py
    """
    def __init__(cls, name, bases, dict):
        super(EnumMetaclass, cls).__init__(name, bases, dict)
        cls._members = []
        for attr in dict.keys():
            if not (attr.startswith('__') and attr.endswith('__')):
                enumval = EnumInstance(name, attr, dict[attr])
                setattr(cls, attr, enumval)
                cls._members.append(attr)

    def __getattr__(cls, name):
        if name == "__members__":
            return cls._members
        raise AttributeError, name

    def __setattr__(cls, name, value):
        # do not allow changing of enum values at runtime
        if hasattr(cls, name) and isinstance(getattr(cls, name), EnumInstance):
            raise Exception('Enum values are immutable.')
        else:
            super(EnumMetaclass, cls).__setattr__(name, value)

    def __getitem__(cls, key):
        for m in cls._members:
            if getattr(cls, m).value() == key:
                return getattr(cls, m)
        return None

    def __iter__(cls):
        for item in cls.__members__:
            yield getattr(cls, item)

    def has(self, other):
        return other in self.__dict__.values()

    def by_name(self, name, default=None):
        for option in self:
            if name in [option.name(False), option.name(True)]:
                return option
        return default

    def __repr__(cls):
        s1 = s2 = ""
        enumbases = [base.__name__ for base in cls.__bases__
                     if isinstance(base, EnumMetaclass) and not base is ValueEnum]
        if enumbases:
            s1 = "(%s)" % ", ".join(enumbases)
        enumvalues = ["%s: %d" % (val, getattr(cls, val))
                      for val in cls._members]
        if enumvalues:
            s2 = ": {%s}" % ", ".join(enumvalues)
        return "%s%s%s" % (cls.__name__, s1, s2)

class FullEnumMetaclass(EnumMetaclass):
    """
    Extended version of the metaclass that adds the base classes' members as
    well. This is the default.
    """
    def __init__(cls, name, bases, dict):
        super(FullEnumMetaclass, cls).__init__(name, bases, dict)
        for obj in cls.__mro__:
            if isinstance(obj, EnumMetaclass):
                for attr in obj._members:
                    # XXX inefficient
                    if not attr in cls._members:
                        cls._members.append(attr)

class EnumInstance(int):
    """
    Represents a single enumeration value.
    """
    def __new__(cls, classname, enumname, value):
        return int.__new__(cls, value)

    def __init__(self, classname, enumname, value):
        self.__classname = classname
        self.__enumname = enumname

    def __repr__(self):
        return "EnumValue(%s, %s, %d)" % (self.__classname, self.__enumname, self)

    def __str__(self):
        """
        Use the integer value itself, or whatever is provided by the base
        class. Orginally, this would return something like ``Colors.red``, but
        I found that this makes usage more complex and I end up using a lot of
        typecasts ala ``int(Colors.red)``. This string can now be accessed via
        ``name()``.
        """
        return str(self.value())

    def __deepcopy__(self, memo):
        return self
    def __copy__(self):
        return self

    def name(self, short=False):
        if short:
            return "%s" % (self.__enumname)
        else:
            return "%s.%s" % (self.__classname, self.__enumname)

    def value(self):
        return int(self)

    def belongs(self, other):
        return self in other.__dict__.values()

class ValueEnum:
    """
    The actual enum class that you should descend from.
    """
    __metaclass__ = FullEnumMetaclass


################################################################################
################################################################################
################################################################################

def HashEnum(*names):
    """
    This implementation does not allow the assignment of values for each identifer
    of the enumeration. Instead, you just specify the required values:

        Days = Enum('Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su')

    Examples:

        print Days
        print Days.Mo
        print Days.Fr
        print Days.Mo < Days.Fr
        print list(Days)
        for each in Days:
            print 'Day:', each

    Based on code from:
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/413486
    """
    ##assert names, "Empty enums are not supported" # <- Don't like empty enums? Uncomment!

    class EnumClass(object):
        __slots__ = names
        def __iter__(self):
            return iter(constants)
        def __len__(self):
            return len(constants)
        def __getitem__(self, i):
            return constants[i]
        def __repr__(self):
            return 'Enum' + str(names)
        def __str__(self):
            return 'enum ' + str(constants)

    class EnumValue(object):
        __slots__ = ('__value')
        def __init__(self, value): self.__value = value
        Value = property(lambda self: self.__value)
        EnumType = property(lambda self: EnumType)
        def __hash__(self):
            return hash(self.__value)
        def __cmp__(self, other):
            # C fans might want to remove the following assertion
            # to make all enums comparable by ordinal value {;))
            assert self.EnumType is other.EnumType, "Only values from the same enum are comparable"
            return cmp(self.__value, other.__value)
        def __invert__(self):
            return constants[maximum - self.__value]
        def __nonzero__(self):
            return bool(self.__value)
        def __repr__(self):
            return str(names[self.__value])

    maximum = len(names) - 1
    constants = [None] * len(names)
    for i, each in enumerate(names):
        val = EnumValue(i)
        setattr(EnumClass, each, val)
        constants[i] = val
    constants = tuple(constants)
    EnumType = EnumClass()
    return EnumType


if __name__ == '__main__':
    import doctest
    doctest.testmod()