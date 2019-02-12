#!/usr/bin/env python
# coding=utf-8

import math
import geopy.distance


class TravelTimes(object):
    
    VELOCITY = 5 # km per hour

    def __init__(self, lat, lon):

        self.LAT = lat
        self.LON = lon
        
    def trafficTime(self, row):

        coords_1 = (row['lat'], row['lon'])
        coords_2 = (self.LAT, self.LON)

        distance = geopy.distance.vincenty(coords_1, coords_2).km
        duration = (distance / self.VELOCITY) * 60
        duration = math.ceil(duration)

        return int(duration)

    # --------------------------------------------------------------------------
    
    def getNearestTheatre(self, locations):

        locations['minutes'] = locations.apply(self.trafficTime, axis=1)
        locations = locations.sort_values('minutes').reset_index(drop=True)

        # Keep only 3 theatres.
        locations = locations.head(3)

        return locations[['_id', 'zone', 'minutes']]

    # --------------------------------------------------------------------------
# ------------------------------------------------------------------------------

