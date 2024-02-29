import disnake
from disnake.ext import commands, tasks

class GetUserById(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="getid", description="Admin management command")
    async def getid(self, ctx, id):
        user = self.bot.get_guild(1177958005266980984).get_member(int(id))
        await ctx.send(f"this user: {user.name}, {user.mention}")


def setup(bot):
    bot.add_cog(GetUserById(bot))