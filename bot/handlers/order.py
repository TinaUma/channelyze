from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import config
from bot.db import save_order
from bot.keyboards import (
    cancel_keyboard,
    categories_keyboard,
    payment_keyboard,
    service_name_by_slug,
    service_price_by_slug,
    services_keyboard,
)
from bot.states import OrderFlow

router = Router()


# ── Category selection ──────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("cat:"))
async def on_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.removeprefix("cat:")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"Категория: <b>{category}</b>\n\nВыберите услугу:",
        reply_markup=services_keyboard(category),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "back:categories")
async def on_back_categories(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Выберите категорию услуги:",
        reply_markup=categories_keyboard(),
    )
    await callback.answer()


# ── Service selection → start FSM ──────────────────────────────────────────


@router.callback_query(F.data.startswith("svc:"))
async def on_service_selected(callback: CallbackQuery, state: FSMContext) -> None:
    slug = callback.data.removeprefix("svc:")
    name = service_name_by_slug(slug)
    price = service_price_by_slug(slug)

    await state.update_data(service_slug=slug, service_name=name, service_price=price)
    await state.set_state(OrderFlow.waiting_name)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"Вы выбрали: <b>{name}</b>\nСтоимость: {price}\n\n"
        "Как вас зовут? (Введите имя)",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Data collection steps ───────────────────────────────────────────────────


@router.message(OrderFlow.waiting_name)
async def on_name(message: Message, state: FSMContext) -> None:
    await state.update_data(client_name=message.text.strip())
    await state.set_state(OrderFlow.waiting_birth_date)
    await message.answer(
        "Введите дату рождения (например: 15.03.1990)",
        reply_markup=cancel_keyboard(),
    )


@router.message(OrderFlow.waiting_birth_date)
async def on_birth_date(message: Message, state: FSMContext) -> None:
    await state.update_data(birth_date=message.text.strip())
    await state.set_state(OrderFlow.waiting_birth_time)
    await message.answer(
        "Введите время рождения (например: 14:30 или «не знаю»)",
        reply_markup=cancel_keyboard(),
    )


@router.message(OrderFlow.waiting_birth_time)
async def on_birth_time(message: Message, state: FSMContext) -> None:
    await state.update_data(birth_time=message.text.strip())
    await state.set_state(OrderFlow.waiting_birth_place)
    await message.answer(
        "Введите место рождения (город, страна)",
        reply_markup=cancel_keyboard(),
    )


@router.message(OrderFlow.waiting_birth_place)
async def on_birth_place(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    slug = data.get("service_slug", "")
    await state.update_data(birth_place=message.text.strip())
    await state.set_state(OrderFlow.waiting_payment)

    price = data["service_price"]
    wallet = config.YOOMONEY_WALLET

    await message.answer(
        f"Отлично! Последний шаг — оплата.\n\n"
        f"Переведите <b>{price}</b> на ЮMoney:\n"
        f"<code>{wallet}</code>\n\n"
        f"После оплаты пришлите скриншот чека 📎",
        reply_markup=payment_keyboard(slug),
        parse_mode="HTML",
    )


# ── Payment screenshot ──────────────────────────────────────────────────────


@router.message(OrderFlow.waiting_payment, F.photo)
async def on_payment_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    photo_id = message.photo[-1].file_id

    order_id = save_order(
        user_id=message.from_user.id,
        username=message.from_user.username,
        service_name=data["service_name"],
        client_name=data["client_name"],
        birth_date=data["birth_date"],
        birth_time=data["birth_time"],
        birth_place=data["birth_place"],
        payment_screenshot_id=photo_id,
    )

    summary = (
        f"🔔 <b>Новый заказ #{order_id}</b>\n\n"
        f"Услуга: {data['service_name']}\n"
        f"Клиент: {data['client_name']}\n"
        f"Дата рождения: {data['birth_date']}\n"
        f"Время рождения: {data['birth_time']}\n"
        f"Место рождения: {data['birth_place']}\n"
        f"Telegram: @{message.from_user.username or message.from_user.id}"
    )
    await message.bot.send_photo(
        chat_id=config.ORDERS_CHANNEL_ID,
        photo=photo_id,
        caption=summary,
        parse_mode="HTML",
    )

    await state.clear()
    await message.answer(
        "Спасибо! Ваш заказ принят ✨\n\n"
        "Я свяжусь с вами в ближайшее время для подтверждения.\n"
        "Если есть вопросы — напишите напрямую @tina_yuma"
    )


@router.message(OrderFlow.waiting_payment)
async def on_payment_not_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    slug = data.get("service_slug", "")
    await message.answer(
        "Пожалуйста, пришлите именно скриншот (фото) чека оплаты 📎",
        reply_markup=payment_keyboard(slug),
    )


# ── Cancel ──────────────────────────────────────────────────────────────────


@router.callback_query(F.data == "cancel")
async def on_cancel_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "Заказ отменён. Напишите /start чтобы начать заново."
    )
    await callback.answer()


@router.message(Command("cancel"))
async def on_cancel_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Заказ отменён. Напишите /start чтобы начать заново.")
