# SkidkiNezagorami Bot

Telegram- и VK-бот для выдачи промокодов из Google Sheets.

## Требования

- Python 3.11+ или Docker
- Токен Telegram-бота ([@BotFather](https://t.me/BotFather))
- Токен VK-сообщества с Long Poll API
- Google Service Account с доступом к таблице промокодов

## Быстрый старт (локально)

1. Скопируйте пример конфигурации:

```bash
cp .env.example .env
```

2. Заполните `.env` своими значениями.

3. Положите JSON-ключ Google Service Account в `credentials/`:

```bash
mkdir -p credentials
cp /path/to/your-service-account.json credentials/google-service-account.json
```

4. Установите зависимости и запустите:

```bash
pip install -r requirements.txt
python main.py
```

Бот запускает два потока: Telegram (`tg.py`) и VK (`vk.py`).

## Docker

1. Подготовьте `.env` и файл `credentials/google-service-account.json` (см. выше).

2. Соберите и запустите:

```bash
docker compose up -d --build
```

3. Логи:

```bash
docker compose logs -f bot
```

4. Остановка:

```bash
docker compose down
```

## Переменные окружения

| Переменная | Обязательная | Описание |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | да | Токен Telegram-бота |
| `VK_GROUP_TOKEN` | да | Токен VK-сообщества |
| `VK_GROUP_ID` | да | ID VK-сообщества |
| `VK_API_VERSION` | нет | Версия VK API (по умолчанию `5.120`) |
| `GOOGLE_SHEETS_URL` | нет | URL Google-таблицы с промокодами |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | нет | Путь к JSON-ключу Service Account |
| `ADMIN_SECRET` | да | Секрет для админ-команд |
| `TELEGRAM_CHANNEL_USERNAME` | нет | Username канала для проверки подписки |
| `TELEGRAM_CHANNEL_INVITE_URL` | нет | Приватная invite-ссылка на канал |
| `TELEGRAM_CHANNEL_PUBLIC_URL` | нет | Публичная ссылка на канал |

## Админ-команды (Telegram)

Отправьте боту текстовое сообщение:

- `refresh_GS_<ADMIN_SECRET>` — перезагрузить данные из Google Sheets
- `stat_output_<ADMIN_SECRET>` — выгрузить файл статистики
- `stat_refresh_<ADMIN_SECRET>` — очистить статистику

В VK доступна команда `refresh_GS_<ADMIN_SECRET>`.

## Структура проекта

```
.
├── main.py              # Точка входа (Telegram + VK)
├── tg.py                # Telegram-бот
├── vk.py                # VK-бот
├── data_file.py         # Данные промокодов для Telegram
├── vk_data_file.py      # Данные промокодов для VK
├── st.py                # Статистика просмотров
├── config.py            # Загрузка переменных из .env
├── credentials/         # JSON-ключ Google (не коммитить)
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

## Безопасность

- Не коммитьте `.env` и JSON-ключи Google в репозиторий.
- Если токены попали в git — перевыпустите их в BotFather / VK / Google Cloud.
- Меняйте `ADMIN_SECRET` на длинное случайное значение.
