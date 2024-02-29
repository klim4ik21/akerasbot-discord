from src import *
import disnake
from disnake.ext import commands
from database.db import SQLighter
from config import db_uri


bot = commands.Bot(command_prefix='?', intents=disnake.Intents.all())
client = disnake.Client()

bot.load_extensions("src/UsersCommands")
bot.load_extensions("src/UsersCommands/playing")
bot.load_extensions("src/AdminCommands")
bot.load_extensions("src/tech")

# Инициализация экземпляра SQLighter
db = SQLighter(db_uri)
bot.db = db


@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Game(name="Jazz 🎷"))
    print(f"Logged in as {bot.user}.")


bot.run("bot token")
