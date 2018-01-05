from datetime import datetime
from time import *

import json
import requests

client_id = "10f2b8848e81cad86d5515b87221a59b771f088bb6b5d31ae33d6c6478aac658"

def get_full_movie(trakt_id, cache, timeout):
    tag = "movie-{0}".format(trakt_id)
    cached = cache.get(trakt_id)

    if cached:
        movie_info = json.loads(cached)
    else:
        headers = {
            'Content-Type': 'application/json',
            'trakt-api-version' : '2',
            'trakt-api-key' : client_id
        }
        url = 'https://api-v2launch.trakt.tv/movies/{0}?extended=full,images'.format(trakt_id)
        result = requests.get(url, headers=headers)

        cache.set(tag, result.text, timeout)
        movie_info = result.json()

    if movie_info['released'] != None:
        formatted = strptime(movie_info['released'], "%Y-%m-%d")
        movie_info['released'] = datetime.fromtimestamp(mktime(formatted))

    return movie_info

def get_full_show(trakt_id, cache, timeout):
    tag = "show-{0}".format(trakt_id)
    cached = cache.get(trakt_id)

    if cached:
        show_info = json.loads(cached)
    else:
        headers = {
            'Content-Type': 'application/json',
            'trakt-api-version' : '2',
            'trakt-api-key' : client_id
        }
        url = 'https://api-v2launch.trakt.tv/shows/{0}?extended=full,images'.format(trakt_id)
        result = requests.get(url, headers=headers)

        cache.set(tag, result.text, timeout)
        show_info = result.json()

    if show_info['first_aired'] and show_info['first_aired'] != "None":
        formatted = strptime(show_info['first_aired'][:10],"%Y-%m-%d")
        show_info['first_aired'] = datetime.fromtimestamp(mktime(formatted))

    try:
        day = show_info["airs"]["day"]
        time = show_info["airs"]["time"]
        show_info["airs"] = None

        if day != None and time != None:
            show_info['airs'] = datetime.strptime(day + " " + time, "%A %H:%M")
    except KeyError:
        show_info["airs"] = None

    return show_info