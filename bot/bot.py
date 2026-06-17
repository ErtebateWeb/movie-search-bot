import sys
import os
from dotenv import load_dotenv

import socket

# Force IPv4 for all outgoing connections
orig_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4(*args, **kwargs):
    return [
        addr for addr in orig_getaddrinfo(*args, **kwargs)
        if addr[0] == socket.AF_INET
    ]

socket.getaddrinfo = getaddrinfo_ipv4
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from search import search_movies, group_movies


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a movie name 🎬")


# Maximum buttons per message to avoid "Reply markup is too long"
MAX_BUTTONS = 10


def build_version_label(v):
    label = v.get("quality", "Download")
    if v.get("sub_type"):
        label += f" ({v['sub_type']})"
    if v.get("file_size"):
        label += f" [{v['file_size']}]"
    return label


async def send_movie_result(update, movie):
    title = movie["title"]
    year = movie["year"]
    versions = movie["versions"]
    imdb_id = movie.get("imdb_id") or ""
    rating = movie.get("rating") or ""

    imdb_link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""
    rating_str = f" ⭐ {rating}" if rating else ""
    text = f"{title} ({year}){rating_str}"

    total = len(versions)
    if total == 0:
        return

    first_msg = True
    for start_idx in range(0, total, MAX_BUTTONS):
        chunk = versions[start_idx:start_idx + MAX_BUTTONS]
        buttons = []

        for v in chunk:
            buttons.append([
                InlineKeyboardButton(build_version_label(v), url=v["url"])
            ])

        # Add IMDb link only on the last chunk
        is_last = (start_idx + MAX_BUTTONS >= total)
        if is_last and imdb_link:
            buttons.append([InlineKeyboardButton("IMDb", url=imdb_link)])

        if first_msg:
            msg = text
            if total > MAX_BUTTONS:
                shown = min(start_idx + MAX_BUTTONS, total)
                msg += f"\n({shown}/{total} shown)"
            first_msg = False
        else:
            shown = min(start_idx + MAX_BUTTONS, total)
            msg = f"... ({shown}/{total})"

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(msg, reply_markup=reply_markup)


# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()

    results = search_movies(query)
    grouped = group_movies(results)

    if not grouped:
        await update.message.reply_text("No results found ❌")
        return

    for key, movie in grouped.items():
        await send_movie_result(update, movie)


# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()