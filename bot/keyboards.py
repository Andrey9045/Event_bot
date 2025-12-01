from telegram import ReplyKeyboardMarkup, KeyboardButton


# /start
def get_start_menu():
    keyboard = [
        [KeyboardButton("🏠 Меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# МЕНЮ ПОЛЬЗОВАТЕЛЯ
def get_main_menu():
    keyboard = [
        [KeyboardButton("📅 Программа"), KeyboardButton("❓ Задать вопрос")],
        [KeyboardButton("👨‍💼 Текущий докладчик"), KeyboardButton("⭐ Подписка")],
        [KeyboardButton("💝 Поддержать проект")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# МЕНЮ ДОКЛАДЧИКА
def get_speaker_main_menu():
    keyboard = [
        [KeyboardButton("🎤 Панель докладчика"), KeyboardButton("👥 Режим слушателя")],
        [KeyboardButton("📅 Программа")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# МЕНЮ ОРГАНИЗАТОРА
def get_organizer_main_menu():
    keyboard = [
        [KeyboardButton("📢 Сделать рассылку")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ПАНЕЛЬ ДОКЛАДЧИКА
def get_speaker_dashboard_menu():
    keyboard = [
        [KeyboardButton("▶️ Начать выступление")],
        [KeyboardButton("📋 Мои вопросы"), KeyboardButton("🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


#  ПАНЕЛЬ ОРГАНИЗАТОРА
def get_organizer_panel_menu():
    keyboard = [
        [KeyboardButton("👥 Все"), KeyboardButton("🎤 Докладчики")],
        [KeyboardButton("🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_speaker_active_menu():
    keyboard = [
        [KeyboardButton("📋 Мои вопросы")],
        [KeyboardButton("⏹️ Завершить выступление")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_donate_menu():
    keyboard = [
        [KeyboardButton("💰 Donate 100₽"), KeyboardButton("💰 Donate 500₽")],
        [KeyboardButton("💰 Donate 1000₽"), KeyboardButton("🎁 Произвольная сумма")],
        [KeyboardButton("🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_question_input_menu():
    """Клавиатура при вводе вопроса"""
    keyboard = [
        [KeyboardButton("❌ Отменить")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
