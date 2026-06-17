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


# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()

    results = search_movies(query)
    grouped = group_movies(results)

    if not grouped:
        await update.message.reply_text("No results found ❌")
        return

    for key, movie in grouped.items():
        title = movie["title"]
        year = movie["year"]
        versions = movie["versions"]
        imdb_id = movie.get("imdb_id") or ""
        rating = movie.get("rating") or ""

        imdb_link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""
        rating_str = f" ⭐ {rating}" if rating else ""

        text = f"{title} ({year}){rating_str}"

        buttons = []

        for v in versions:
            label = v.get("quality", "Download")

            if v.get("sub_type"):
                label += f" ({v['sub_type']})"
            if v.get("file_size"):
                label += f" [{v['file_size']}]"

            buttons.append([
                InlineKeyboardButton(
                    label,
                    url=v["url"]
                )
            ])

        if imdb_link:
            buttons.append([
                InlineKeyboardButton("IMDb", url=imdb_link)
            ])

        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text, reply_markup=reply_markup)


# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()