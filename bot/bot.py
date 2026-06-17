import sys
import os
from dotenv import load_dotenv

import socket

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
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

from search import search_movies, group_movies


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a movie name 🎬")


MAX_BUTTONS = 10


def build_version_label(v):
    label = v.get("quality", "Download")
    if v.get("sub_type"):
        label += f" ({v['sub_type']})"
    if v.get("file_size"):
        label += f" [{v['file_size']}]"
    return label


async def send_movie_page(context, chat_id, data_key, page=0, message_id=None):
    data = context.user_data.get(data_key)
    if not data:
        return

    title = data["title"]
    year = data["year"]
    versions = data["versions"]
    imdb_id = data.get("imdb_id", "")
    rating = data.get("rating", "")

    imdb_link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""
    rating_str = f" ⭐ {rating}" if rating else ""
    text = f"{title} ({year}){rating_str}"

    total = len(versions)
    if total == 0:
        return

    start = page * MAX_BUTTONS
    end = min(start + MAX_BUTTONS, total)
    chunk = versions[start:end]

    buttons = []
    for v in chunk:
        buttons.append([
            InlineKeyboardButton(build_version_label(v), url=v["url"])
        ])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Back", callback_data=f"page:{data_key}:{page - 1}"))

    shown = f"{start + 1}-{end}"
    nav_buttons.append(InlineKeyboardButton(f"{shown}/{total}", callback_data="noop"))

    if end < total:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"page:{data_key}:{page + 1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    if end >= total and imdb_link:
        buttons.append([InlineKeyboardButton("IMDb", url=imdb_link)])

    reply_markup = InlineKeyboardMarkup(buttons)
    msg = f"{text}\n({shown}/{total})"

    if message_id:
        await context.bot.edit_message_text(msg, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id, msg, reply_markup=reply_markup)


async def send_movie_result(update, context, movie):
    if "movie_counter" not in context.user_data:
        context.user_data["movie_counter"] = 0
    context.user_data["movie_counter"] += 1
    data_key = f"movie:{context.user_data['movie_counter']}"

    context.user_data[data_key] = {
        "title": movie["title"],
        "year": movie["year"],
        "imdb_id": movie.get("imdb_id", ""),
        "rating": movie.get("rating", ""),
        "versions": movie["versions"],
    }
    await send_movie_page(context, update.effective_chat.id, data_key, page=0)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "noop":
        return

    parts = data.split(":", 2)
    if len(parts) != 3 or parts[0] != "page":
        return

    _, data_key, page_str = parts
    page = int(page_str)
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    await send_movie_page(context, chat_id, data_key, page, message_id=message_id)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()

    results = search_movies(query)
    grouped = group_movies(results)

    if not grouped:
        await update.message.reply_text("No results found ❌")
        return

    for key, movie in grouped.items():
        await send_movie_result(update, context, movie)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
