import datetime

import psycopg2
from psycopg2 import pool

import config
import pkg.templates.messages as tmp
import pkg.templates.keyboards as brd
import pkg.templates.variables as var
import pkg.constructors.constructors as cnstr

from vkbottle.bot import Message, Bot


async def get_calls(message: Message):
    await message.answer(tmp.schedule_calls, keyboard=brd.KEYBOARD_BASE)


async def get_info(message: Message):
    await message.answer(tmp.info_messages, keyboard=brd.KEYBOARD_BASE)


async def start(message: Message):
    await message.answer(tmp.hello_messages, keyboard=brd.KEYBOARD_BASE)


async def unknown_request(message: Message):
    await message.answer(tmp.unknown_request, keyboard=brd.KEYBOARD_BASE)


async def numerator_denominator(message: Message):
    num_or_den = int(datetime.date.today().strftime("%V")) % 2
    await message.answer(f"\nУчимся по {'числителю' if num_or_den else 'знаменателю'}", keyboard=brd.KEYBOARD_BASE)


async def get_schedule(message: Message, schedules: dict, users_group: dict):
    request = var.DAY_WEEKS_DICT.get(message.text.lower(), message.text.lower())  # вернется сокращенный день недели

    if request in ["сегодня", "завтра"]:
        request = cnstr.transform_request(request)

    if request == "вс":
        await message.answer(tmp.sunday, keyboard=brd.KEYBOARD_BASE)
        return

    group = users_group.get(message.from_id)

    if not group:
        await message.answer(tmp.not_group_user)
        return

    answer = cnstr.create_schedule_message(group, request, schedules)
    await message.answer(answer, keyboard=brd.KEYBOARD_BASE)


async def get_schedule_week(message: Message, schedules: dict, users_group: dict):
    group = users_group.get(message.from_id)

    if not group:
        await message.answer(tmp.not_group_user)
        return

    answer = cnstr.create_schedule_message_week(group, schedules)
    await message.answer(answer, keyboard=brd.KEYBOARD_BASE)


async def set_user_group(message: Message, pool_connections: psycopg2.pool, schedules: dict, users_group: dict):
    group = message.text.lower()

    if group not in schedules:
        await message.answer(f"Группы {group} нет в моей базе", keyboard=brd.KEYBOARD_BASE)
        return

    if group == users_group.get(message.from_id, ""):
        await message.answer(f"Вы уже состоите в группе {group}", keyboard=brd.KEYBOARD_BASE)
        return

    try:
        connection = pool_connections.getconn()
        cursor = connection.cursor()

        answer = f"Номер группы успешно изменен на {group}"
        if message.from_id in users_group:
            cursor.execute("UPDATE group_users SET number_group=%s WHERE id=%s;", (group, message.from_id))
        else:
            cursor.execute("INSERT INTO group_users (id, number_group) VALUES (%s, %s);", (message.from_id, group))
            answer = "Я запомнил твою группу"

        cursor.close()
        pool_connections.putconn(connection)

        await message.answer(answer, keyboard=brd.KEYBOARD_BASE)

        users_group[message.from_id] = group

    except:
        await message.answer(tmp.error_update_group, keyboard=brd.KEYBOARD_BASE)


async def start_dialogue_admin(message: Message, pool_connections: psycopg2.pool, bot: Bot, users_states: dict):
    try:
        connection = pool_connections.getconn()
        cursor = connection.cursor()

        cursor.execute("INSERT INTO states (user_id) VALUES (%s)", (message.from_id,))

        cursor.close()
        pool_connections.putconn(connection)

        await message.answer(tmp.contact_administrator, keyboard=brd.KEYBOARD_CONTACT)

        users_states[message.from_id] = None

        # оповестить админов группы
        text = f"Поступил запрос на связь с администратором. Ссылка на профиль: https://vk.com/id{message.from_id}"
        for admin_id in config.IDS_ADMINS:
            try:
                await bot.api.messages.send(peer_id=admin_id, message=text, random_id=0)
            except:
                continue

    except:
        await message.answer(tmp.error_start_dialogue, keyboard=brd.KEYBOARD_BASE)


async def stop_dialogue_admin(message: Message, pool_connections: psycopg2.pool, users_states: dict):
    try:
        connection = pool_connections.getconn()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM states WHERE user_id=%s", (message.from_id,))

        cursor.close()
        pool_connections.putconn(connection)

        users_states.pop(message.from_id, None)

        await message.answer(tmp.finish_dialogue, keyboard=brd.KEYBOARD_BASE)


    except:
        await message.answer(tmp.error_stop_dialogue, keyboard=brd.KEYBOARD_CONTACT)


