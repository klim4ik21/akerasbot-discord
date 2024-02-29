import disnake
from disnake.ext import commands, tasks
from database.db import SQLighter
from disnake.ui import Button, View
import random
from config import db_uri
from logs.log import log_action

class Coinflip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="coinflip", description="Игра в монетку")
    async def coinflipchik(self, ctx, bet_amount: int):
        db = SQLighter(db_uri)
        user_balance = db.get_bal(user_id=ctx.author.id)

        if user_balance < bet_amount:
            await ctx.send("У вас недостаточно средств для этой ставки.")
        else:
            embed = disnake.Embed(title=f"{ctx.author.display_name}'s Coinflip 🪙", color=disnake.Color.blue())
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            view = View()
            button_heads = Button(label="Heads", style=disnake.ButtonStyle.primary)
            button_tails = Button(label="Tails", style=disnake.ButtonStyle.primary)
            view.add_item(button_heads)
            view.add_item(button_tails)

            message = await ctx.send(embed=embed, view=view)

            async def button_callback(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Эта игра не для вас!", ephemeral=True)

                choice = interaction.component.label
                result = random.choice(["Heads", "Tails"])
                winnings = 0
                outcome = "Lose"

                if choice == result:
                    winnings = bet_amount
                    db.add_balance(user_id=interaction.user.id, sum=winnings)
                    outcome = "Won"
                else:
                    db.minus_balance(user_id=interaction.user.id, sum=bet_amount)

                embed.title = f"{ctx.author.display_name}'s Coinflip 🪙"
                embed.description = f"Выигрыш: {winnings} монет | Ставка: {bet_amount} монет"
                embed.set_footer(text=f"Результат: {outcome} | Монета упала на {result}")
                gif_url = "https://media1.giphy.com/media/FfrlRYkqKY1lC/giphy.gif"
                embed.set_image(url=gif_url)
                log_action(f"COINFLIP - {ctx.author.name} {outcome} bet {bet_amount}")
                await interaction.response.edit_message(embed=embed, view=None)

            button_heads.callback = button_callback
            button_tails.callback = button_callback

def setup(bot):
    bot.add_cog(Coinflip(bot))
