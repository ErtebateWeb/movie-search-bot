from database.db import init_db, get_connection, save_movie
from crawler.parsers.donyayeserial_parser import DonyayeSerialArchiveParser
import requests
import sqlite3

init_db()
conn = get_connection()
parser = DonyayeSerialArchiveParser()

urls = [
    'https://dls2.film2cinemaha.top/DonyayeSerial/top_5000_movies.html',
    'https://dls2.film2cinemaha.top/DonyayeSerial/top_1000_series.html',
]

for archive_url in urls:
    print(f'Fetching {archive_url}...')
    r = requests.get(archive_url, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
    movies = parser.parse(archive_url, r.text)
    print(f'  Found {len(movies)} entries')
    for movie in movies:
        if movie and movie.get('versions'):
            for v in movie['versions']:
                save_movie(conn, {
                    'title': movie.get('title'),
                    'year': movie.get('year'),
                    'quality': v.get('quality_label'),
                    'imdb_id': movie.get('imdb_id'),
                    'rating': movie.get('rating'),
                    'votes': movie.get('votes'),
                    'url': v.get('url'),
                    'file_size': v.get('size'),
                    'sub_type': v.get('sub_type'),
                })
    print(f'  Saved to DB')

conn.close()

c = sqlite3.connect('storage/movies.db')
count = c.execute('SELECT COUNT(title) FROM movies').fetchone()[0]
print(f'Total in DB: {count}')
c.close()
