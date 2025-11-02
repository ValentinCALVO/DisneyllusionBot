import os
import requests
import csv
from io import StringIO
from datetime import datetime
from discord.ext import tasks, commands

TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
CHANNEL_ID = 1434557314547060766  # ID du salon

bot = commands.Bot(command_prefix="!")

def get_disney_dates():
    """Récupère les anniversaires Disney depuis Google Sheet"""
    response = requests.get(GOOGLE_SHEET_URL)
    response.raise_for_status()
    data = {}
    f = StringIO(response.text)
    reader = csv.DictReader(f)
    for row in reader:
        date = row['date']
        message = row['message']
        if date not in data:
            data[date] = []
        data[date].append(message)
    return data

@tasks.loop(hours=24)
async def daily_check():
    """Envoie les anniversaires tous les jours"""
    channel = bot.get_channel(CHANNEL_ID)
    dates_disney = get_disney_dates()
    today = datetime.now().strftime("%d-%m")
    if today in dates_disney:
        events = "\n".join(dates_disney[today])
        await channel.send(f"🗓️ **Aujourd'hui :**\n{events}")

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt !")
    daily_check.start()

bot.run(TOKEN)
