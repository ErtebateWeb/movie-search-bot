(Movie Search Bot)

Environment variables
---------------------

Copy `.env.example` to `.env` and fill in your secrets (Telegram `BOT_TOKEN`, `CLAUDE_API_KEY`, etc.). The project uses `python-dotenv` to load `.env` when present.

Examples:

Windows PowerShell:

```powershell
setx BOT_TOKEN "your-telegram-bot-token"
setx CLAUDE_API_KEY "your-claude-api-key"
```

Windows CMD:

```cmd
set BOT_TOKEN=your-telegram-bot-token
set CLAUDE_API_KEY=your-claude-api-key
```

Unix / macOS (bash):

```bash
export BOT_TOKEN=your-telegram-bot-token
export CLAUDE_API_KEY=your-claude-api-key
```

Or simply create a `.env` file in the project root with the keys shown in `.env.example`.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the bot:

```bash
python bot/bot.py
```

