#!/usr/bin/env pythofn
# coding=utf-8

import json


def currentLocation():
    with open('files/us.json', 'r') as f:
        locations = json.load(f)

    return locations