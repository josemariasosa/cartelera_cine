#!/usr/bin/env python
# coding=utf-8

# ------------------------------------------------------------------------------
# Cinepolis Tools | Mi Refacción
# ------------------------------------------------------------------------------
# jose maria sosa

""" Getting the Cinepolis Movies.
"""

from modules._1_where_are_we import currentLocation
from modules._2_theatre_location import getTheatreLocs
from modules._3_nearest_movies import TravelTimes
from modules._4_scrapy_movies import Cinepolis
from modules._5_show_results import PrintMovies


def main():

    # Step 1. Get the current location.
    locations = currentLocation()

    message = "Type the index for a desired current location: "
    for i, loc in enumerate(locations):
        print "{} ".format(i), loc['name']
    option = raw_input(message)

    if (option.isdigit()) and (option in [str(x) for x in range(len(locations))]):
        option = int(option)
        locations = locations[option]

    else:
        print('Not a valid option!')
        exit()


    # Step 2. Get the theatres locations.
    theatres = getTheatreLocs()


    # Step 3. Get the nearest theatres locations.
    lat = locations['location']['lat']
    lon = locations['location']['lon']
    nearest = TravelTimes(lat, lon).getNearestTheatre(theatres)


    # Step 4. Get the movies from Cinepolis.
    Cinepolis().updateMovies(nearest)


    # Step 5. Show the results to the user.
    PrintMovies().output()


if __name__ == '__main__':
    main()
