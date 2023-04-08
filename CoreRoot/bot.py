import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict
from models.user import User
from pydantic import ValidationError
from register import register

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

form_router = Router()

API_TOKEN = '5948668821:AAHTSIhygwPZPAYbjBQwvLV7GCDyuGh1CYc'

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
        f"Choose a password",
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
        response = await register(user.serialize())
        if(response==201):
            text = "Thanks! Registration is done. Now you can return to site and login."
        else:
            text = response

    except ValidationError as e:
        logging.info("ValidationError %r", e.json())

    await message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove()
    )


async def main():
    bot = Bot(token="5948668821:AAHTSIhygwPZPAYbjBQwvLV7GCDyuGh1CYc", parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())