"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '5948668821:AAHTSIhygwPZPAYbjBQwvLV7GCDyuGh1CYc'


signup_button = KeyboardButton(text="Sign Up", callback_data="signup")
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(signup_button)


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def get_photo(user):
    user_photos = await bot.get_user_profile_photos(user)
    user_photos = user_photos.photos
    photos_ids = []
    for photo in user_photos:
        photos_ids.append(photo[0].file_id)
    return photos_ids[0]


async def get_user_info(message):
    id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    photo = await get_photo(id)
    print('Username: ' + username+ ' ID: ' + str(id)  + ' first_name: ' + first_name + ' last_name: '+ last_name + ' PhotoId: '+ photo)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Register now and start enjoying!", reply_markup=keyboard)


@dp.message_handler()
async def kb_answer(message: types.Message):
    if message.text == 'Sign Up':
        await message.answer('Please, enter your Email')
        await get_user_info(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)