import disnake
from disnake.ext import commands, tasks
from database.db import SQLighter
from disnake.ui import View, Button, Modal, TextInput, Select
from disnake import SelectOption
import datetime
from config import db_uri

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SQLighter(db_uri)
        self.role_check_task.start()

    @commands.slash_command(name="create_role", description="Создать новую роль")
    async def create_role(self, ctx, role_name: str, hex_color: str):
        user_balance = self.db.get_bal(user_id=ctx.author.id)
        role_creation_cost = 1000
        if user_balance < role_creation_cost:
            await ctx.send("Недостаточно средств для создания роли.")
            return

        try:
            color = disnake.Color(int(hex_color, 16))
            new_role = await ctx.guild.create_role(name=role_name, color=color)
            await ctx.author.add_roles(new_role)
            role_expiry = datetime.datetime.now() + datetime.timedelta(weeks=1)
            self.db.add_role(role_name, new_role.id, ctx.author.id, role_creation_cost, role_expiry)
            await ctx.send(f"Роль '{role_name}' успешно создана и назначена вам.")
        except Exception as e:
            await ctx.send(f"Ошибка при создании роли: {e}")

    @commands.slash_command(name="manage_role", description="Управление ролью")
    async def manage_role(self, ctx):
        roles = self.db.get_user_roles(ctx.author.id)
        options = [SelectOption(label=role[0], value=str(role[1])) for role in roles]
        select = RoleSelect(ctx, options)
        view = View()
        view.add_item(select)
        await ctx.send("Выберите роль для управления:", view=view)

    @tasks.loop(minutes=60)
    async def role_check_task(self):
        expired_roles = self.db.get_expired_roles()
        for role in expired_roles:
            try:
                discord_role = self.bot.get_guild(role[2]).get_role(role[1])
                if discord_role:
                    await discord_role.delete()
                self.db.remove_role(role[1])
            except Exception as e:
                print(f"Ошибка при удалении роли: {e}")

    @role_check_task.before_loop
    async def before_role_check_task(self):
        await self.bot.wait_until_ready()

class RoleSelect(disnake.ui.Select):
    def __init__(self, ctx, options):
        super().__init__(placeholder="Выберите роль...", min_values=1, max_values=1, options=options)
        self.ctx = ctx

    async def callback(self, interaction: disnake.Interaction):
        role_id = int(self.values[0])
        view = ManageRoleView(self.ctx, role_id)
        await interaction.response.edit_message(content="Управление ролью:", view=view)

class ManageRoleView(disnake.ui.View):
    def __init__(self, ctx, role_id):
        super().__init__()
        self.ctx = ctx
        self.role_id = role_id

    @disnake.ui.button(label="Подарить роль", style=disnake.ButtonStyle.green, custom_id="give_role")
    async def give_role(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        # Логика для подарка роли
        await interaction.response.send_modal(GiveRoleModal(self.ctx, self.role_id))

    @disnake.ui.button(label="Изменить цену", style=disnake.ButtonStyle.blurple, custom_id="change_price")
    async def change_price(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        # Логика для изменения цены
        await interaction.response.send_modal(ChangePriceModal(self.ctx, self.role_id))

    @disnake.ui.button(label="Изменить цвет", style=disnake.ButtonStyle.grey, custom_id="change_color")
    async def change_color(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        # Логика для изменения цвета
        await interaction.response.send_modal(ChangeColorModal(self.ctx, self.role_id))

    @disnake.ui.button(label="Забрать роль", style=disnake.ButtonStyle.red, custom_id="remove_role")
    async def remove_role(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        # Логика для удаления роли
        await interaction.response.send_modal(RemoveRoleModal(self.ctx, self.role_id))


# Реализация модальных окон для каждой кнопки
class RemoveRoleModal(disnake.ui.Modal):
    def __init__(self, ctx, role_id, *args, **kwargs):
        super().__init__("Забрать роль", *args, **kwargs)
        self.ctx = ctx
        self.role_id = role_id
        self.add_item(disnake.ui.TextInput(label="ID пользователя", placeholder="Введите ID пользователя"))

    async def callback(self, interaction: disnake.Interaction):
        user_id = int(self.children[0].value)
        user = await self.ctx.guild.fetch_member(user_id)
        role = self.ctx.guild.get_role(self.role_id)
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"Роль {role.name} забрана у пользователя {user.display_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("У пользователя нет этой роли.", ephemeral=True)

class ChangePriceModal(disnake.ui.Modal):
    def __init__(self, ctx, role_id):
        super().__init__(title="Изменить цену роли")

        self.ctx = ctx
        self.role_id = role_id
        self.add_item(disnake.ui.TextInput(label="Новая цена", placeholder="Введите новую цену"))

    async def callback(self, interaction: disnake.Interaction):
        new_price = int(self.children[0].value)
        self.ctx.bot.db.update_role_price(self.role_id, new_price)
        await interaction.response.send_message(f"Цена роли обновлена до {new_price}.", ephemeral=True)

    async def callback(self, interaction: disnake.Interaction):
        new_price = int(self.children[0].value)
        self.ctx.bot.db.update_role_price(self.role_id, new_price)
        await interaction.response.send_message(f"Цена роли обновлена до {new_price}.", ephemeral=True)

class ChangeColorModal(disnake.ui.Modal):
    def __init__(self, ctx, role_id, *args, **kwargs):
        super().__init__("Изменить цвет роли", *args, **kwargs)
        self.ctx = ctx
        self.role_id = role_id
        self.add_item(disnake.ui.TextInput(label="Новый HEX-код цвета", placeholder="Введите HEX-код цвета"))

    async def callback(self, interaction: disnake.Interaction):
        new_color = disnake.Color(int(self.children[0].value, 16))
        role = self.ctx.guild.get_role(self.role_id)
        if role:
            await role.edit(color=new_color)
            await interaction.response.send_message(f"Цвет роли изменен на {new_color}.", ephemeral=True)
        else:
            await interaction.response.send_message("Роль не найдена.", ephemeral=True)

def setup(bot):
    bot.add_cog(RoleManager(bot))