import disnake
from disnake.ext import commands

from database.db import SQLighter
from config import db_uri
import datetime

class Checkprofile(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="profile", description="Проверить свой или чужой баланс")
    async def checkbalance(ctx, member: disnake.Member=commands.Param(description="чей профиль хочешь увидеть", default=None)):
        db = SQLighter(db_uri)
        await ctx.response.defer()
        #klim4ik = await ctx.guild.fetch_emoji(1089599616917438608)

        if member == None:
            if db.check_user(ctx.author.id):
                premium_end = db.get_premium_end(user_id=ctx.author.id)
                print(premium_end)
                if premium_end is None or premium_end < datetime.datetime.now():
                    if db.get_marry(ctx.author.id) != None:
                        marry_id = db.get_marry(ctx.author.id)
                        marry_member = await ctx.guild.query_members(user_ids=[marry_id])
                        marry_name = marry_member[0].global_name
                    else:
                        marry = None
                    print("есть премиум")
                    embed=disnake.Embed(title=f"{ctx.author.name} profile")
                    embed.add_field(name=f">Коинов:", value=f"```{db.get_bal(ctx.author.id)}```", inline=True)
                    embed.add_field(name=f">vc_hours:", value=f"```{db.get_vc_hours(ctx.author.id)}```", inline=True)
                    embed.add_field(name=f">Married", value=f"```{marry_name}```", inline=True)
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                    await ctx.send(embed=embed)
                else:
                    emoji = disnake.utils.get(ctx.guild.emojis, name="ver1")
                    coin1 = disnake.utils.get(ctx.guild.emojis, name="coin96")
                    prem8 = disnake.utils.get(ctx.guild.emojis, name="premium64")
                    hour = disnake.utils.get(ctx.guild.emojis, name="hours64")
                    # Используйте более яркий и насыщенный цвет, например золотой
                    embed = disnake.Embed(title=f"{ctx.author.name} profile {str(emoji)}", color=0xFFD700)
                    coins = db.get_bal(ctx.author.id)
                    vc_hours = db.get_vc_hours(ctx.author.id)
                    embed.add_field(name="Коинов", value=f"**{coins}** {str(coin1)}", inline=True)
                    embed.add_field(name="Часов в голосовом чате", value=f"**{vc_hours}** {str(hour)}", inline=True)
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    #embed.set_footer(text=f"Premium")

                    await ctx.send(embed=embed)
            else:
                await ctx.send("Ты не авторизован")

        else:
            if db.check_user(member.id):

                embed=disnake.Embed(title=f"{member.name} profile")
                embed.add_field(name=f">Коинов:", value=f"```{db.get_bal(member.id)}```", inline=True)
                embed.add_field(name=f">vc_hours:", value=f"```{db.get_vc_hours(member.id)}```", inline=True)
                embed.set_thumbnail(url=member.display_avatar.url)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Пользователь не авторизован")
    

def setup(bot):
    bot.add_cog(Checkprofile(bot))