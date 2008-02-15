"""
Compatibility routines for older python versions.
"""

def any(iterable):
    """
    Python 2-5 built-in ``any``.
    """
    for element in iterable:
        if element: return True
    return False

def all(iterable):
    """
    Python 2-5 built-in ``all``.
    """
    for element in iterable:
        if not element: return False
    return True