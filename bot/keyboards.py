from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

SERVICES: dict[str, list[tuple[str, str]]] = {
    "Самопознание": [
        ("Тройной портрет", "trojnoj-portret"),
        ("Энергетический портрет", "energeticheskij-portret"),
        ("ОСНОВНЫЕ АСПЕКТЫ", "osnovnye-aspekty"),
        ("Разбор натальной карты", "razbor-natalnoj-karty"),
    ],
    "Отношения и партнёрство": [
        ("СИНАСТРИЯ", "sinastriya"),
        ("Астрологический аудит партнёрства", "astrologicheskij-audit-partnyorstva"),
        ("МАЯК (специальный пакет)", "mayak-spetsialnyj-paket"),
    ],
    "Карма и судьба": [
        ("Астро-Детокс", "astro-detoks-rasputyvanie-vetvej-sudby"),
        (
            "Карта Уроков",
            "karta-urokov-astrologicheskij-analiz-povtoryayuschihsya-stsenariev",
        ),
        ("НЕГОРДИЕВ УЗЕЛ", "negordiev-uzel"),
        ("Кармический аудит", "karmicheskij-audit"),
    ],
    "Прогнозы и навигация": [
        ("Расшифровка соляра", "rasshifrovka-solyara"),
        ("Ведический слепок", "vedicheskij-slepok-tvoya-zvyozdnaya-zadacha"),
        ("Ведическая синастрия", "vedicheskaya-sinastriya-karmicheskij-kod-pary"),
    ],
    "Особые запросы": [
        ("Разбор карты ребёнка", "razbor-natalnoj-karty-rebyonka"),
        ("Карма Лап", "karma-lap"),
    ],
}

SERVICE_PRICES: dict[str, str] = {
    "trojnoj-portret": "2 500 ₽",
    "energeticheskij-portret": "3 000 ₽",
    "osnovnye-aspekty": "5 000 ₽",
    "razbor-natalnoj-karty": "8 000 ₽",
    "sinastriya": "10 000 ₽",
    "astrologicheskij-audit-partnyorstva": "7 000 ₽",
    "mayak-spetsialnyj-paket": "10 000 ₽",
    "astro-detoks-rasputyvanie-vetvej-sudby": "10 000 ₽",
    "karta-urokov-astrologicheskij-analiz-povtoryayuschihsya-stsenariev": "по запросу",
    "negordiev-uzel": "3 000 ₽",
    "karmicheskij-audit": "5 000 ₽",
    "rasshifrovka-solyara": "по запросу",
    "vedicheskij-slepok-tvoya-zvyozdnaya-zadacha": "3 500 ₽",
    "vedicheskaya-sinastriya-karmicheskij-kod-pary": "5 500 ₽",
    "razbor-natalnoj-karty-rebyonka": "6 000 ₽",
    "karma-lap": "3 500 ₽",
}


def categories_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=cat, callback_data=f"cat:{cat}")] for cat in SERVICES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def services_keyboard(category: str) -> InlineKeyboardMarkup:
    items = SERVICES.get(category, [])
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"svc:{slug}")]
        for name, slug in items
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="◀ Назад к категориям", callback_data="back:categories"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="cancel")]]
    )


def service_name_by_slug(slug: str) -> str:
    for items in SERVICES.values():
        for name, s in items:
            if s == slug:
                return name
    return slug


def service_price_by_slug(slug: str) -> str:
    return SERVICE_PRICES.get(slug, "по запросу")
