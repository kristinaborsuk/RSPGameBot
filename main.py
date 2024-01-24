import asyncio
import random
from typing import Dict

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

from game_session import GameSession

TOKEN: str = '6968658953:AAGsbi_0dGfZQyUdN5Sju4R_vjSvWZU3H3g'

dp: Dispatcher = Dispatcher()
bot: Bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
game_sessions_db: Dict[int, GameSession] = {}  # Словник для збереження ігрових сессій для користувачів


def main_menu_keyboard_init() -> types.InlineKeyboardMarkup:
    play_btn = types.InlineKeyboardButton(text='Почати гру', callback_data='play_btn_pressed')
    help_btn = types.InlineKeyboardButton(text='Дізнатись правила', callback_data='help_btn_pressed')
    return types.InlineKeyboardMarkup(inline_keyboard=[[play_btn], [help_btn]])


def game_menu_keyboard_init() -> types.InlineKeyboardMarkup:
    rock_btn = types.InlineKeyboardButton(text='Камінь', callback_data='rock_btn_handler')
    paper_btn = types.InlineKeyboardButton(text='Бумага', callback_data='paper_btn_handler')
    scissors_btn = types.InlineKeyboardButton(text='Ножиці', callback_data='scissors_btn_handler')
    return types.InlineKeyboardMarkup(inline_keyboard=[[rock_btn, paper_btn, scissors_btn]])


def between_round_keyboard_init() -> types.InlineKeyboardMarkup:
    play_btn = types.InlineKeyboardButton(text='Ще один раунд!', callback_data='play_btn_pressed')
    exit_game_btn = types.InlineKeyboardButton(text='Завершити гру та отримати результати',
                                               callback_data='exit_game_btn_handler')
    return types.InlineKeyboardMarkup(inline_keyboard=[[play_btn, exit_game_btn]])


main_keyboard = main_menu_keyboard_init()
game_keyboard = game_menu_keyboard_init()
between_round_keyboard = between_round_keyboard_init()


@dp.message(Command(commands=['start']))
async def start_session(message: types.Message) -> types.Message:
    await message.answer(text='Привіт!\nПропоную тобі зіграти в гру "Камінь - Ножиці - Бумага".\n\n'
                              ' - Для старту натисни кнопку "Почати гру";\n'
                              ' - Якщо бажаєш ознайомитись із правилами гри, натисни кнопку "Дізнатись правила".',
                         reply_markup=main_keyboard)


async def receive_round(user_id: int, users_choice: str, message: types.Message) -> types.Message:
    session = game_sessions_db.get(user_id)
    if session:
        bot_choice = random.choice(session.game_moves)
        round_decision = await session.play_round(bot_choice, users_choice)
        await message.answer(text=f"Твій хід:\n{users_choice.upper()}\n"
                                  f"Мій хід:\n{bot_choice.upper()}\n"
                                  f"{round_decision}",
                             reply_markup=between_round_keyboard)
    else:
        await message.answer(text=f"Ігрову сессію не розпочато! Натисність 'Почати гру'.",
                             reply_markup=main_keyboard)


# Handlers for main keyboard
@dp.callback_query(lambda c: c.data == 'play_btn_pressed')
async def play_btn_handle(callback_query: types.CallbackQuery) -> types.Message:
    user_id = callback_query.from_user.id
    if user_id not in game_sessions_db.keys():
        game_sessions_db[callback_query.from_user.id] = GameSession()

    await bot.send_message(callback_query.from_user.id,
                           text="Роби свій хід!", reply_markup=game_keyboard)


@dp.callback_query(lambda c: c.data == 'help_btn_pressed')
async def help_btn_handle(callback_query: types.CallbackQuery) -> types.Message:
    await bot.send_message(callback_query.from_user.id,
                           text="Єдине правило - перемагає той гравець, який переміг у більшій кількості раундів.")


# Handlers for game keyboard
@dp.callback_query(lambda c: c.data == 'rock_btn_handler')
async def rock_btn_handle(callback_query: types.CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    await receive_round(user_id, 'Камінь', callback_query.message)


@dp.callback_query(lambda c: c.data == 'paper_btn_handler')
async def paper_btn_handle(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await receive_round(user_id, 'Бумага', callback_query.message)


@dp.callback_query(lambda c: c.data == 'scissors_btn_handler')
async def scissors_btn_handle(callback_query: types.CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    await receive_round(user_id, 'Ножиці', callback_query.message)


@dp.callback_query(lambda c: c.data == 'exit_game_btn_handler')
async def exit_game_btn_handle(callback_query: types.CallbackQuery) -> None:
    try:
        session = game_sessions_db.pop(callback_query.from_user.id)
        await callback_query.message.answer(text=await session.show_results(),
                                            reply_markup=main_keyboard)
    except KeyError:
        await callback_query.message.answer(text=f"Ігрову сессію не розпочато! Натисність 'Почати гру'.",
                                            reply_markup=main_keyboard)


# Цю частину коду взято з офіційної документації
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
