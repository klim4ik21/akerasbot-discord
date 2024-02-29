import disnake
from disnake.ext import commands
from database.db import SQLighter
from config import db_uri

class LinkTgID(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SQLighter(db_uri)

    @commands.slash_command(name="link", description="Связать Telegram ID с вашей учетной записью")
    async def link_tg_id(self, ctx, telegram_id: str):
        # Проверяем, связан ли уже данный Telegram ID
        if self.db.is_tg_id_linked(telegram_id):
            await ctx.send("Этот Telegram ID уже связан с другой учетной записью.")
        else:
            # Связываем Telegram ID с учетной записью пользователя
            self.db.link_tg_id(user_id=ctx.author.id, tg_id=telegram_id)
            await ctx.send(f"Telegram ID {telegram_id} успешно связан с вашей учетной записью.")

def setup(bot):
    bot.add_cog(LinkTgID(bot))