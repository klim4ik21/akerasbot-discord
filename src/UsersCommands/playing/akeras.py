import disnake
from disnake.ext import commands
import openai

akeras_ai = """
it was here funny prompt to ai pre-generated answer :).
"""
class AkerasCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        openai.api_key = 'openai key'

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if self.bot.user.mentioned_in(message):
            prompt = f"{akeras_ai} как бы ты ответил на'{message.content}'"
            response = self.generate_response(prompt)

            # Отправка ответа
            await message.channel.send(response)

    def generate_response(self, prompt):
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=100
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Ошибка при запросе к OpenAI: {e}")
            return "Извините, я не могу ответить на этот вопрос."

def setup(bot):
    bot.add_cog(AkerasCog(bot))
