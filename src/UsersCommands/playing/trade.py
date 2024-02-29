import disnake
from disnake.ext import commands
from disnake.ui import View, Button
from database.db import SQLighter  # Подключите вашу базу данных
from config import db_uri  # Подставьте свой URI для базы данных
from logs.log import log_action

class MoneyTransfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="transfer", description="Передача денег другому пользователю")
    async def transfer(self, ctx, recipient: disnake.Member, amount: int):
        # Проверка наличия достаточного баланса у отправителя
        db = SQLighter(db_uri)
        sender_balance = db.get_bal(ctx.author.id)
        if sender_balance < amount:
            await ctx.send("У вас недостаточно средств для этой операции.")
            return
        
        embed = disnake.Embed(
            title="Передача денег",
            description=f"Отправитель: {ctx.author.mention}\nПолучатель: {recipient.mention}\nСумма: {amount}",
            color=disnake.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text="Подтвердите операцию, нажав на кнопку ниже.")

        view = View()
        confirm_button = Button(
            style=disnake.ButtonStyle.primary,
            label="Подтвердить"
        )
        view.add_item(confirm_button)

        message = await ctx.send(embed=embed, view=view)

        async def confirm_transfer(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Эта операция не для вас!", ephemeral=True)
                return

            db.minus_balance(ctx.author.id, amount)
            db.add_balance(recipient.id, amount)
            
            success_embed = disnake.Embed(
                title="Передача денег",
                description=f"Отправитель: {ctx.author.mention}\nПолучатель: {recipient.mention}\nСумма: {amount}",
                color=disnake.Color.green()
            )
            success_embed.set_thumbnail(url=ctx.author.display_avatar.url)
            success_embed.set_footer(text=f"Передача в размере {amount} успешно выполнена! ✅")
            log_action(f"TRANSFER - from {ctx.author.name} to {recipient.name}, сумма {amount}")
            await interaction.response.edit_message(embed=success_embed, view=None)

        confirm_button.callback = confirm_transfer

def setup(bot):
    bot.add_cog(MoneyTransfer(bot))