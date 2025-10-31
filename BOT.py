import logging
import requests
import asyncio
from urllib import response
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Your Credentials ---
TELEGRAM_BOT_TOKEN = "8302327095:AAHdlVq4Mm2Mt4xnNyip3JW4xoqlosPljQk"
CRICAPI_KEY = "b4cc64b4-0bfc-4763-af53-302efa10348c"

# --- API Endpoints ---
BASE_URL = "https://api.cricapi.com/v1"
MATCHES_URL = f"{BASE_URL}/currentMatches?apikey={CRICAPI_KEY}&offset=0"
NEWS_URL = f"{BASE_URL}/cricNews?apikey={CRICAPI_KEY}"
PLAYER_URL = f"{BASE_URL}/players?apikey={CRICAPI_KEY}&search="
POINTS_URL = f"{BASE_URL}/pointsTable?apikey={CRICAPI_KEY}&id="

# --- Series Mapping ---
SERIES_MAP = {
    "ipl": "ipl2025",
    "worldcup": "wc2023",
    "t20wc": "t20wc2024",
    "ashes": "ashes2025"
}

# --- Subscriptions ---
subscriptions = {}  # {chat_id: {"last_score": ""}}

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏏 Welcome to *Pro Cricket Bot*!\n\n"
        "Tap *Menu* icon to see all commands.",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Commands*\n\n"
        "/start - Welcome to bot\n"
        "/help - Show this help\n"
        "/score - Live scores\n"
        "/matches - Ongoing & upcoming matches\n"
        "/team <name> - Team-specific matches\n"
        "/player <name> - Player stats\n"
        "/points <series> - Points table (IPL, WorldCup, etc.)\n"
        "/news - Latest cricket news\n"
        "/subscribe - Auto updates\n"
        "/unsubscribe - Stop updates\n"
        "/about - Bot info",
        parse_mode="Markdown"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Pro Cricket Bot*\n\n"
        "✔ Live scores & auto updates\n"
        "✔ Team search & player stats\n"
        "✔ Points table & news\n"
        "✔ Match notifications\n\n"
        "Built with Python + CricAPI ⚡",
        parse_mode="Markdown"
    )

# --- Score Command ---
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get(MATCHES_URL).json()
        matches = res.get("data", [])
        if not matches:
            await update.message.reply_text("❌ No live matches right now.")
            return

        message = "🏏 *Live Scores*\n\n"
        for m in matches[:5]:
            teams = f"{m['teams'][0]} vs {m['teams'][1]}"
            status = m.get("status", "N/A")
            scores = m.get("score", [])
            if scores:
                for s in scores:
                    message += f"➡️ {teams}\n{s['inning']}: {s['r']}/{s['w']} in {s['o']} overs\n📌 {status}\n\n"
            else:
                message += f"➡️ {teams}\n📌 {status}\n\n"

        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Error fetching scores")

# --- Matches Command ---
async def matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get(MATCHES_URL).json()
        matches = res.get("data", [])
        if not matches:
            await update.message.reply_text("❌ No matches found.")
            return

        message = "📅 *Ongoing & Upcoming Matches*\n\n"
        for m in matches[:5]:
            teams = f"{m['teams'][0]} vs {m['teams'][1]}"
            status = m.get("status", "N/A")
            message += f"➡️ {teams}\n📌 {status}\n\n"

        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Error fetching matches")

# --- Team Command ---
async def team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/team India`", parse_mode="Markdown")
        return

    team_name = " ".join(context.args).lower()
    try:
        res = requests.get(MATCHES_URL).json()
        matches = res.get("data", [])
        filtered = [m for m in matches if team_name in str(m['teams']).lower()]

        if not filtered:
            await update.message.reply_text(f"No matches found for {team_name.title()}")
            return

        message = f"🏏 *Matches for {team_name.title()}*\n\n"
        for m in filtered:
            teams = f"{m['teams'][0]} vs {m['teams'][1]}"
            status = m.get("status", "N/A")
            message += f"➡️ {teams}\n📌 {status}\n\n"

        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Error fetching team matches")

    await update.message.reply_text(response)

# --- Player Command ---
async def player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/player Virat Kohli`", parse_mode="Markdown")
        return

    name = " ".join(context.args)
    try:
        res = requests.get(PLAYER_URL + name).json()
        players = res.get("data", [])
        if not players:
            await update.message.reply_text("❌ Player not found.")
            return

        p = players[0]
        message = (
            f"👤 *{p['name']}*\n"
            f"🏳️ Country: {p.get('country', 'N/A')}\n"
        )

        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Error fetching player info")

# --- Points Command ---
async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/points IPL`", parse_mode="Markdown")
        return

    series_key = context.args[0].lower()
    series_id = SERIES_MAP.get(series_key)

    if not series_id:
        await update.message.reply_text("❌ Unknown series. Try IPL, WorldCup, T20WC, Ashes.")
        return

    try:
        res = requests.get(POINTS_URL + series_id).json()
        table = res.get("data", {}).get("pointsTable", [])
        if not table:
            await update.message.reply_text("❌ No points table available.")
            return

        message = f"🏆 *{series_key.upper()} Points Table*\n\n"
        for team in table:
            message += (
                f"{team['team']} - {team['points']} pts "
                f"({team['played']}P, {team['won']}W, {team['lost']}L)\n"
            )

        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Error fetching points table")

# --- News Command ---
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get(NEWS_URL).json()
        articles = res.get("data", [])
        if not articles:
            await update.message.reply_text("❌ No news found.")
            return

        message = "📰 *Cricket News*\n\n"
        for a in articles[:5]:
            message += f"➡️ {a['title']}\n🔗 {a['url']}\n\n"

        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Error fetching news")

# --- Subscriptions ---
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    subscriptions[chat_id] = {"last_score": ""}
    await update.message.reply_text("✅ Subscribed to live match updates!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in subscriptions:
        del subscriptions[chat_id]
        await update.message.reply_text("❌ Unsubscribed from updates.")
    else:
        await update.message.reply_text("You are not subscribed.")

# --- Background Task ---
async def check_updates(app: Application):
    while True:
        try:
            res = requests.get(MATCHES_URL).json()
            matches = res.get("data", [])
            if not matches:
                await asyncio.sleep(60)
                continue

            live_match = matches[0]
            scores = live_match.get("score", [])
            if not scores:
                await asyncio.sleep(60)
                continue

            score = scores[0]
            score_text = f"{score['inning']}: {score['r']}/{score['w']} in {score['o']} overs"

            for chat_id, sub in subscriptions.items():
                if sub["last_score"] != score_text:
                    sub["last_score"] = score_text
                    await app.bot.send_message(chat_id, f"📢 Live Update:\n{score_text}")
        except Exception as e:
            logger.error(f"Update error: {e}")

        await asyncio.sleep(60)

# --- Main ---
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("matches", matches))
    app.add_handler(CommandHandler("team", team))
    app.add_handler(CommandHandler("player", player))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Run background task
    app.job_queue.run_repeating(lambda _: asyncio.create_task(check_updates(app)), interval=60, first=10)
    print("🚀 Pro Cricket Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
