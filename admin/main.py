import admin.administration_functions as admin

info = ("1 - создать резервную копию БД\n"
        "2 - выгрузить резервную копию на сервер\n"
        "3 - загрузить изображение на сервера ВК\n"
        "4 - рассылка сообщения всем пользователям\n"
        "5 - просмотр статистики")

print("Начало работы административного модуля (для прекращения работы введите stop)\n")
print(f"Выберите действие:\n{info}")

req = input("\nКоманда: ").lower()
while req != "stop":
    if req == "1":
        admin.backup()
    elif req == "2":
        pass
    elif req == "3":
        admin.upload_img()
    elif req == "4":
        pass
    elif req == "5":
        admin.statistic()
    else:
        print(f"\nНеизвестная команда. Список команд:\n{info}")

    req = input("\nКоманда: ").lower()
