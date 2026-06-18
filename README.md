# Movie Search Bot

Telegram bot for searching movies and series from DonyayeSerial and Film2Media sources.

## Setup

1. Copy `.env.example` to `.env` and fill in your `BOT_TOKEN` (get from [@BotFather](https://t.me/BotFather)).

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Crawl Sources

Edit `config.py` to enable/disable sources. Uncomment the URLs you want to crawl:

```python
SOURCES = [
    "https://edge01.155626.ir.cdn.ir/aG5p/Film/New-Server/",
    "https://dls2.film2cinemaha.top/DonyayeSerial/movies/",
    "https://dls2.film2cinemaha.top/DonyayeSerial/movie4/",
    #"https://dls2.film2cinemaha.top/DonyayeSerial/series/",
    #"https://dls2.film2cinemaha.top/DonyayeSerial/series2/",
    #"https://dls2.film2cinemaha.top/DonyayeSerial/series3/",
    #"https://dls2.film2cinemaha.top/DonyayeSerial/series4/",
]
```

## Crawl

Populate the database with movie data:

```bash
python crawler.py
```

Crawls configured sources concurrently (5 threads by default), extracts movie/series info, and saves to `storage/movies.db`.

## Run the Bot

```bash
python bot/bot.py
```

## Usage

Send any movie or series name to the bot. Examples:

- `jurassic park` — search by title
- `tt0118570` — search by IMDb ID
- `Air Bud` — partial title match

Results show quality, subtitle type, and file size for each version. Series episodes display episode number (e.g. `S03E05 - 720p`). Use ◀️/▶️ buttons to navigate large results.

## Branch Info

- `main` — stable, tagged releases
- `V2` — concurrent crawling, episode labels, bot pagination
