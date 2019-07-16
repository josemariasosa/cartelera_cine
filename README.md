# Cartelera Cine

Get the nearest movies in a Cinépolis Theatre, of any given position expressed in coordinates. 

## Resourses

**Important!** be sure that `chromedriver` is installed, check: http://chromedriver.chromium.org/.

Always check for new chromedriver updates!

```bash
$ brew cask upgrade chromedriver
```

## Set up the Python 3 environment.

Set a new virtual environment with the required libraries.

```bash
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install pandas geopy beautifulsoup4 lxml
```

Remember you can also use the `requirements.txt` file.

```bash
$ pip install -r requirements.txt
```

## Step by step

### Step 1. Get the current location.

```python
import json


def currentLocation():
    with open('files/us.json', 'r') as f:
        locations = json.load(f)

    return locations
```

### Step 2. Get the theatres locations.

```python
import json

import rubik as rk
import pandas as pd


def getTheatreLocs():

    with open('files/theatre_locations.json', 'r') as f:
        theatres = json.load(f)

    theatres = pd.DataFrame(theatres)
    theatres = rk.flatDict(theatres, 'location')

    return theatres
```

### Step 3. Get the nearest theatres locations.

```python
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
```

### Step 4. Get the movies from Cinepolis.

```python
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

            with Browser('chrome', headless=False) as browser:

                browser.visit(url)
                time.sleep(5)

                script = "return document.body.innerHTML"
                innerHTML = browser.execute_script(script)
                # innerHTML = innerHTML.encode('utf-8') # Only in Python 2.7

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
            # movies = movies.decode('utf-8') # Only in Python 2.7

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
```

### Step 5. Show the results to the user.

```python
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
            messages = [
                'Option **************** {} *************************'.format(i),
                'Title ES: \t\t{}'.format(near['title'].encode('utf-8')),
                'Original Title: \t{}'.format(near['original'].encode('utf-8')),
                'Movie starts today at: \t{}'.format(near['time']),
                '\nIf you leave now, you will arrive on time:',
                'Location: \t\t{}'.format(self.formatLocation(near['_id'])),
                'Waiting in Traffic: \t{} minutes'.format(near['minutes']),
                'Waiting at Theatre: \t{} minutes'.format(near['waiting']),
                '---------------------------------------------------\n\n'
            ]

            for message in messages:
                print(message)

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
```


