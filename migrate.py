import os
import json
import psycopg2
import urllib.parse
import uuid

DB_URL = os.environ['DATABASE_URL']

def migrate():
    with open("tracks.json", "r") as f:
        tracks = json.load(f)

    for track in tracks:
        track['id'] = str(uuid.uuid4())

    urllib.parse.uses_netloc.append("postgres")
    url = urllib.parse.urlparse(DB_URL)
    with psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port) as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE TABLE tracks (id uuid primary key, artist text, title text, label text, download_link text, url text, date date, played bool)")
            for track in tracks:
                cursor.execute("INSERT INTO tracks (id, title, artist, label, date, download_link, url, played) values (%(id)s, %(title)s, %(artist)s, %(label)s, %(date)s, %(download_link)s, %(url)s, FALSE)", track)
        conn.commit()

if __name__ == "__main__":
    migrate()
