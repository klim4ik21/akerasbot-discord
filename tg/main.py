from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import db_uri, TG_BOT_TOKEN
import random

# Импортируем обновленный класс SQLighter
from updated_db_with_coinflip import SQLighter

# Инициализация бота и диспетчера
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)

# Создание экземпляра подключения к базе данных
db = SQLighter(db_uri)

# Словарь для хранения ставок пользователей
user_bets = {}

@dp.message_handler(commands=['transfer'])
async def transfer(message: types.Message):
    args = message.get_args().split()
    if message.chat.type != "private":
        await message.reply("я не работаю в группах без подписки!")
        return
    if len(args) != 2 or not args[1].isdigit():
        await message.reply("Используйте команду в формате: /transfer @username <amount>")
        return

    recipient_id = None
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention":
                recipient_id = entity.user.id
                break

    if not recipient_id:
        await message.reply("Не удалось определить пользователя для перевода.")
        return

    amount = int(args[1])

    sender_id = str(message.from_user.id)
    sender_discord_id = db.get_discord_id_by_tg_id(sender_id)

    # Получение Discord ID получателя по его Telegram ID
    recipient_discord_id = db.get_discord_id_by_tg_id(str(recipient_id))

    if sender_discord_id and recipient_discord_id:
        sender_balance = db.get_bal(sender_discord_id)
        if sender_balance < amount:
            await message.reply("Недостаточно средств для перевода.")
            return

        db.minus_balance(sender_discord_id, amount)
        db.add_balance(recipient_discord_id, amount)

        await message.reply(f"Переведено {amount} монет пользователю с Telegram ID {recipient_id}.")
    else:
        await message.reply("Не удалось найти аккаунты для перевода.")


# Команда /profile
@dp.message_handler(commands=['profile'])
async def profile(message: types.Message):
    if message.chat.type != "private":
        await message.reply("я не работаю в группах без подписки!")
        return
    tg_id = str(message.from_user.id)
    discord_id = db.get_discord_id_by_tg_id(tg_id)

    if discord_id:
        profile_data = db.get_profile_data(discord_id)
        response_message = f"Профиль пользователя {message.from_user.full_name}:\nкоинов: {profile_data}"
        await message.reply(response_message)
    else:
        await message.reply("Telegram ID не связан с учетной записью Discord.")

# Команда /coinflip
@dp.message_handler(commands=['coinflip'])
async def coinflip(message: types.Message):
    if message.chat.type != "private":
        await message.reply("я не работаю в группах без подписки!")
        return
    args = message.get_args().split()
    if not args or not args[0].isdigit():
        await message.reply("Пожалуйста, укажите сумму ставки. Например: /coinflip 100")
        return

    bet_amount = int(args[0])
    user_bets[message.from_user.id] = bet_amount  # Сохраняем ставку

    tg_id = str(message.from_user.id)
    discord_id = db.get_discord_id_by_tg_id(tg_id)

    if discord_id:
        user_balance = db.get_bal(user_id=discord_id)
        if user_balance < bet_amount:
            await message.reply("У вас недостаточно средств для этой ставки.")
            return


        keyboard = InlineKeyboardMarkup()
        button_heads = InlineKeyboardButton("Heads", callback_data="heads")
        button_tails = InlineKeyboardButton("Tails", callback_data="tails")
        keyboard.add(button_heads, button_tails)

        await message.reply("Выберите сторону монеты:", reply_markup=keyboard)
    else:
        await message.reply("Telegram ID не связан с учетной записью Discord.")

@dp.callback_query_handler(lambda c: c.data in ["heads", "tails"])
async def coinflip_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id in user_bets:
        if callback_query.message.reply_to_message.from_user.id != user_id:
            await callback_query.answer("Вы не можете играть в эту игру за другого пользователя.", show_alert=True)
            return

        bet_amount = user_bets[user_id]  # Получаем ставку
        del user_bets[user_id]  # Удаляем ставку из словаря

        discord_id = db.get_discord_id_by_tg_id(str(user_id))
        if discord_id:
            result = random.choice(["Heads", "Tails"])
            winnings = 0
            outcome = "Lose"

            if callback_query.data == result:
                winnings = bet_amount
                db.add_balance(user_id=discord_id, sum=winnings)
                outcome = "Won"
            else:
                db.minus_balance(user_id=discord_id, sum=bet_amount)

            await callback_query.message.edit_text(f"Результат: {outcome} | Монета упала на {result}, Выигрыш: {winnings} монет")
        else:
            await callback_query.answer("Произошла ошибка: не найден Discord ID", show_alert=True)
    else:
        await callback_query.answer("Ставка не найдена", show_alert=True)

if __name__ == '__main__':
    executor.start_polling(dp)
