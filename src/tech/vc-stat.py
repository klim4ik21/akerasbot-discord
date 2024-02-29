import disnake
from disnake.ext import commands, tasks
from database.db import SQLighter
import datetime
from config import db_uri

# It's actually doesn't work i think :)

class VoiceTimeTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_start_times = {}
        self.track_voice_time.start()

    @tasks.loop(seconds=60)  # Запуск каждую минуту
    async def track_voice_time(self):
        await self.bot.wait_until_ready()
        now = datetime.datetime.utcnow()
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.voice and member.voice.channel:
                    user_id = member.id
                    if user_id not in self.voice_start_times:
                        # Если пользователь в голосовом канале и время не установлено, устанавливаем его
                        self.voice_start_times[user_id] = now
                    else:
                        # Если время уже установлено, обновляем общее время
                        self.update_vc_time(user_id, now)

    def update_vc_time(self, user_id, now):
        start_time = self.voice_start_times[user_id]
        vc_time_minutes = (now - start_time).total_seconds() / 60
        if vc_time_minutes > 0:
            self.update_vc_hours(user_id, vc_time_minutes)
            # Обновляем время начала для следующего расчета
            self.voice_start_times[user_id] = now

    def update_vc_hours(self, user_id, vc_time):
        try:
            db = SQLighter(db_uri)
            current_vc_hours = db.get_vc_hours(user_id)
            new_vc_hours = current_vc_hours + vc_time / 60  # Переводим минуты в часы
            db.update_vc_hours(user_id, new_vc_hours)
            db.connection.commit()
            db.connection.close()
        except Exception as e:
            print(f"Error updating VC hours for user {user_id}: {e}")

def setup(bot):
    bot.add_cog(VoiceTimeTracker(bot))
