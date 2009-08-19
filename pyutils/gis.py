"""
Uses Shapely:
    http://pypi.python.org/pypi/Shapely/
"""

from shapely.geometry import *


def closest_point_on_segment(p, a, b, extend=False):
    """The point between C{Point}s ``a`` and ``b`` closest to ``p``.

    If ``extend`` is set, the returned point may be on the extension
    between of ab.

    Ported from PostGIS:
        http://trac.osgeo.org/postgis/browser/trunk/lwgeom/ptarray.c?rev=2277#L542

    Based on comp.graphics.algorithms FAQ:
        http://www.faqs.org/faqs/graphics/algorithms-faq/

        (1)           AC dot AB
                  r = ----------
                       ||AB||^2
             r has the following meaning:
             r=0 P = A
             r=1 P = B
             r<0 P is on the backward extension of AB
             r>1 P is on the forward extension of AB
             0<r<1 P is interior to AB

    See also:
        http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
    """
    if a == b:
        return a

    r = ( (p.x-a.x) * (b.x-a.x) + (p.y-a.y) * (b.y-a.y) ) /     \
             ( (b.x-a.x)*(b.x-a.x) + (b.y-a.y)*(b.y-a.y) )

    if not extend:
        if r<0: return a
        elif r>1: return b

    return Point(a.x + ((b.x - a.x) * r),
                 a.y + ((b.y - a.y) * r))



def line_locate_point(line, point):
    """Return point on C{LineString} ``line`` closest to the given
    C{Point}.

    Ported from PostGIS:
        http://trac.osgeo.org/postgis/browser/trunk/lwgeom/ptarray.c?rev=2277#L584

    Different from the PostGIS version, this returns an actual point
    object, rather than a scaled location of the point on the line.

    >>> l = LineString(((0,0), (0,10), (10,10),))
    >>> str(line_locate_point(l, Point(5,5)))
    'POINT (0.0000000000000000 5.0000000000000000)'
    >>> str(line_locate_point(l, Point(5,6)))
    'POINT (5.0000000000000000 10.0000000000000000)'
    >>> str(line_locate_point(l, Point(0,0)))
    'POINT (0.0000000000000000 0.0000000000000000)'
    >>> str(line_locate_point(l, Point(0,10)))
    'POINT (0.0000000000000000 10.0000000000000000)'
    """

    start = end = min_dist = seg = None

    it = iter(line.coords)
    start = it.next()
    while True:
        try:
            end = it.next()
        except StopIteration:
            break;

        dist = LineString((start, end,)).distance(point)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            seg = (start, end,)

        start = end

    return closest_point_on_segment(point, *[Point(c) for c in seg])


if __name__ == '__main__':
    import doctest
    doctest.testmod()