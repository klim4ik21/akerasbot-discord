import disnake
from disnake.ext import commands
from database.db import SQLighter
from disnake.ui import Button, View
from config import db_uri

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.slash_command(name="cgame", description="Игра в камень, ножницы, бумагу с другим пользователем")
    async def rps_game(self, ctx, opponent: disnake.Member, bet_amount: int):
        db = SQLighter(db_uri)
        user_balance = db.get_bal(user_id=ctx.author.id)
        opponent_balance = db.get_bal(user_id=opponent.id)

        if user_balance < bet_amount or opponent_balance < bet_amount:
            await ctx.send("Один из игроков не имеет достаточно средств для этой ставки.")
            return

        embed = disnake.Embed(title=f"{ctx.author.display_name} vs {opponent.display_name} - Rock Paper Scissors 🗿✂️📄", color=disnake.Color.orange())
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        view = View()
        for choice in ["Rock", "Paper", "Scissors"]:
            button = Button(label=choice, style=disnake.ButtonStyle.primary)
            button.callback = self.button_callback
            view.add_item(button)

        self.active_games[(ctx.author.id, opponent.id)] = {'ctx': ctx, 'bet_amount': bet_amount, 'choices': {}, 'view': view}

        await ctx.send(f"{opponent.mention}, вы вызваны на игру в камень, ножницы, бумагу! Ставка: {bet_amount} монет.", embed=embed, view=view)

    async def button_callback(self, interaction):
        game = self.active_games.get((interaction.message.interaction.user.id, interaction.user.id)) or self.active_games.get((interaction.user.id, interaction.message.interaction.user.id))
        if not game:
            return await interaction.response.send_message("Эта игра не для вас!", ephemeral=True)

        game['choices'][interaction.user.id] = interaction.component.label

        if len(game['choices']) == 2:
            await self.resolve_game(game)

    async def resolve_game(self, game):
        ctx = game['ctx']
        bet_amount = game['bet_amount']
        choices = game['choices']
        db = SQLighter(db_uri)

        def determine_winner(choice1, choice2):
            if (choice1 == "Rock" and choice2 == "Scissors") or (choice1 == "Scissors" and choice2 == "Paper") or (choice1 == "Paper" and choice2 == "Rock"):
                return 1
            elif choice1 == choice2:
                return 0
            else:
                return -1

        player1, player2 = choices.keys()
        outcome = determine_winner(choices[player1], choices[player2])

        if outcome == 1:
            winner, loser = player1, player2
        elif outcome == -1:
            winner, loser = player2, player1
        else:
            winner, loser = None, None

        if winner:
            db.add_balance(user_id=winner, sum=bet_amount)
            db.minus_balance(user_id=loser, sum=bet_amount)
            result_text = f"{ctx.guild.get_member(winner).display_name} победил и выиграл {bet_amount} монет!"
        else:
            result_text = "Игра окончилась вничью!"

        embed = disnake.Embed(title="Результат игры", description=result_text, color=disnake.Color.purple())
        await ctx.send(embed=embed)
        game['view'].disable_all_items()
        await ctx.edit_original_message(view=game['view'])

        del self.active_games[(player1, player2)]

def setup(bot):
    bot.add_cog(RockPaperScissors(bot))