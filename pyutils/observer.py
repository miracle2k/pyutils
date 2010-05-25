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


class event(object):
    def __init__(self, func):
        self.__doc__ = func.__doc__
        self._key = ' ' + func.__name__
    def __get__(self, obj, cls):
        try:
            return obj.__dict__[self._key]
        except KeyError, exc:
            be = obj.__dict__[self._key] = boundevent()
            return be


class boundevent(object):
    def __init__(self):
        self._fns = []
    def __iadd__(self, fn):
        self._fns.append(fn)
        return self
    def __isub__(self, fn):
        self._fns.remove(fn)
        return self
    def __call__(self, *args, **kwargs):
        for f in self._fns[:]:
            f(*args, **kwargs)