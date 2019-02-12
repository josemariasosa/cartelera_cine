#!/usr/bin/env python
# coding=utf-8

# ------------------------------------------------------------------------------
# Cinepolis Tools | Mi Refacción
# ------------------------------------------------------------------------------
# jose maria sosa

import json
import time
import datetime

import bs4 as bs
import rubik as rk
import pandas as pd

from splinter import Browser


class Cinepolis(object):
    
    def __init__(self):

        self.NOW = datetime.datetime.now()

    def getUrlHtml(self, url):

            with Browser('chrome', headless=True) as browser:

                browser.visit(url)
                time.sleep(5)

                script = "return document.body.innerHTML"
                innerHTML = browser.execute_script(script)
                innerHTML = innerHTML.encode('utf-8') 

                with open('files/movies.txt', 'w') as f:
                    f.write(innerHTML)
    
    # --------------------------------------------------------------------------
    
    def concatSite(self, row):

        url = "http://www.cinepolis.com/cartelera/{}/{}"
        url = url.format(row['zone'], row['_id'])

        return url

    # --------------------------------------------------------------------------
    
    def getMovieTime(self, link):

        time_list = []

        for time in link.find_all('time'):
            if 'value' in time.attrs.keys():
                value = time.attrs['value']
                time_list.append(value)

        return time_list

    # --------------------------------------------------------------------------
    
    def checkCinepolis(self, url):
    
        self.getUrlHtml(url)

        with open('files/movies.txt', 'r') as f:
            movies = f.read()
            movies = movies.decode('utf-8')

        soup = bs.BeautifulSoup(movies, 'lxml')

        movie_list = []
        for link in soup.find_all('article'):
            for span in link.find_all('span'):
                if 'class' in span.attrs.keys():
                    if 'data-layer' in span['class']:
                        movie_list.append({
                            'director': span.attrs['data-director'],
                            'title': span.attrs['data-titulo'],
                            'location': span.attrs['data-list'],
                            'original': span.attrs['data-titulooriginal'],
                            'time': self.getMovieTime(link)
                        })

        return movie_list

    # --------------------------------------------------------------------------
    
    def getMovies(self, nearest):

        nearest['site'] = nearest.apply(self.concatSite, axis=1)

        nearest['movies'] = nearest['site'].map(self.checkCinepolis)
        nearest = rk.unGroupLists(nearest, 'movies')

        return nearest

    # --------------------------------------------------------------------------
    
    def updateMovies(self, nearest):

        nearest = self.getMovies(nearest)

        with open('files/aux.json', 'w') as f:
            json.dump({
                'results': nearest.to_dict(orient='record'),
                'last_update': self.NOW.strftime('%d-%b-%Y %H:%M')
            }, f)

        return None

    # --------------------------------------------------------------------------
# ------------------------------------------------------------------------------

