# Channelyze — Astrology Bot & Price List

Инструмент для астролога: прайс-лист услуг + Telegram-бот для приёма заказов.

## Что умеет

- **Прайс-лист** — красивая веб-страница со всеми услугами и ценами
- **Telegram-бот** — полный флоу заказа прямо в чате:
  - Выбор категории и услуги
  - Сбор данных клиента (имя, дата/время/место рождения)
  - Кнопка оплаты через ЮMoney (WebView прямо в Telegram)
  - Пересылка заказа с чеком в приватный канал
  - Подтверждение клиенту

## Структура

```
channelyze/
├── bot/                        # Telegram-бот
│   ├── handlers/
│   │   ├── start.py            # /start, /help
│   │   └── order.py            # FSM-флоу заказа
│   ├── config.py               # Настройки из .env
│   ├── db.py                   # SQLite — хранение заказов
│   ├── keyboards.py            # Inline-клавиатуры
│   ├── states.py               # FSM-состояния
│   ├── main.py                 # Точка входа
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── .github/workflows/
│   └── deploy.yml              # CI/CD → VPS через self-hosted runner
├── .env.example                # Шаблон переменных окружения
└── .gitignore
```

## Запуск локально

```bash
cp .env.example .env
# заполни .env своими значениями

cd bot
pip install -r requirements.txt
python -m bot.main
```

## Деплой на VPS

Деплой автоматический: любой push в `bot/**` запускает GitHub Actions.

**Требования:**
- VPS с Docker и Docker Compose
- Self-hosted GitHub Actions runner (зарегистрирован на сервере)
- Секреты в GitHub → Settings → Secrets:
  - `BOT_TOKEN`
  - `ORDERS_CHANNEL_ID`
  - `YOOMONEY_WALLET`

## Переменные окружения

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен бота от @BotFather |
| `ORDERS_CHANNEL_ID` | ID приватного канала для заказов (например: `-1004237588253`) |
| `YOOMONEY_WALLET` | Номер кошелька ЮMoney для приёма оплаты |
| `PROXY_URL` | HTTP-прокси для доступа к Telegram API (опционально) |

## Стек

- [aiogram 3.x](https://docs.aiogram.dev/) — Telegram Bot Framework
- SQLite — хранение заказов
- Docker + GitHub Actions — деплой
