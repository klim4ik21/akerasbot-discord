import disnake
from disnake.ext import commands
from datetime import datetime
from logs.log import log_action
from database.db import SQLighter
from config import db_uri

ADMIN_ID = 468445928878112793  # ID администратора

class LogsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="logs", description="Поиск логов по имени пользователя, действию и дате")
    async def log(self, inter: disnake.AppCmdInter, username: str, action: str, date: str = "", limit: int = 10):
        db = SQLighter(db_uri)
        isadmin = db.is_admin(inter.author.id)
        """Поиск логов по имени пользователя, действию и дате, доступен только администратору."""
        if isadmin == 0:
            await inter.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return

        log_action(f"CHECKLOG - {inter.author.name} log check")
        log_data = self.find_logs(username, action, date, limit)
        await inter.response.send_message(log_data or "Логи не найдены.", ephemeral=True)

    def find_logs(self, username, action, date, limit):
        """Поиск в файле logs.txt."""
        # Преобразование даты в формат лога
        formatted_date = ""
        if date:
            try:
                formatted_date = datetime.strptime(date, "%d.%m.%y").strftime("%Y-%m-%d")
            except ValueError:
                return "Некорректный формат даты. Используйте ДД.ММ.ГГ"

        try:
            with open("logs.txt", "r") as file:
                logs = file.readlines()
        except FileNotFoundError:
            return "Файл логов не найден."

        filtered_logs = []
        for log in logs:
            if username in log and action in log and (formatted_date in log or not date):
                filtered_logs.append(log)
                if len(filtered_logs) >= limit:
                    break

        return '\n'.join(filtered_logs) if filtered_logs else None

def setup(bot):
    bot.add_cog(LogsCog(bot))
