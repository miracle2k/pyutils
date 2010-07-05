"""From: http://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips/1926336#1926336

Usage:

    # producer
    class MyJob(object):
        @event
        def progress(pct):
            '''Called when progress is made. pct is the percent complete.'''

        def run(self):
            n = 10
            for i in range(n+1):
                self.progress(100.0 * i / n)

    # consumer
    import sys, myjobs
    job = myjobs.MyJob()
    job.progress += lambda pct: sys.stdout.write("%.1f%% done\n" % pct)
    job.run()
"""


__all__ = ('event',)


def event(func=None, *a, **kw):
    """Portal function to expose our event facility. Needs supported
    multiple different ways of being called:

      - obj = event()
      - @event
      - @event(sender=True)


    """
    if not func and not a and not kw:
        # Not used as a decorator
        return boundevent()
    else:
        if func:
            assert not a and not kw
            # Used as a decorator without any options
            return event_decorator(func)
        else:
            # Used as a decorator with options
            def temp_decorator(func):
                return event_decorator(func, *a, **kw)
            return temp_decorator


class event_decorator(object):
    """A non-data descriptor that will return a ``boundevent`` if the
    attribute it represents is accessed.

    If ``sender`` is given, then the ``boundevent`` will be setup so
    that all event listeners will receive the object itself as the
    first argument.
    """

    def __init__(self, func, sender=False):
        self.__doc__ = func.__doc__
        self._key = ' ' + func.__name__
        self.with_sender = sender

    def __get__(self, obj, cls):
        try:
            return obj.__dict__[self._key]
        except KeyError, exc:
            be = obj.__dict__[self._key] = boundevent(
                obj if self.with_sender else None)
            return be


class boundevent(object):
    """Implements the actual event.

    Allows adding event listeners, and invoking the event.

    If ``sender_obj`` is set, then it will be given as the first argument
    to each event listener.
    """

    def __init__(self, sender_obj=None):
        self._fns = []
        self.sender_obj = sender_obj

    def __iadd__(self, fn):
        self._fns.append(fn)
        return self

    def __isub__(self, fn):
        self._fns.remove(fn)
        return self

    def __call__(self, *args, **kwargs):
        for f in self._fns[:]:
            if self.sender_obj:
                f(self.sender_obj, *args, **kwargs)
            else:
                f(*args, **kwargs)



__test__ = {'': """

>>> def printer(id):
...     def func(*a):
...         print "%s: %s" % (id, ", ".join(map(str, a)))
...     return func

# Use a a standalone object
>>> obj = event()
>>> obj += printer('a')
>>> obj += printer('b')
>>> obj(1, 2, 3)
a: 1, 2, 3
b: 1, 2, 3

# Use as a method decorator
>>> class Foo(object):
...    @event
...    def event_no_sender(self):
...        pass
...    @event(sender=True)
...    def event_with_sender(self):
...        pass
>>> foo = Foo()
>>> foo.event_no_sender += printer('a')
>>> foo.event_no_sender += printer('b')
>>> foo.event_with_sender += printer('a')
>>> foo.event_with_sender += printer('b')
>>> foo.event_no_sender(1, 2, 3)
a: 1, 2, 3
b: 1, 2, 3
>>> foo.event_with_sender(1, 2, 3)
a: <__main__.Foo object at ...>, 1, 2, 3
b: <__main__.Foo object at ...>, 1, 2, 3
"""}
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)