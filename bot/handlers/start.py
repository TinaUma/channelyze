from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards import categories_keyboard

router = Router()

WELCOME_TEXT = (
    "Привет! Я помогу оформить заказ на астрологическую консультацию ✨\n\n"
    "Выберите категорию услуги:"
)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=categories_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Отправьте /start чтобы оформить заказ.\n"
        "Отправьте /cancel чтобы отменить текущий заказ."
    )
