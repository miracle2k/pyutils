"""Port of the "Latitude/longitude spherical geodesy formulae & scripts"
(c) Chris Veness 2002-2009, originally in JavaScript, licensed under
LPGL:

    http://www.movable-type.co.uk/scripts/latlong.html

Not all functions are included (only those I needed personally so far),
and a cross-track function, as described on the page but not included
in code, was added by myself.

Some other links I stumbled over while researching this follow below -
I hope I won't need them again:

    http://stackoverflow.com/questions/1299567/how-to-calculate-distance-from-a-point-to-a-line-segment-on-a-sphere/
    http://stackoverflow.com/questions/1051723/distance-from-point-to-line-great-circle-functino-not-working-right-need-help
    http://williams.best.vwh.net/avform.htm
    http://mail.python.org/pipermail/python-list/2005-June/328382.html
    http://postgis.refractions.net/pipermail/postgis-users/2009-July/023903.html
    http://www.google.com/codesearch/p?hl=en&sa=N&cd=3&ct=rc#ArccXqZgcB0/source/Common/Source/Airspace.cpp (xcsoar@sourceforge)
    http://mathforum.org/library/drmath/view/51785.html
    http://www.physicsforums.com/showthread.php?t=178252
"""


from math import radians, degrees, sin, cos, asin, sqrt, atan2, pi


__all__ = ('EARTH_RADIUS',
           'distance_haversine', 'distance_cosine', 'bearing',
           'bearing_degrees', 'destination', 'cross_track',)


EARTH_RADIUS = R = 6371.0;   # kilometers  (make sure this is a float)


def distance_haversine(lat1, lon1, lat2, lon2):
    """Use Haversine formula to calculate distance (in km) between two
    points specified by latitude/longitude (in numeric degrees).

   from: Haversine formula - R. W. Sinnott, "Virtues of the Haversine",
         Sky and Telescope, vol 68, no 2, 1984
         http://www.census.gov/cgi-bin/geo/gisfaq?Q5.1
    """
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dlat / 2) * sin(dlat / 2) + cos(lat1) * \
        cos(lat2) * sin(dlon / 2) * sin(dlon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = R * c
    return d


def distance_cosine(lat1, lon1, lat2, lon2):
    """Use Law of Cosines to calculate distance (in km) between two
    points specified by latitude/longitude (in numeric degrees).
    """
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    dlon = radians(lon2 - lon1)
    return acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(dlon)) * R


def bearing(lat1, lon1, lat2, lon2):
    """Calculate the (initial) bearing between two points:

        http://williams.best.vwh.net/avform.htm#Crs

    Will return a value in radians, different from the original.
    """
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    dlon = radians(lon2 - lon1)

    y = sin(dlon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    return atan2(y, x)


def bearing_degrees(lat1, lon1, lat2, lon2):
    """See ``bearing()```.
    """
    radians = bearing(lat1, lon1, lat2, lon2)
    return (degrees(radians) + 360) % 360  # unsigned


def destination(lat, long, bearing, d):
    """Calculate destination point given start point, with initial bearing
    in degrees and distance in kilometers:

        http://williams.best.vwh.net/avform.htm#LL

    Returns a 2-tuple (lat, long), in degrees.
    """
    lat1 = radians(lat)
    lon1 = radians(int)
    bearing = radians(bearing)

    lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(bearing))
    lon2 = lon1 + atan2(sin(bearing) * sin(d/R) * cos(lat1),
                        cos(d/R) - sin(lat1) * sin(lat2))
    lon2 = (lon2 + pi) % (2 * pi) - pi   # normalize to -180...+180

    # if lat2 == NaN || lon2 == NaN: return None  # Hm.
    return degrees(lat2), degrees(lon2)


def cross_track(latA, lonA, latB, lonB, latP, lonP):
    """Returns the distance of a point P from a great-circle path AB,
    in kilometers.

    Sometimes called cross track error.

    >>> "%.8f" % cross_track(48.76165, 11.41947, 48.75857, 11.42501, 48.76176, 11.41595)
    '0.15697753'
    """
    d13 = distance_haversine(latA, lonA, latP, lonP)
    brng12 = bearing(latA, lonA, latB, lonB)
    brng13 = bearing(latA, lonA, latP, lonP)
    dXt = asin(sin(d13 / R) * sin(brng13 - brng12)) * R
    return dXt


if __name__ == '__main__':
    import doctest
    doctest.testmod()