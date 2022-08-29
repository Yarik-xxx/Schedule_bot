from vkbottle.bot import Bot, Message

import datetime
import logging
import re

import pkg.templates.variables as var
import pkg.handlers as handlers
import pkg.init.init as init
import config


# DEBUG режим
DEBUG = True


# логирование
logging.getLogger("vkbottle").setLevel(logging.INFO)
logging.getLogger("asyncio").setLevel(logging.INFO)
log_update = logging.getLogger("updates")
log_dialogue = logging.getLogger("dialogue")

# настройка часового пояса
offset = datetime.timedelta(hours=5)
tz = datetime.timezone(offset)

# инициализация расписания, пула соединений и пользователей
schedules = init.init_schedule("files/schedule.json")
pool_con = init.init_connections_pool(**config.DB_SETTINGS)
users_group = init.init_users_group(pool_con)
users_states = init.init_user_states(pool_con)

# переменная для работы с ботом
bot = Bot(config.DEBUG_TOKEN if DEBUG else config.TOKEN)


# хендлер на все входящие сообщения
@bot.on.message()
async def handler(message: Message):
    # Проверка режима диалога
    if message.from_id in users_states:
        log_dialogue.info(f"{message.from_id} {message.text}")
        if message.text == "Завершить диалог":
            await handlers.stop_dialogue_admin(message, pool_con, users_states)
        return

    # обработка запросов
    log_update.info(f"{message.from_id} {message.text}")
    text = message.text.lower()

    # запрос расписания на день недели
    if text in var.DAY_WEEKS_LIST:
        await handlers.get_schedule(message, schedules, users_group)
    # запрос типа недели
    elif text == "чис/знам":
        await handlers.numerator_denominator(message)
    # запрос расписания звонков
    elif text == "звонки":
        await handlers.get_calls(message)
    # запрос расписания на всю неделю
    elif text == "неделя":
        await handlers.get_schedule_week(message, schedules, users_group)
    # запрос справки по доступным командам
    elif text == "справка":
        await handlers.get_info(message)
    # запрос на изменения номера группы
    elif re.search(r'^\d{3}-\d{2}[а-яa-z]?$', text):
        await handlers.set_user_group(message, pool_con, schedules, users_group)
    # начало работы с ботом
    elif text == "начать":
        await handlers.start(message)
    # запрос на связь с администратором группы
    elif text == "диалог с администратором группы":
        await handlers.start_dialogue_admin(message, pool_con, bot, users_states)
    # неизвестный запрос
    else:
        await handlers.unknown_request(message)


bot.run_forever()
