import sys
import os
from dotenv import load_dotenv


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

        text = f"{title} ({year})"

        # Create buttons for qualities
        buttons = []

        for v in versions:
            buttons.append([
                InlineKeyboardButton(
                    v["quality"],
                    url=v["url"]  # direct download
                )
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