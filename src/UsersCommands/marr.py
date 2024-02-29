import disnake
from disnake.ext import commands
from disnake.ui import View, Button
import datetime  # Импорт модуля datetime
from database.db import SQLighter
from config import db_uri

# Подключите вашу базу данных, если это необходимо
# from database.db import SQLighter  
# from config import db_uri  # Подставьте свой URI для базы данных

class Marriage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="married", description="Предложение о браке другому пользователю")
    async def married(self, ctx, user: disnake.Member):
        # Создание Embed-сообщения с аватарками и именами
        embed = disnake.Embed(
            title="Предложение о браке",
            description=f"{ctx.author.mention} предлагает брак {user.mention}",
            color=disnake.Color.purple()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_image(url=ctx.author.display_avatar.url)
        embed.set_footer(text="Выберите действие ниже.")

        # Создание кнопок для согласия и отказа
        view = View()

        accept_button = Button(
            style=disnake.ButtonStyle.success,
            label="Согласиться"
        )
        decline_button = Button(
            style=disnake.ButtonStyle.danger,
            label="Отказаться"
        )
        view.add_item(accept_button)
        view.add_item(decline_button)

        # Отправка Embed-сообщения с кнопками
        message = await ctx.send(embed=embed, view=view)

        # Функции обработки нажатия кнопок
        async def accept(interaction):
            if interaction.user != user:
                await interaction.response.send_message("Это не для вас!", ephemeral=True)
                return
            # Получение текущей даты
            db = SQLighter(db_uri)
            if db.get_bal(user_id=ctx.author.id) < 100000:
                await interaction.response.send_message("Вам не хватает баланса стоимость 100к", ephemeral=True)
                return
            #if db.get_marry != None:
                #await interaction.response.send_message("Вы уже состоите в браке!")
                #return
            today = datetime.date.today().strftime("%d.%m.%Y")
            db.marry(ctx.author.id, interaction.user.id)
            db.marry(interaction.user.id, ctx.author.id)
            db.marry_time(marry_time=today, user_id=ctx.author.id)
            db.marry_time(marry_time=today, user_id=interaction.user.id)
            db.minus_balance(sum=100000, user_id=ctx.author.id)

            # Здесь код для обновления базы данных, если это необходимо
            # Отредактирование сообщения о согласии
            success_embed = disnake.Embed(
                title="Бракосочетание",
                description=f"{ctx.author.mention} и {user.mention} теперь в браке 💍\nДата бракосочетания: {today}",
                color=disnake.Color.green()
            )
            success_embed.set_image(url="https://media2.giphy.com/media/Q3I7uuGWABAUlYo8DM/giphy.gif?cid=ecf05e47th42lqxa26jl5w04qspkgbc52d9980dmmkictvua&ep=v1_gifs_search&rid=giphy.gif")
            await interaction.response.edit_message(embed=success_embed, view=None)

        async def decline(interaction):
            if interaction.user != user:
                await interaction.response.send_message("Это не для вас!", ephemeral=True)
                return
            # Отредактирование сообщения об отказе
            fail_embed = disnake.Embed(
                title="Брак",
                description=f"{user.mention} отказался от предложения {ctx.author.mention} 💔",
                color=disnake.Color.red()
            )
            await interaction.response.edit_message(embed=fail_embed, view=None)

        accept_button.callback = accept
        decline_button.callback = decline

def setup(bot):
    bot.add_cog(Marriage(bot))
