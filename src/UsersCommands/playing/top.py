import disnake
from disnake.ext import commands
from database.db import SQLighter
from disnake import Embed
from config import db_uri

class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="top", description="Топ игроков по балансу")
    async def top_players(self, ctx):
        db = SQLighter(db_uri)
        top_players = db.get_top_players()
        total_balance = db.get_total_balance()

        embed = Embed(title="Топ игроков по балансу 🏆", color=disnake.Color.gold())

        for rank, player in enumerate(top_players, start=1):
            user_id, balance = player
            user = await self.bot.fetch_user(user_id)
            embed.add_field(name=f"{rank}. {user.display_name}", value=f"Баланс: {balance} монет", inline=False)
            
        embed.set_footer(text=f"Общая казна сервера: {total_balance} монет")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Top(bot))
