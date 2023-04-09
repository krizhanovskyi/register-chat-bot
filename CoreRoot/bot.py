import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict
from models.user import User
from pydantic import ValidationError
from register import register, upload_user_profile_photo
from io import BytesIO

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    UserProfilePhotos,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

form_router = Router()

TOKEN = getenv('BOT_TOKEN')
URL = getenv('API_URL')
URL_PHOTO = getenv('URL_PHOTO')

bot = Bot(token=TOKEN, parse_mode="HTML")


class Form(StatesGroup):
    email = State()
    password = State()
    confirm = State()
    language = State()


@form_router.message(Command("start"))
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.email)
    await message.answer(
        "Register now and start enjoying! What's your Email?",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.email)
async def process_email(message: Message, state: FSMContext) -> None:
    #await get_user_info(message)
    await state.update_data(email=message.text)
    print(message.text)
    await state.set_state(Form.password)
    await message.answer(
        f"Choose a password(Minimum of 8 characters)",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.password)
async def process_password(message: Message, state: FSMContext) -> None:
    await state.update_data(password=message.text)
    await state.set_state(Form.confirm)
    await message.answer(
        "Please, confirm a registration",
        reply_markup=ReplyKeyboardMarkup(
        keyboard=[
        [
            KeyboardButton(text="Yes"),
            KeyboardButton(text="No"),
        ]
        ], resize_keyboard=True,
        ),
    )

@form_router.message(Form.confirm, F.text.casefold() == "yes")
async def process_registration_yes(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await message.reply(
        "Registering...",
        reply_markup=ReplyKeyboardRemove(),
    )
    await process_and_show_summary(message=message, data=data)

    
@form_router.message(Form.confirm, F.text.casefold() == "no")
async def process_registration_no(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Not bad not terrible.\nSee you soon.",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Form.confirm)
async def process_unknown_confirm(message: Message, state: FSMContext) -> None:
    await message.reply("I don't understand you :(")
    

async def process_and_show_summary(message: Message, data: Dict[str, Any]) -> None:
    email = data["email"]
    password = data["password"]
    id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    text = ''
    try:
        user = User(email=email, password=password, tg_id=id, tg_user_name=username, tg_first_name=first_name, tg_last_name=last_name, username = username, first_name='None', last_name='None')
        response = await register(url=URL, body=user.serialize())
        if(response==201):
            text = "Thanks! Registration is done. Now you can return to site and login."
        else:
            text = response
    

    except ValidationError as e:
        logging.info("ValidationError %r", e.json())

    await download_user_profile_photo(message)

    await message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove()
    )

async def download_user_profile_photo(message: Message) -> None:
    user_profile_photo: UserProfilePhotos = await message.from_user.get_profile_photos()
    #  upload user profile photo if exists
    if len(user_profile_photo.photos) > 0:
        if len(user_profile_photo.photos[0]) > 0:
                file = await bot.get_file(user_profile_photo.photos[0][0].file_id) 
                result: BytesIO = await bot.download_file(file.file_path)
                await upload_user_profile_photo(URL_PHOTO, result, str(message.from_user.id) + '.png', str(message.from_user.id) )
    else:
            #  if user profile photo not exists then upload user not found pic
            with open('CoreRoot/not_found.png', "rb") as fh:
                buf = BytesIO(fh.read())
            await upload_user_profile_photo(URL_PHOTO, buf, str(message.from_user.id) + '.png', str(message.from_user.id) )
            



async def main():
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())