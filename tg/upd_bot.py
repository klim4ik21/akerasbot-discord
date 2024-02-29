from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import TG_BOT_TOKEN

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler()
async def greet_everyone(message: types.Message):
    if "/transfer" in message.text or "/coinflip" in message.text or "/profile" in message.text:
        if message.chat.type != "private":
            await message.answer("я не работаю в группах, только личные сообщения")
    if message.chat.type == "private":
        await message.reply("Чтобы я работал в телеграм нужно купить подписку! 299 рублей в месяц\nразработчик устал писать код for free.\nкупить: @xxlv_klim")

if __name__ == '__main__':
    executor.start_polling(dp)