"""Модуль обработчиков. Вызываются из основного файла bot.py"""

import datetime

import psycopg2
from psycopg2 import pool
from vkbottle.bot import Message, Bot

import config
import pkg.templates.messages as tmp
import pkg.templates.keyboards as brd
import pkg.templates.variables as var
import pkg.constructors.constructors as cnstr


# расписание звонков
async def get_calls(message: Message):
    await message.answer(tmp.schedule_calls, keyboard=brd.KEYBOARD_BASE)


# информация о доступных командах бота
async def get_info(message: Message):
    await message.answer(tmp.info_messages, keyboard=brd.KEYBOARD_BASE)


# приветственное сообщение ToDo: сделать персональное обращение
async def start(message: Message):
    await message.answer(tmp.hello_messages, keyboard=brd.KEYBOARD_BASE)


# неизвестный запрос
async def unknown_request(message: Message):
    await message.answer(tmp.unknown_request, keyboard=brd.KEYBOARD_BASE)


# вывод типа недели: числитель, знаменатель
async def numerator_denominator(message: Message):
    num_or_den = int(datetime.date.today().strftime("%V")) % 2
    await message.answer(f"\nУчимся по {'числителю' if num_or_den else 'знаменателю'}", keyboard=brd.KEYBOARD_BASE)


# запрос расписания на конкретный день недели
async def get_schedule(message: Message, schedules: dict, users_group: dict):
    request = var.DAY_WEEKS_DICT.get(message.text.lower(), message.text.lower())  # вернется сокращенный день недели

    # преобразование сегодня/завтра в день недели
    if request in ["сегодня", "завтра"]:
        request = cnstr.transform_request(request)

    # проверка запроса на воскресенье
    if request == "вс":
        await message.answer(tmp.sunday, keyboard=brd.KEYBOARD_BASE)
        return

    # получение номера группы пользователя
    group = users_group.get(message.from_id)

    if not group:
        await message.answer(tmp.not_group_user)
        return

    # генерация и отправка расписания
    answer = cnstr.create_schedule_message(group, request, schedules)
    await message.answer(answer, keyboard=brd.KEYBOARD_BASE)


# запрос расписания на всю неделю
async def get_schedule_week(message: Message, schedules: dict, users_group: dict):
    # получение номера группы
    group = users_group.get(message.from_id)

    if not group:
        await message.answer(tmp.not_group_user)
        return

    # генерация и отправка расписания на всю неделю
    answer = cnstr.create_schedule_message_week(group, schedules)
    await message.answer(answer, keyboard=brd.KEYBOARD_BASE)


# изменение/установка номера группы
async def set_user_group(message: Message, pool_connections: psycopg2.pool, schedules: dict, users_group: dict):
    group = message.text.lower()

    # проверка наличия номера группы в файле с расписанием
    if group not in schedules:
        await message.answer(f"Группы {group} нет в моей базе", keyboard=brd.KEYBOARD_BASE)
        return

    # проверка на наличие изменений
    if group == users_group.get(message.from_id, ""):
        await message.answer(f"Вы уже состоите в группе {group}", keyboard=brd.KEYBOARD_BASE)
        return

    try:
        # изменение номера группы
        connection = pool_connections.getconn()
        cursor = connection.cursor()

        answer = f"Номер группы успешно изменен на {group}"

        # обновление номера группы
        if message.from_id in users_group:
            cursor.execute("UPDATE group_users SET number_group=%s WHERE id=%s;", (group, message.from_id))
        # установка номера группы
        else:
            cursor.execute("INSERT INTO group_users (id, number_group) VALUES (%s, %s);", (message.from_id, group))
            answer = "Я запомнил твою группу"

        # закрытие соединения, возврат его в пул, сохранение изменений
        cursor.close()
        connection.commit()
        pool_connections.putconn(connection)

        await message.answer(answer, keyboard=brd.KEYBOARD_BASE)

        # изменение номера группы в оперативной памяти
        users_group[message.from_id] = group

    except:
        await message.answer(tmp.error_update_group, keyboard=brd.KEYBOARD_BASE)


# запрос на связь с администраторами группы
async def start_dialogue_admin(message: Message, pool_connections: psycopg2.pool, bot: Bot, users_states: dict):
    try:
        connection = pool_connections.getconn()
        cursor = connection.cursor()

        # изменение состояния пользователя в БД
        cursor.execute("INSERT INTO states (user_id) VALUES (%s)", (message.from_id,))

        # закрытие соединения, возврат его в пул, сохранение изменений
        cursor.close()
        connection.commit()
        pool_connections.putconn(connection)

        await message.answer(tmp.contact_administrator, keyboard=brd.KEYBOARD_CONTACT)

        # изменение состояния пользователя в оперативной памяти
        users_states[message.from_id] = None

        # оповещение администраторов группы
        text = f"Поступил запрос на связь с администратором. Ссылка на профиль: https://vk.com/id{message.from_id}"
        for admin_id in config.IDS_ADMINS:
            try:
                await bot.api.messages.send(peer_id=admin_id, message=text, random_id=0)
            except:
                continue

    except:
        await message.answer(tmp.error_start_dialogue, keyboard=brd.KEYBOARD_BASE)


# остановка диалога с администраторами группы
async def stop_dialogue_admin(message: Message, pool_connections: psycopg2.pool, users_states: dict):
    try:
        connection = pool_connections.getconn()
        cursor = connection.cursor()

        # изменение состояния пользователя в БД
        cursor.execute("DELETE FROM states WHERE user_id=%s", (message.from_id,))

        # закрытие соединения, возврат его в пул, сохранение изменений
        cursor.close()
        connection.commit()
        pool_connections.putconn(connection)

        # изменение состояния пользователя в оперативной памяти
        users_states.pop(message.from_id, None)

        await message.answer(tmp.finish_dialogue, keyboard=brd.KEYBOARD_BASE)


    except:
        await message.answer(tmp.error_stop_dialogue, keyboard=brd.KEYBOARD_CONTACT)


