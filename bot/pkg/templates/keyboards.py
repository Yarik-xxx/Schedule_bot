from vkbottle import Keyboard, KeyboardButtonColor, Text

KEYBOARD_BASE = (
    Keyboard(one_time=False, inline=False)
    .add(Text("Сегодня"), color=KeyboardButtonColor.SECONDARY)
    .add(Text("Неделя"), color=KeyboardButtonColor.SECONDARY)
    .add(Text("Завтра"), color=KeyboardButtonColor.SECONDARY)
    .row()

    .add(Text("Понедельник"), color=KeyboardButtonColor.SECONDARY)
    .add(Text("Вторник"), color=KeyboardButtonColor.SECONDARY)
    .add(Text("Среда"), color=KeyboardButtonColor.SECONDARY)
    .row()

    .add(Text("Четверг"), color=KeyboardButtonColor.SECONDARY)
    .add(Text("Пятница"), color=KeyboardButtonColor.SECONDARY)
    .add(Text("Суббота"), color=KeyboardButtonColor.SECONDARY)
    .row()

    .add(Text("Звонки"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("Чис/знам"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("Справка"), color=KeyboardButtonColor.POSITIVE)
    .row()

    .add(Text("Диалог с администратором группы"), color=KeyboardButtonColor.NEGATIVE)

    .get_json()
)

KEYBOARD_CONTACT = (
    Keyboard(one_time=False, inline=False)
    .add(Text("Завершить диалог"), color=KeyboardButtonColor.NEGATIVE)
    .get_json()
)
