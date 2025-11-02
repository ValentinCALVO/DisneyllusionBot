import os
import requests
import csv
import discord
from discord.ext import commands, tasks
from io import StringIO
from datetime import datetime

# Variables d'environnement
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID du channel Discord

# Intents Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_messages_today():
    """Récupère les messages dont la date correspond à aujourd'hui."""
    response = requests.get(GOOGLE_SHEET_URL)
    data = csv.DictReader(StringIO(response.text))
    messages_today = []
    today = datetime.now().strftime("%d/%m")

    for row in data:
        # Normaliser les clés (minuscules et sans espaces)
        row = {k.strip().lower(): v for k, v in row.items()}
        if "date" in row and row["date"] == today:
            message = row.get("message", "")
            if message:
                messages_today.append(message)
    return messages_today

@tasks.loop(hours=24)
async def daily_check():
    """Tâche quotidienne pour envoyer les messages."""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Channel avec l'ID {CHANNEL_ID} introuvable.")
        return

    messages = get_messages_today()
    if messages:
        await channel.send("\n".join(messages))

@daily_check.before_loop
async def before_daily_check():
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt !")
    if not daily_check.is_running():
        daily_check.start()

bot.run(DISCORD_TOKEN)
