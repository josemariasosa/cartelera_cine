#!/usr/bin/env pythofn
# coding=utf-8

import json

import rubik as rk
import pandas as pd


def getTheatreLocs():

    with open('files/theatre_locations.json', 'r') as f:
        theatres = json.load(f)

    theatres = pd.DataFrame(theatres)
    theatres = rk.flatDict(theatres, 'location')

    return theatres