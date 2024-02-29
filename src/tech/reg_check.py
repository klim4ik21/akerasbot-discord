import disnake
from disnake.ext import commands, tasks
import asyncio
from config import guild_id, db_uri

from database.db import SQLighter
from datetime import datetime, timedelta
from logs.log import log_action, error_action

class regCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_users.start()

    def cog_unload(self):
        self.check_users.cancel()

    @commands.slash_command(description="reload_cog")
    async def cogreload(self, inter: disnake.ApplicationCommandInteraction, cog_file: str):
        db = SQLighter(db_uri)
        isadmin = db.is_admin(inter.author.id)
        """Поиск логов по имени пользователя, действию и дате, доступен только администратору."""
        if isadmin == 0:
            await inter.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        if cog_file.startswith("!"):
            cog_file = cog_file[1:]
            extension_name = f'src.AdminCommands.{cog_file}'
        elif cog_file.startswith(".p"):
            cog_file = cog_file[2:]
            extension_name = f'src.UsersCommands.playing.{cog_file}'
        elif cog_file.startswith(".t"):
            print("tech restarting")
            cog_file = cog_file[2:]
            extension_name = f'src.tech.{cog_file}'
        else:
            extension_name = f'src.UsersCommands.{cog_file}'
        if extension_name in self.bot.extensions:
            try:
                self.bot.reload_extension(extension_name)
                log_action(f"COGRELOAD by {inter.author.name} cog {cog_file}")
                await inter.response.send_message(f"Cog `{cog_file}` успешно перезагружен.")
            except Exception as e:
                await inter.response.send_message(f"Произошла ошибка при перезагрузке cog `{cog_file}`: {e}")
        else:
            await inter.response.send_message(f"Cog `{cog_file}` не загружен и не может быть перезагружен.")

    
    @commands.slash_command(name="rich21", description="adminskiy add bal21.")
    async def check_users(self, ctx):
        db = SQLighter(db_uri)
        db.add_balance(user_id=ctx.author.id, sum=100)
        ctx.send("выдал 21ю.")


    @tasks.loop(seconds=5)
    async def check_users(self):
        current_time = datetime.now()
        target_time = datetime(2023, 12, 14, 0, 0, 0)
        for guild in self.bot.guilds:
            for member in guild.members:
                if await self.check_user_from_database(member.id) == False:
                    db = SQLighter(db_uri)
                    db.register(member.id)
                    log_action(f"REGISTERED - {member.name} {member.id}")

    async def check_user_from_database(self, user_id):
        db = SQLighter(db_uri)
        if db.check_user(user_id):
            return True
        else:
            return False

def setup(bot):
    bot.add_cog(regCheck(bot))
