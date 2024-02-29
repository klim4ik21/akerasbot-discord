import disnake
from disnake.ext import commands

from database.db import SQLighter
from config import db_uri
import datetime

adm_id = 468445928878112793

class AddPremium(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="adm_premium", description="get premium for user")
    async def checkbalance(ctx, member: disnake.Member=commands.Param(description="userid", default=None)):
        db = SQLighter(db_uri)
        if adm_id == ctx.author.id:
            db.upd_premium(user_id=member.id)
            await ctx.send(f"получил подписку {member.name}")

def setup(bot):
    bot.add_cog(AddPremium(bot))
