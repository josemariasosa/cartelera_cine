#!/usr/bin/env python
# coding=utf-8

import json
import datetime

import rubik as rk
import pandas as pd


class PrintMovies(object):
    
    """ Given a destination, find the closest movie.
    """
    
    def __init__(self):

        self.TOLERANCE = 10 # minutes

        self.NOW = datetime.datetime.now()
        self.TODAY = datetime.date.today()
   
    # --------------------------------------------------------------------------
    
    def calculateETA(self, duration):

        return self.NOW + datetime.timedelta(minutes=duration+self.TOLERANCE)

    # --------------------------------------------------------------------------
    
    def formatTime(self, movie_time):

        mytime = datetime.datetime.strptime(movie_time,'%H:%M').time()
        mydatetime = datetime.datetime.combine(self.TODAY, mytime)

        return mydatetime

    # --------------------------------------------------------------------------
    
    def getWaitingTime(self, nearest):

        nearest = rk.flatDict(nearest, 'movies')
        nearest = rk.unGroupLists(nearest, 'time')

        mask = nearest['time'].isnull()
        nearest = nearest[~mask].reset_index(drop=True)

        nearest['eta'] = nearest['minutes'].map(self.calculateETA)
        nearest['formatted_time'] = nearest['time'].map(self.formatTime)

        nearest['waiting'] = (nearest['formatted_time']-nearest['eta'])
        nearest['waiting'] = nearest['waiting'].astype('timedelta64[m]')
        nearest['waiting'] = nearest['waiting'].astype(int)
        
        mask = nearest['waiting'] >= 0
        nearest = nearest[mask]
        nearest = nearest.sort_values('waiting').reset_index(drop=True)

        select = [
            '_id',
            'minutes',
            'director',
            'original',
            'title',
            'time',
            'waiting'
        ]
        nearest = nearest[select]

        return nearest

    # --------------------------------------------------------------------------
    
    def formatLocation(self, s):

        s = s.replace('-', ' ').title()

        return s

    # --------------------------------------------------------------------------
    
    def printOutput(self, nearest):

        print('\n')
        nearest = nearest.drop_duplicates('title', keep='first')
        nearest = nearest.reset_index(drop=True).head(5).to_dict(orient="record")

        i = 0
        for near in nearest:
            i += 1
            print 'Option **************** {} *************************'.format(i)
            print 'Title ES: \t\t{}'.format(near['title'].encode('utf-8'))
            print 'Original Title: \t{}'.format(near['original'].encode('utf-8'))
            print 'Movie starts today at: \t{}'.format(near['time'])
            print '\nIf you leave now, you will arrive on time:'
            print 'Location: \t\t{}'.format(self.formatLocation(near['_id']))
            print 'Waiting in Traffic: \t{} minutes'.format(near['minutes'])
            print 'Waiting at Theatre: \t{} minutes'.format(near['waiting'])

            print '---------------------------------------------------\n\n'

        return None

    # --------------------------------------------------------------------------
    
    def output(self):

        with open('files/aux.json', 'r') as f:
            nearest = json.load(f)
            nearest = pd.DataFrame(nearest['results'])

        nearest = self.getWaitingTime(nearest)
        self.printOutput(nearest)

        return None

    # --------------------------------------------------------------------------
# ------------------------------------------------------------------------------

