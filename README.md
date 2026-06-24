# Channelyze

**AI-платформа структурирования контента и продаж для онлайн-экспертов.**

Три вложенных инструмента, которые работают как единая воронка:

```
Экспорт Telegram-канала
        ↓
Каталог услуг + PDF-прайс
        ↓
Интерактивная квиз-воронка диагностики клиента
        ↓
Telegram-бот приёма заказов с оплатой через ЮMoney
```

## Что делает каждый инструмент

**1. Парсинг канала** — анализирует экспорт Telegram-канала, выделяет услуги и формирует структурированный каталог

**2. Каталог услуг + PDF-прайс** — веб-страница со всеми услугами и ценами, генерация PDF для отправки клиентам

**3. Квиз-воронка** — интерактивный тест помогает клиенту выбрать подходящую услугу

**4. Telegram-бот** — полный флоу заказа прямо в чате:
- Выбор категории и услуги
- Сбор данных клиента (имя, дата/время/место рождения)
- Оплата через ЮMoney (WebView прямо в Telegram)
- Пересылка заказа с чеком в приватный канал
- Подтверждение клиенту

## Стек

`Python` `aiogram` `React` `SQLite` `Docker` `GitHub Actions`

## Структура

```
channelyze/
├── bot/                        # Telegram-бот (aiogram 3.x, FSM)
│   ├── handlers/
│   │   ├── start.py
│   │   └── order.py
│   ├── config.py               # Настройки из .env
│   ├── db.py                   # SQLite — хранение заказов
│   ├── keyboards.py
│   ├── states.py
│   ├── main.py
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/workflows/
│   └── deploy.yml              # CI/CD → VPS через self-hosted runner
├── .env.example
└── .gitignore
```

## Запуск бота локально

```bash
cp .env.example .env
# заполни .env своими значениями

cd bot
pip install -r requirements.txt
python -m bot.main
```

## Деплой на VPS

Автоматический при пуше в `bot/**` через GitHub Actions.

**Секреты в GitHub → Settings → Secrets:**
- `BOT_TOKEN`
- `ORDERS_CHANNEL_ID`
- `YOOMONEY_WALLET`

## Переменные окружения

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен бота от @BotFather |
| `ORDERS_CHANNEL_ID` | ID приватного канала для заказов |
| `YOOMONEY_WALLET` | Номер кошелька ЮMoney |
| `PROXY_URL` | HTTP-прокси (опционально, для VPS без прямого доступа к Telegram) |
