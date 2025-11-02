import os
import requests
import csv
import discord
from discord.ext import commands, tasks
from io import StringIO
from datetime import datetime

GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")  # Utilise la variable d'environnement

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_anniversaries():
    response = requests.get(GOOGLE_SHEET_URL)
    data = csv.DictReader(StringIO(response.text))
    events_today = []
    today = datetime.now().strftime("%d/%m")
    for row in data:
        if row["Date"] == today:
            events_today.append(f"{row['Type']}: {row['Name']}")
    return events_today

@tasks.loop(hours=24)
async def daily_check():
    channel_id = TON_ID_DU_CHANNEL
    channel = bot.get_channel(channel_id)
    events = get_anniversaries()
    if events:
        await channel.send(f"🗓️ **Aujourd'hui :**\n" + "\n".join(events))

@daily_check.before_loop
async def before_daily_check():
    await bot.wait_until_ready()

daily_check.start()

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt !")

bot.run(os.getenv("DISCORD_TOKEN"))  # Token du bot sécurisé
