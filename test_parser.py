from crawler.parsers.donyayeserial_parser import DonyayeSerialParser, DonyayeSerialArchiveParser
from crawler.parser_factory import ParserFactory
import requests

parser = DonyayeSerialParser()

test_urls = [
    "https://dls2.film2cinemaha.top/DonyayeSerial/movie4/1939/tt0032138/SoftSub/The.Wizard.Of.OZ.1939.1080p.BluRay.x265.RARBG.SoftSub.DonyayeSerial.mkv",
    "https://dls2.film2cinemaha.top/DonyayeSerial/movie4/1939/tt0032138/SoftSub/The.Wizard.Of.Oz.1939.BluRay.720p.YIFY.SoftSub.DonyayeSerial.mkv",
    "https://dls2.film2cinemaha.top/DonyayeSerial/movies/2000/tt0160484/NoSub/Lost.Souls.2000.720p.WEBRip.YIFY.DonyayeSerial.mp4",
    "https://dls2.film2cinemaha.top/DonyayeSerial/series/Mindhunter/Dubbed/S02/1080p.Web-DL/Mindhunter.S02E01.1080p.Web-DL.mkv",
    "https://dls4.film2cinemaha.top/DonyayeSerial/movies/1994/tt0111161/SoftSub/The.Shawshank.Redemption.1994.1080p.BluRay.SoftSub.RARBG.DonyayeSerial.mkv",
]

for url in test_urls:
    result = parser.parse(url)
    print("=" * 60)
    print(f"File: {url.split('/')[-1]}")
    for k, v in result.items():
        if v:
            print(f"  {k}: {v}")

# Test with HTML table for file size extraction
print("\n\n" + "=" * 60)
print("TEST: HTML table parsing for file size")
print("=" * 60)

try:
    page_url = "https://dls2.film2cinemaha.top/DonyayeSerial/movie4/1939/tt0032138/SoftSub/"
    r = requests.get(page_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    html = r.text

    file_url = "https://dls2.film2cinemaha.top/DonyayeSerial/movie4/1939/tt0032138/SoftSub/The.Wizard.Of.Oz.1939.BluRay.720p.YIFY.SoftSub.DonyayeSerial.mkv"
    result = parser.parse(file_url, html)
    print(f"File: {file_url.split('/')[-1]}")
    for k, v in result.items():
        if v:
            print(f"  {k}: {v}")
except Exception as e:
    print(f"HTML test error: {e}")

# Test archive parser
print("\n\n" + "=" * 60)
print("TEST: Archive parser")
print("=" * 60)

try:
    archive_url = "https://dls2.film2cinemaha.top/DonyayeSerial/top_5000_movies.html"
    r = requests.get(archive_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    html = r.text
    archive_parser = DonyayeSerialArchiveParser()
    movies = archive_parser.parse(archive_url, html)
    if movies:
        print(f"Parsed {len(movies)} movies from archive page")
        for m in movies[:3]:
            print(f"  - {m.get('title')} (IMDb: {m.get('imdb_id')}, Rating: {m.get('rating')})")
            for v in m.get('versions', []):
                print(f"      {v.get('quality_label')} [{v.get('size')}] ({v.get('sub_type')})")
except Exception as e:
    print(f"Archive test error: {e}")
