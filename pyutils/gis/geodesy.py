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


import math


__all__ = ('EARTH_RADIUS',
           'distance_haversine', 'bearing', 'bearing_degrees', 'cross_track',)


EARTH_RADIUS = R = 6371;   # kilometers


def distance_haversine(lat1, lon1, lat2, lon2):
    """Use Haversine formula to calculate distance (in km) between two
    points specified by latitude/longitude (in numeric degrees).

   from: Haversine formula - R. W. Sinnott, "Virtues of the Haversine",
         Sky and Telescope, vol 68, no 2, 1984
         http://www.census.gov/cgi-bin/geo/gisfaq?Q5.1
    """
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d


def bearing(lat1, lon1, lat2, lon2):
    """Calculate the (initial) bearing between two points:

        http://williams.best.vwh.net/avform.htm#Crs

    Will return a value in radians, different from the original.
    """
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) -    \
        math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return math.atan2(y, x)


def bearing_degrees(lat1, lon1, lat2, lon2):
    """See ``bearing()```.
    """
    radians = bearing(lat1, lon1, lat2, lon2)
    return (math.degrees(x) + 360) % 360  # unsigned


def cross_track(latA, lonA, latB, lonB, latP, lonP):
    """Returns the distance of a point P from a great-circle path AB,
    in kilometers.

    Sometimes called cross track error.
    """
    d13 = distance_haversine(latA, lonA, latP, lonP)
    brng12 = bearing(latA, lonA, latB, lonB)
    brng13 = bearing(latA, lonA, latP, lonP)
    dXt = math.asin(math.sin(d13 / R) * math.sin(brng13 - brng12)) * R
    return dXt




print cross_track(
   -94.127592, 41.81762,
   -94.087257, 41.848202,
   -94.046875, 41.791057
   )



print cross_track(
  48.76165, 11.41947,
  48.75857, 11.42501,
   48.76176, 11.41595
   )