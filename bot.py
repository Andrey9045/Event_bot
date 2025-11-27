import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
from keyboards import get_main_menu, get_speaker_main_menu, get_organizer_main_menu, get_speaker_dashboard_menu, get_organizer_panel_menu, get_speaker_active_menu, get_donate_menu


user_roles = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_user_role(user_id):
    return user_roles.get(user_id, "user")


def set_role_speaker(update, context):
    user_id = update.effective_user.id
    user_roles[user_id] = "speaker"
    update.message.reply_text(
        "Теперь вы в роли ДОКЛАДЧИКА!",
        reply_markup=get_speaker_main_menu()
    )

def set_role_organizer(update, context):
    user_id = update.effective_user.id
    user_roles[user_id] = "organizer"
    update.message.reply_text(
        "Теперь вы в роли ОРГАНИЗАТОРА!",
        reply_markup=get_organizer_main_menu()
    )


def set_role_user(update, context):
    user_id = update.effective_user.id
    user_roles[user_id] = "user"
    update.message.reply_text(
        "Теперь вы в роли ПОЛЬЗОВАТЕЛЯ!",
        reply_markup=get_main_menu()
    )


def start(update, context):
    user = update.effective_user
    user_id = user.id
    role = get_user_role(user_id)
    welcome_text = f"""Привет, {user.first_name}! 👋

Я бот для митапов 🤖"""
    if role == "speaker":
        update.message.reply_text(welcome_text, reply_markup=get_speaker_main_menu())
    elif role == "organizer":
        update.message.reply_text(welcome_text, reply_markup=get_organizer_main_menu())
    else:   
        update.message.reply_text(welcome_text, reply_markup=get_main_menu())

def handle_buttons(update, context):
    user_id = update.effective_user.id
    text = update.message.text
    role = get_user_role(user_id)
    print(f"🔘 Пользователь нажал: {text}")
    #РЕЖИМ ЮЗЕРА
    if role == "user":
        if text == "📅 Программа":
            update.message.reply_text("🗓 Здесь будет программа мероприятия!")
        elif text == "❓ Задать вопрос":
            update.message.reply_text("❔ Здесь можно будет задать вопрос докладчику!")
        elif text == "👨‍💼 Текущий докладчик":
            update.message.reply_text("🎤 Сейчас выступает: Тестовый докладчик")
        elif text == "⭐ Подписаться":
            update.message.reply_text("✅ Вы подписались на обновления!")
        elif text == "💝 Поддержать проект":
            update.message.reply_text(
                "💝 Поддержать развитие наших митапов!\n\n"
                "Выберите сумму доната:",
                reply_markup=get_donate_menu()
            )
        if text == "💰 Donate 100₽":
            update.message.reply_text("💳 Для доната 100₽ используйте: ...\nСпасибо за поддержку! ❤️")
        elif text == "💰 Donate 500₽":
            update.message.reply_text("💳 Для доната 500₽ используйте: ...\nСпасибо за поддержку! ❤️")
        elif text == "💰 Donate 1000₽":
            update.message.reply_text("💳 Для доната 1000₽ используйте: ...\nСпасибо за поддержку! ❤️")
        elif text == "🎁 Произвольная сумма":
            update.message.reply_text("💳 Для произвольной суммы используйте: ...\nЛюбая сумма поможет нашему сообществу! ❤️")
        elif text == "🏠 Главное меню":
        	update.message.reply_text("🏠 Главное меню", reply_markup=get_main_menu())

    # HT:BV CGBRTHF
    elif role =="speaker":
        if text == "🎤 Панель докладчика":
            update.message.reply_text(
                "🎤 Панель докладчика\n\nУправление выступлением:",
                reply_markup=get_speaker_dashboard_menu()
            )
        elif text == "👥 Режим слушателя":
            user_roles[user_id] = "user"
            update.message.reply_text(
                "🔁 Переключились в режим слушателя!", 
                reply_markup=get_main_menu()
            )
        elif text == "📅 Программа":
            update.message.reply_text("Программа")
        elif text == "▶️ Начать выступление":
            update.message.reply_text(
                "🎤 Вы начали выступление!\n\n"
                "Теперь слушатели могут задавать вам вопросы.",
                reply_markup=get_speaker_active_menu()
            )
        elif text == "⏹️ Завершить выступление":
             update.message.reply_text(
                "⏹️ Выступление завершено!\n"
                "Вы вернулись в панель докладчика.",
                reply_markup=get_speaker_dashboard_menu()  # ← Возвращаем обычную панель
            )
        elif text == "📋 Мои вопросы":
            update.message.reply_text("❓ Здесь будут вопросы от слушателей")
        elif text == "🏠 Главное меню":
            update.message.reply_text("🏠 Главное меню", reply_markup=get_speaker_main_menu())
    #РЕЖИМ ОРГАНИЗАТОРА
    elif role == "organizer":
        if text == "👥 Добавить докладчика":
            update.message.reply_text("➕ Здесь можно добавить докладчика")
        elif text == "📅 Изменить программу":
            update.message.reply_text(
                "📅 Редактирование программы:",
                reply_markup=get_organizer_panel_menu()
            )
        elif text == "📢 Сделать рассылку":
            update.message.reply_text("📢 Здесь будет массовая рассылка")
        elif text == "➕ Добавить доклад":
            update.message.reply_text("➕ Добавление нового доклада")
        elif text == "✏️ Изменить доклад":
            update.message.reply_text("✏️ Изменение доклада")
        elif text == "🗑️ Удалить доклад":
            update.message.reply_text("🗑️ Удаление доклада")
        elif text == "🏠 Главное меню":
            update.message.reply_text("🏠 Главное меню", reply_markup=get_organizer_main_menu())

def main():
    load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    updater = Updater(BOT_TOKEN, use_context=True)
    dp=updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("speaker", set_role_speaker))
    dp.add_handler(CommandHandler("organizer", set_role_organizer))
    dp.add_handler(CommandHandler("user", set_role_user))
    dp.add_handler(MessageHandler(Filters.text, handle_buttons))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
	main()