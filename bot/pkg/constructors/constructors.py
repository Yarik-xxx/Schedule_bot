import re

import pkg.templates.variables as var
import datetime


def transform_request(request):
    """Преобразует запросы 'сегодня' и 'завтра' в дни недели"""
    day_week_num = datetime.date.today()  # дата сегодня

    if request == 'завтра':
        day_week_num += datetime.timedelta(days=1)  # дата завтра

    return ["", "пн", "вт", "ср", "чт", "пт", "сб", "вс"][day_week_num.isoweekday()]


def get_lesson_time(number, subject):
    answer = var.BASE_TIMETABLE.get(number, '')
    if re.match(r".*культур\D и спорт.*", subject) is not None:
        answer = var.PHYSICAL_TIMETABLE.get(number, '')

    return answer


# ToDo: объединить с create_schedule_message_week
def create_schedule_message(group: str, request: str, schedules: dict):
    """Функция составления расписания в ответ на запрос"""

    if group not in schedules:
        return "Мы обновили расписание. И кажется, для вашей группы у нас не получилось создать расписание("

    if request not in schedules[group]:
        return "Пар нет! Можно заняться чем-то другим"

    schedule_day_week = schedules[group][request]  # расписание на день недели с учетом номера группы
    answer = [f"Расписание на {var.DAY_WEEKS_DECLINATION[request]}, группа {group}:\n"]

    # добавление номера пары и предмета
    for key, value in schedule_day_week.items():
        if key.isdigit():
            answer.append(f'• {key} пара ({get_lesson_time(key, value)}) - {value}\n')
        else:
            answer.append(f'• {key} - {value}\n')

    return "".join(answer)


# ToDo: объединить с create_schedule_message
def create_schedule_message_week(group: str, schedules: dict):
    if group not in schedules:
        return "Мы обновили расписание. И кажется, для вашей группы у нас не получилось создать расписание("

    schedule_week = schedules[group]  # расписание группы
    answer = [f"Расписание на неделю, группа {group}:\n"]

    for day_week, schedule_day in schedule_week.items():
        answer.append(f"\nРасписание на {var.DAY_WEEKS_DECLINATION[day_week]}:\n")
        schedule_day_week = schedules[group][day_week]  # расписание на день недели с учетом номера группы

        for key, value in schedule_day_week.items():
            if key.isdigit():
                answer.append(f'• {key} пара ({get_lesson_time(key, value)}) - {value}\n')
            else:
                answer.append(f'• {key} - {value}\n')

    return "".join(answer)
