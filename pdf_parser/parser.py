import json
import os
import pprint
import re
import pdfplumber


# хранение ошибок возникших в ходе программы
ignore = {
    "error_group": [],
    "error_start_index": [],
    "english_version": []
}

# списки для определения нового дня недели
day_week_list = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ",
                 "пн", "вт", "ср", "чт", "пт", "сб"]

day_week_list_eng = ["MON", "TUE", "WED", "THU", "FRI", "SAT",
                     "mon", "tue", "web", "thu", "fri", "sat"]

# переменная для итогового расписания
schedule_json = {}

# изменения в сравнении с предыдущим расписанием
differences = {}


# get_all_path_schedule составляет список относительных путей до файлов с расписанием занятий
def get_all_path_schedule(name_directory: str):
    name_files = os.listdir(name_directory)
    return [os.path.join(name_directory, name) for name in name_files]


# get_number_group определяет номер группы
def get_number_group(table: list, path: str, number: int):
    # Очень много вложенных конструкций для определения номера группы
    for row in table:
        for cell in row:
            if cell:
                group = re.findall(r'\s\d{3}-\d{2}[а-яА-яAA-Za-z]?', cell)
                if group:
                    return group[0][1:]

    # Если дошло до этой строки, то группа не найдена
    print(f"Файл {path}, страница {number + 1}... Не удалось определить группу")

    group = input("Введите номер группы (для пропуска нажмите ENTER): ")
    if group:
        return group

    # Если оператор не смог найти группу
    ignore["error_group"].append(table)


# get_start_index определяет строку начала расписания
def get_start_index(table: list):
    for idx, row in enumerate(table):
        if "ПН" in row:
            return idx
        if "MON" in row:
            ignore["english_version"].append(table)
            return

    # Если дошло до этой строки, то не получилось узнать начало расписания
    ignore["error_start_index"].append(table)


# line_cleaning очищает сроку от нулевых значений
def line_cleaning(row: list):
    while None in row:
        row.remove(None)

    while "" in row:
        row.remove("")

    if len(row) == 1 and row[0] not in day_week_list:
        return

    for idx, cell in enumerate(row):
        cell = cell.replace("\n", " ")

        while "  " in cell:
            cell = cell.replace("  ", " ")

        cell = cell.replace("п/г ", "п/г")

        row[idx] = cell

    return row


# formation_schedule формирует расписание в словаре
def formation_schedule(group, start_index, table):
    schedule_json[group] = {}
    day_week = ""

    for row in table[start_index:]:
        # Очистка строки
        row = line_cleaning(row)

        if not row:
            continue

        # Обновление дня недели
        for dw in day_week_list:
            if dw in row:
                day_week = dw.lower()  # day_week будет создан в самом начале, так как найдена стартовая строка
                row.remove(dw)
                schedule_json[group][day_week] = {}
                break

        # Пропуск строк типа: ["1"] (появляются после row.remove(dw))
        if len(row) <= 1:
            continue

        # Могут возникнуть проблемы с JSON если первый индекс не будет означать номер пары
        # Если появились трудности, то напечатать row, чтобы проверить ключи-номера пар

        # Запись в словарь
        lesson_number = row[0]
        schedule_json[group][day_week][lesson_number] = " | ".join(row[1:])  # Добавление с разделением на подгруппы


# print_ignore выводит возникшие ошибки
def print_ignore():
    message = ""
    for key, val in ignore.items():
        if not val:
            continue
        message += key
        for tab in val:
            message += "\t" + str(tab)

    if not message:
        print(None)
    else:
        print(message)


# file_comparison сравнивает новое расписание с предыдущей версией
def file_comparison():
    with open("schedule.json", "r", encoding="utf-8") as read_file:
        schedules_old = json.load(read_file)

    # перечень всех групп
    groups = set(schedules_old).union(set(schedule_json))

    # сравнение расписания
    for g in groups:
        old = schedules_old.get(g, {})
        new = schedule_json.get(g, {})
        if old != new:
            differences[g] = {}
            differences[g]["old"] = old
            differences[g]["new"] = new


# print_differences печатает изменения в расписании
def print_differences():
    for dif, schedule_dif in differences.items():
        print(f"Группа {dif}:")
        print(f"{'_' * 10}Старая версия{'_' * 10}")
        pprint.pprint(schedule_dif["old"])
        print(f"{'_' * 10}Новая версия{'_' * 10}")
        pprint.pprint(schedule_dif["new"])
        print("\n", "_______" * 10)


# parse_schedules собирает все функции сбора расписания
def parse_schedules():
    for path in get_all_path_schedule("schedule_group"):
        file = pdfplumber.open(path)
        for number in range(len(file.pages)):
            # Получение таблиц с каждой страницы
            table = file.pages[number].extract_table()

            # Определение номера группы и стартовой строки
            group = get_number_group(table, path, number)
            start_index = get_start_index(table)

            if not group or not start_index:
                continue

            # Формирование расписания
            print(f"Создание расписания группы №{group}")
            formation_schedule(group, start_index, table)


if __name__ == "__main__":
    # получение расписания
    parse_schedules()
    print(f"Расписание составлено (всего: {len(schedule_json)} групп)")

    # вывод возникших ошибок
    print("Полученные ошибки: ")
    print_ignore()

    # сравнение нового и старого расписания
    file_comparison()
    print(f"Всего изменений: {len(differences)}")

    pr_dif = input("Вывести изменения (y/n): ")
    if pr_dif == "y":
        print_differences()

    # сохранение изменений
    save = input("\nСохранить расписание [y/n]: ")
    if save == "y":
        with open(f"schedule.json", "w", encoding="utf-8") as write_file:
            json.dump(schedule_json, write_file, indent=2, ensure_ascii=False)
