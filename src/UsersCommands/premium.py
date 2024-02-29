import disnake
from disnake.ext import commands
from disnake.ui import Button, View
from datetime import datetime, timedelta
from database.db import SQLighter
from config import db_uri

class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SQLighter(db_uri)

    @commands.slash_command(name="premium", description="Проверка и покупка премиум-подписки")
    async def premium(self, ctx):
        user_id = ctx.author.id
        premium_end = self.db.get_premium_end(user_id=user_id)

        if premium_end is None or premium_end < datetime.now():
            # Пользователь не имеет активной подписки
            payment_url = f"https://yourpaymentpage.com/pay?user_id={user_id}"
            await ctx.send(f"У вас нет активной премиум-подписки. Для покупки перейдите по ссылке: {payment_url}")
        else:
            # Пользователь имеет активную подписку
            await ctx.send(f"Ваша премиум-подписка активна до {premium_end}")


    def get_buy_premium_view(self, ctx):
        view = View()
        buy_button = Button(label="Купить премиум", style=disnake.ButtonStyle.primary)
        view.add_item(buy_button)

        async def buy_button_callback(interaction):
            await self.buy_premium(ctx)

        buy_button.callback = buy_button_callback
        return view

    async def buy_premium(self, ctx):
        user_id = ctx.author.id
        user_balance = self.db.get_bal(user_id=user_id)
        premium_cost = 1000  # Стоимость подписки, например 1000 монет

        if user_balance < premium_cost:
            await ctx.send("У вас недостаточно средств для покупки премиум-подписки.")
            return

        # Обновляем баланс пользователя и дату окончания подписки
        self.db.minus_balance(user_id=user_id, sum=premium_cost)
        self.db.update_premium_end(user_id=user_id, new_end=datetime.now() + timedelta(weeks=1))
        
        await ctx.send(f"Премиум-подписка успешно куплена! Она будет действовать до {datetime.now() + timedelta(weeks=1)}")

def setup(bot):
    bot.add_cog(Premium(bot))
