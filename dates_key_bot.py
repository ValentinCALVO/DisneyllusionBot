import os
import requests
import csv
import discord
from discord.ext import commands, tasks
from io import StringIO
from datetime import datetime

GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")  # URL de ton Google Sheet
CHANNEL_ID = 1434557314547060766  # Remplace par ton ID de salon

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_anniversaries():
    response = requests.get(GOOGLE_SHEET_URL)
    data = csv.DictReader(StringIO(response.text))
    events_today = []
    today = datetime.now().strftime("%d/%m")
    for row in data:
        if row["date"] == today:
            events_today.append(f"{row['Type']}: {row['Name']}")
    return events_today

@tasks.loop(hours=24)
async def daily_check():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Salon {CHANNEL_ID} introuvable")
        return
    events = get_anniversaries()
    if events:
        await channel.send(f"🗓️ **Aujourd'hui :**\n" + "\n".join(events))

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt !")
    if not daily_check.is_running():  # Vérifie si la boucle est déjà en cours
        daily_check.start()  # Démarre la boucle après que le bot soit prêt

bot.run(os.getenv("DISCORD_TOKEN"))  # Token sécurisé via variable d'environnement
