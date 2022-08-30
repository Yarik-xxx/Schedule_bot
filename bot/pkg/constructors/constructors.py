import re

import pkg.templates.variables as var
import datetime


# Преобразует запросы сегодня/завтра в дни недели
def transform_request(request):
    day_week_num = datetime.date.today()  # дата сегодня

    if request == 'завтра':
        day_week_num += datetime.timedelta(days=1)  # дата завтра

    return ["", "пн", "вт", "ср", "чт", "пт", "сб", "вс"][day_week_num.isoweekday()]


# Формирует время занятия в зависимости от предмета (у ФК другое расписание)
def get_lesson_time(number, subject):
    answer = var.BASE_TIMETABLE.get(number, '')
    if re.match(r".*культур\D и спорт.*", subject) is not None:
        answer = var.PHYSICAL_TIMETABLE.get(number, '')

    return answer


# ToDo: объединить с create_schedule_message_week, вынести сообщения в template
# Составление расписания на конкретный день недели с учетом группы
def create_schedule_message(group: str, request: str, schedules: dict):
    # если каким-то образом расписание отсутствует (было после обновления)
    if group not in schedules:
        return "Мы обновили расписание. И кажется, для вашей группы у нас не получилось создать расписание("

    # если нет пар для запрашиваемого дня недели
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


# ToDo: объединить с create_schedule_message, вынести сообщения в template
# Составление расписания на неделю с учетом группы
def create_schedule_message_week(group: str, schedules: dict):
    # если каким-то образом расписание отсутствует (было после обновления)
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
