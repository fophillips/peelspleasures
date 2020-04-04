import tweepy
import os
import urllib
import random
import collections
import psycopg2
from googleapiclient.discovery import build

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
DB_URL = os.environ['DATABASE_URL']
YT_KEY = os.environ['YT_KEY']

class Track(collections.namedtuple(
        "Track",
        ("id", "artist", "title", "label", "date"))):
    __slots__ = ()
    def __str__(self):
        return "{artist} - {title} ({label}) - #JohnPeel {date}".format(
            artist=self.artist,
            title=self.title,
            label=self.label,
            date=self.date)

def pop_track():
    urllib.parse.uses_netloc.append("postgres")
    url = urllib.parse.urlparse(DB_URL)
    with psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM tracks WHERE NOT played")
            tracks_left = cursor.fetchone()[0]
            track_row = random.randint(0, tracks_left)
            cursor.execute("SELECT id, artist, title, label, date FROM tracks WHERE NOT played OFFSET %(n)s LIMIT 1", {"n": track_row})
            track_data = cursor.fetchone()
            cursor.execute("UPDATE tracks SET played = TRUE WHERE id = %(id)s",
                           {'id': track_data[0]})
    return Track(*track_data)

def get_track_video(track):
    s = build("youtube", "v3", developerKey=YT_KEY)
    query = "{artist} {title}".format(artist=track.artist, title=track.title)
    request = s.search().list(part='snippet', q=query)
    response = request.execute()
    if response['items'] and all(w in response['items'][0]['snippet']['title'].upper() for w in query.upper().split()):
        return "http://youtu.be/{}".format(response['items'][0]['id']['videoId'])
    else:
        return None

def tweet_track():
    track = pop_track()
    video = get_track_video(track)
    if video:
        status = "{track} {video}".format(track=str(track), video=video)
    else:
        status = str(track)
    print(status)

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    #api.update_status(status)

if __name__ == "__main__":
    import sys
    tweet_track()
