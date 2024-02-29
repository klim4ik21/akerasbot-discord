import disnake
from disnake.ext import commands
from disnake import TextInputStyle
from logs.log import log_action
from database.db import SQLighter
from config import db_uri

class BanModal(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.member = member
        components = [
            disnake.ui.TextInput(
                label="Время бана",
                placeholder="Введите время в часах",
                custom_id="ban_duration",
                style=TextInputStyle.short,
                max_length=50
            ),
            disnake.ui.TextInput(
                label="Причина бана",
                placeholder="Введите причину бана",
                custom_id="ban_reason",
                style=TextInputStyle.paragraph
            )
        ]
        super().__init__(
            title="Бан пользователя",
            custom_id="ban_user",
            components=components
        )

    async def callback(self, interaction: disnake.ModalInteraction):
        # Логика бана пользователя
        duration = interaction.text_values["ban_duration"]
        reason = interaction.text_values["ban_reason"]
        log_action(f"BAN - время {duration} причина {reason}")
        await interaction.response.send_message(
            f"{self.member.display_name} забанен на {duration} по причине: {reason}",
            ephemeral=True
        )

class GiveModal(disnake.ui.Modal):
    def __init__(self, inter_user: disnake.Member, action_member: disnake.Member):
        self.action_member = action_member
        self.inter_user = inter_user
        components = [
            disnake.ui.TextInput(
                label="Сумма выдачи",
                placeholder="Введите сумму (не больше 10к)",
                custom_id="give_sum",
                style=TextInputStyle.short,
                max_length=50
            ),
            disnake.ui.TextInput(
                label="Причина выдачи",
                placeholder="Введите для чего выдача",
                custom_id="give_reason",
                style=TextInputStyle.paragraph
            )
        ]
        super().__init__(
            title="Выдача монет",
            custom_id="give_user",
            components=components
        )

    async def callback(self, interaction: disnake.ModalInteraction):
        # Логика бана пользователя
        db = SQLighter(db_uri)
        sum = interaction.text_values["give_sum"]
        reason = interaction.text_values["give_reason"]
        if int(sum) <= 10000:
            log_action(f"GIVE - from {self.inter_user.name} сумма {sum} to {self.action_member.name} причина {reason}")
            db.add_balance(self.action_member.id, sum=sum)
            await interaction.response.send_message(
                f"{self.inter_user} выдал {sum} to {self.action_member.name} по причине: {reason}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"{self.inter_user.display_name} ошибка, сумма превышает 10к монет",
                ephemeral=True
            )

class LogsModal(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.member = member
        components = [
            disnake.ui.TextInput(
                label="Действие",
                placeholder="ban, mute, give",
                custom_id="act",
                style=TextInputStyle.short,
                max_length=50
            ),
        ]
        super().__init__(
            title="Logs",
            custom_id="act_logs",
            components=components
        )

    async def callback(self, interaction: disnake.ModalInteraction):
        # Логика бана пользователя
        logs = interaction.text_values["act"]
        log_action(f"GIVE - сумма {sum} причина {logs}")
        await interaction.response.send_message(
            f"{self.member.display_name} выдал {sum} по причине: {logs}",
            ephemeral=True
        )

class AdminView(disnake.ui.View):
    def __init__(self, initiator: disnake.Member, target_member: disnake.Member):
        super().__init__()
        self.initiator_id = initiator.id
        self.target_member = target_member     # Сохраните ID пользователя, который инициировал команду

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        # Проверяем, совпадает ли ID пользователя, взаимодействующего с кнопкой, с ID инициатора команды
        if interaction.user.id != self.initiator_id:
            await interaction.response.send_message("У вас нет прав на использование этих кнопок.", ephemeral=True)
            return False
        return True

    @disnake.ui.button(label="Бан", style=disnake.ButtonStyle.red)
    async def ban_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(BanModal(interaction.user,))

    @disnake.ui.button(label="Выдать", style=disnake.ButtonStyle.blurple)
    async def give_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(GiveModal(inter_user = interaction.user, action_member=self.target_member))

    @disnake.ui.button(label="Варн", style=disnake.ButtonStyle.blurple)
    async def warn(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(GiveModal(interaction.user, self.target_member))

    # Добавьте здесь другие кнопки и соответствующие методы

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="adm", description="Административное меню")
    async def adm(self, inter: disnake.AppCmdInter, target_member: disnake.Member):
        db = SQLighter(db_uri)
        if db.is_admin(inter.user.id) == 1:
            embed = disnake.Embed(title="Управление пользователем", description=f"Выбран пользователь: {target_member.display_name}")
            view = AdminView(inter.user, target_member=target_member)  # Передайте пользователя, который вызвал команду
            await inter.response.send_message(embed=embed, view=view)
        else:
            await inter.response.send_message("у вас нет прав")

def setup(bot):
    bot.add_cog(AdminCog(bot))