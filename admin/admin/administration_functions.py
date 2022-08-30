import datetime
import os
import shutil

import psycopg2
import vk_api

import config
import json


vk_session = vk_api.VkApi(token=config.TOKEN_VK)


# функция отправки сообщения в ВК
def send_message(user_id, text, attachment=None):
    """Функция для отправки сообщения"""
    args = {
        'user_id': user_id,
        'message': text,
        'random_id': 0
    }
    if attachment:
        args['attachment'] = attachment

    vk_session.method('messages.send', args)


# получение ID и номера группы из БД
def query_all():
    # подключение к БД
    conn = psycopg2.connect(**config.db_settings)
    cursor = conn.cursor()

    # получение всех записей
    cursor.execute("SELECT * FROM group_users;")
    res = cursor.fetchall()
    conn.commit()
    cursor.close()

    return res


# сохранение состояния БД в JSON-файл
def backup():
    back_up = query_all()

    print(f"\tГотов. Всего {len(back_up)} пользователей")

    # запись данных в файл
    today = datetime.datetime.now().strftime("%F_%H-%M")
    with open(f"files/db_backup/{today}.json", "w", encoding="utf-8") as write_file:
        json.dump(back_up, write_file, indent=4, ensure_ascii=False)


def dump():
    pass


# загрузка изображения на сервер ВК
def upload_img():
    # Логика выбора загружаемого файла
    images = os.listdir("files/images/new")

    print("\tДоступные файлы для загрузки:")
    for n, name in enumerate(images, start=1):
        print(f"\t\t{n} - {name}")

    try:
        choice = int(input("\tУкажите номер файла: "))
        while choice > len(images) or choice < 1:
            print("\tТакого номера не существует\n")
            choice = int(input("\tУкажите номер файла: "))
    except ValueError:
        print("\tОшибка ввода")
        return

    # Логика загрузки изображения
    vk_session = vk_api.VkApi(token=config.TOKEN_VK)
    vk = vk_session.get_api()

    upload = vk_api.VkUpload(vk)
    photo = upload.photo_messages(f"files/images/new/{images[choice-1]}")  # путь до картинки
    owner_id = photo[0]['owner_id']
    photo_id = photo[0]['id']
    access_key = photo[0]['access_key']
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'

    # Логика пост-обработки файлов
    shutil.move(f"files/images/new/{images[choice-1]}", "files/images/loaded")  # Перенос изображения в папку loaded
    with open("files/images/links_img.csv", "a") as f:  # Запись в csv файл
        f.write(f"{images[choice-1]},{attachment}\n")

    print(f"Ссылка на загруженное изображение: {attachment}")


# просмотр статистики использования бота
def statistic():
    # количество пользователей
    db = query_all()
    print("\t╒ Статистика:")
    print(f"\t╞ {'Количество пользователей':30}| {len(db)}")

    # статистика по группам
    counter_group = {}
    amount_group = set()

    for _, group in db:
        group = group.strip()
        amount_group.add(group)
        counter_group[group] = counter_group.get(group, 0) + 1

    print(f"\t╞ {'Количество отслеживаемых групп':30}| {len(amount_group)}")

    print("\t╘ Статистика по группам:")
    counter_group = sorted(counter_group.items(), key=lambda item: item[1], reverse=True)
    for group, amount in counter_group:
        print(f"\t\t╞ {group:8}| {amount}")


# рассылка сообщения всем пользователям
def mailing_all(text: str):
    result = query_all()
    #result = [(config.DEV_ADMIN,)]

    count_row = len(result)

    for row in result:
        try:
            send_message(row[0], text)
            print(f"\t\t{row[0]} - Отправлено")
        except Exception as err:
            print(f"\t\t{row[0]} - Ошибка {err}")

    print(f"\n\tРассылка завершена. Всего оповещено: {count_row}")


# функция начала рассылки
def mailing():
    while True:
        message = input("\tВведите сообщение для рассылки:")
        send_message(config.DEV_ADMIN, message)

        print("\tСообщение отправлено в тестовом режиме")

        req = input("\tЗапустить рассылку (y - отправить, r - изменить сообщение, s - выход)\n--->")
        if req == "r":
            continue
        elif req == "s":
            break
        elif req == "y":
            mailing_all(message)
            break
        else:
            print("\tНеизвестный ввод. Остановка функции рассылки")
            break



