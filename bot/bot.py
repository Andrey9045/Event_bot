import os
import logging
import telegram
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv
from keyboards import get_start_menu, get_main_menu, get_speaker_main_menu, get_organizer_main_menu, get_speaker_dashboard_menu, get_organizer_panel_menu, get_speaker_active_menu, get_donate_menu, get_question_input_menu, get_news_distribution_menu
from database import get_event_program, create_question_for_current_speaker, is_talk_active, toggle_subscription, get_questions_list, get_current_speaker
from datacenter.models import User, Event, Newsletter, Talk

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
user_roles = {}
user_states = {}
STATE_WAITING_MESSAGE = "waiting_message"
STATE_WAITING_QUESTION = "waiting_question"
FIRST, SECOND = range(2)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_user_role(user_id):
    return user_roles.get(user_id)


def set_user_state(user_id, state):
    user_states[user_id] = state


def get_user_state(user_id):
    return user_states.get(user_id)


def clear_user_state(user_id):
    if user_id in user_states:
        del user_states[user_id]


def set_role_speaker(update, context):
    user_id = update.effective_user.id
    user_roles[user_id] = "speaker"


def set_role_organizer(update, context):
    user_id = update.effective_user.id
    user_roles[user_id] = "organizer"


def set_role_user(update, context):
    user_id = update.effective_user.id
    user_roles[user_id] = "user"


def clear_role(user_id):
    if user_id in user_roles:
        del user_roles[user_id]


def start(update, context):
    user = update.effective_user
    user_id = user.id
    username = f"{user.first_name} {user.last_name}"
    if not User.objects.filter(chat_id=user_id).exists():
        User.objects.create(chat_id=user_id, nickname=username)

    welcome_text = f"""Привет, {user.first_name}! 👋
Я бот для митапов 🤖
С моей помощью вы сможете посмотреть программу мероприятия и задать вопрос ведущему\n
Чтобы открыть меню нажми на кнопку 🏠 Меню или воспользуйся командой /menu"""
    update.message.reply_text(welcome_text, reply_markup=get_start_menu())


def menu(update, context):
    user = update.effective_user
    user_id = user.id
    role = User.objects.get(chat_id=user_id).role
    role = str(role)
    if role == "Докладчик":
        update.message.reply_text("Переходим в меню докладчика", reply_markup=get_speaker_main_menu())
    if role == "Администратор":
        update.message.reply_text("Переходим в меню администратора", reply_markup=get_organizer_main_menu())
    if role == "Пользователь":
        update.message.reply_text("Переходим в главное меню", reply_markup=get_main_menu())


def show_program(update, context):
    event, talks = get_event_program()
    if event and talks:
        program_text = f"📅{event.title}\n\n"
        program_text += f"📖 {event.description}\n\n"
        program_text += f"🗓 {event.date.strftime('%d.%m.%Y в %H:%M')}\n\n"
        program_text += "🎤 Программа выступлений:\n\n"

        for talk in talks:
            program_text += f"{talk.queue}. {talk.title}\n"
            program_text += f"👤 {talk.speaker}\n"
            program_text += f"⏰ {talk.started_at.strftime('%H:%M') if talk.started_at else 'Время уточняется'}\n"
            program_text += f"📝 {talk.description}\n\n"
        update.message.reply_text(program_text)
    else:
        update.message.reply_text(
            "📅 На данный момент нет активных мероприятий.\n\n"
            "Следите за анонсами!"
        )


def create_newsletter_message(event):
    list = ""
    for index, talk in enumerate(event.talks.all(), start=1):
        list += f"{index}. {talk.title} — {talk.speaker}\n\n"
    message = f"""Здравствуйте,
Приглашаем вас принять участие в новом мероприятии {event.title}
Который будет проходить {event.date.date()} с {event.date.time()}\n
{event.description}
В программе мероприятия:\n
{list}
Будем рады видеть вас среди участников!
    """
    return message


def newsletter(update, context):
    update.message.reply_text("Введите id мероприятия по которому хотите сделать рассылку")
    return FIRST


def newsletter_first_response(update, context):
    id = update.message.text
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        update.message.reply_text("Мероприятия с таким id не существует")
        return ConversationHandler.END
    update.message.reply_text(f"Вы выбрали мероприятие: \n\n{event.title}", reply_markup=get_news_distribution_menu())
    newsletter = Newsletter(id=1, event_id=id)
    newsletter.save()
    return SECOND


def newsletter_second_response(update, context):
    answer = update.message.text
    if answer == "✅ Подтвердить":
        users = User.objects.filter(subscription=True)
        event = Newsletter.objects.get(id=1).event
        for user in users:
            bot = telegram.Bot(token=BOT_TOKEN)
            try:
                with open(f'media/{str(event.image)}', 'rb') as image:
                    bot.send_photo(
                        chat_id=user.chat_id,
                        photo=image,
                        caption=create_newsletter_message(event),
                        )
            except ValueError:
                bot.send_message(
                    chat_id=user.chat_id,
                    text=create_newsletter_message(event)
                )
            except PermissionError:
                try:
                    bot.send_message(
                        chat_id=user.chat_id,
                        text=create_newsletter_message(event)
                    )
                except telegram.error.BadRequest as e:
                    print(e)
                    continue
            except telegram.error.BadRequest as e:
                print(e)
                continue
        update.message.reply_text("Сообщения отправлены.\nВозвращаемся в главное меню", reply_markup=get_organizer_main_menu())
    if answer == "❌ Отменить":
        update.message.reply_text("Возвращаемся в главное меню", reply_markup=get_organizer_main_menu())
    return ConversationHandler.END


def start_talk(update, context):
    if Talk.objects.filter(is_active=True).exists():
        update.message.reply_text("Сейчас уже идёт чужое выступление")
    else:
        chat_id = update.effective_user.id
        user_id = User.objects.get(chat_id=chat_id).id
        talk = Talk.objects.filter(speaker_id=user_id, is_active=None).order_by('queue').first()
        if talk:
            talk.is_active = True
            talk.started_at = datetime.datetime.now()
            talk.save()
            update.message.reply_text(
                "🎤 Вы начали выступление!\n\n"
                "Теперь слушатели могут задавать вам вопросы.",
                reply_markup=get_speaker_active_menu()
            )
        else:
            update.message.reply_text(
                "У вас больше нет выступлений сегодня",
                reply_markup=get_main_menu()
            )


def end_talk(update, context):
    talk = Talk.objects.get(is_active=True)
    talk.is_active = False
    talk.finished_at = datetime.datetime.now()
    talk.save()
    update.message.reply_text(
            "⏹️ Выступление завершено!\n"
            "Вы вернулись в панель докладчика.",
            reply_markup=get_speaker_dashboard_menu()  # ← Возвращаем обычную панель
        )


def get_questions(update, context):
    questions = get_questions_list()
    message = "Список вопросов к вашему выступлению\n\n"
    for index, question in enumerate(questions, start=1):
        message += f"{index}. {question}\n\n"
    update.message.reply_text(message)


def start_ask_question(update, context):
    user_id = update.effective_user.id
    if not is_talk_active():
        update.message.reply_text("😔 Сейчас нет активных выступлений...")
        return
    speaker_info = get_current_speaker()
    if speaker_info == "Никто":
        update.message.reply_text("😔 Текущий докладчик не запустил поток вопросов...")
        return
    set_user_state(user_id, STATE_WAITING_QUESTION)
    update.message.reply_text(
        f"🎤 Сейчас выступает: {speaker_info}\n\n"
        f"✍️ Напишите ваш вопрос для докладчика:",
        reply_markup=get_question_input_menu()  # ✅ Показывает кнопку "Отменить"
    )


def handle_question_input(update, context):
    user_id = update.effective_user.id
    question_text = update.message.text
    if question_text == "❌ Отменить":
        clear_user_state(user_id)
        update.message.reply_text("❌ Ввод вопроса отменен", reply_markup=get_main_menu())
        return
    if not question_text.strip():
        update.message.reply_text("❌ Вопрос не может быть пустым...")
        return
    question, error = create_question_for_current_speaker(question_text)
    if error:
        update.message.reply_text(f"❌ {error}", reply_markup=get_main_menu())
    else:
        speaker_info = get_current_speaker()
        update.message.reply_text(
            f"✅ Ваш вопрос отправлен докладчику {speaker_info}!\n\n"
            f"📝 Ваш вопрос: {question_text}",
            reply_markup=get_main_menu()  # ✅ Возврат в главное меню
        )
    clear_user_state(user_id)


def handle_message_input(update, context):

    user_id = update.effective_user.id
    message = update.message.text
    bot = telegram.Bot(token=BOT_TOKEN)
    role = get_user_role(user_id)
    if role == "all":
        users = User.objects.all()
    else:
        if role == "user":
            users = User.objects.filter(role=1)
        if role == "speaker":
            users = User.objects.filter(role=2)
        if role == "organizer":
            users = User.objects.filter(role=3)
    for user in users:
        try:
            bot.send_message(
                chat_id=user.chat_id,
                text=message
                            )
        except telegram.error.BadRequest as e:
            print(e)
            continue
    update.message.reply_text("Сообщение разослано", reply_markup=get_organizer_main_menu())
    clear_user_state(user_id)
    clear_role(user_id)


def handle_user_buttons(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    print(f"🔘 Пользователь нажал: {text}")
    if text == "❌ Отменить":
        clear_user_state(user_id)
        update.message.reply_text("❌ Действие отменено", reply_markup=get_main_menu())
        return
    user_state = get_user_state(user_id)
    if user_state == STATE_WAITING_QUESTION:
        handle_question_input(update, context)
        return
    if text == "📅 Программа":
        show_program(update, context)
    elif text == "🏠 Меню":
        update.message.reply_text("🏠 Меню", reply_markup=get_main_menu())
    elif text == "❓ Задать вопрос":
        start_ask_question(update, context)
    elif text == "👨‍💼 Текущий докладчик":
        update.message.reply_text("🎤 Сейчас выступает: Тестовый докладчик")
    elif text == "⭐ Подписка":
        toggle_subscription(user_id, update)
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


def handle_speaker_buttons(update, context, user_id):
    text = update.message.text
    print(f"🔘 Пользователь нажал: {text}")
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
    elif text == "⭐ Подписка":
        toggle_subscription(user_id, update)
    elif text == "🏠 Меню":
        update.message.reply_text("🏠 Меню", reply_markup=get_speaker_main_menu())
    elif text == "📅 Программа":
        show_program(update, context)
    elif text == "▶️ Начать выступление":
        start_talk(update, context)
    elif text == "⏹️ Завершить выступление":
        end_talk(update, context)
    elif text == "📋 Мои вопросы":
        get_questions(update, context)
    elif text == "🏠 Главное меню":
        update.message.reply_text("🏠 Главное меню", reply_markup=get_speaker_main_menu())
    elif text == "❓ Задать вопрос":
        start_ask_question(update, context)
    elif text == "👨‍💼 Текущий докладчик":
        update.message.reply_text(f"🎤 Сейчас выступает: {get_current_speaker()}")
    elif text == "💝 Поддержать проект":
        update.message.reply_text(
            "💝 Поддержать развитие наших митапов!\n\n"
            "Выберите сумму доната:",
            reply_markup=get_donate_menu()
        )


def handle_organizer_buttons(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    user_state = get_user_state(user_id)
    if user_state == STATE_WAITING_MESSAGE:
        handle_message_input(update, context)
        return

    print(f"🔘 Пользователь нажал: {text}")
    if text == "📢 Сделать рассылку":
        update.message.reply_text("📢 Здесь будет массовая рассылка",
                                  reply_markup=get_organizer_panel_menu())
    elif text == "🏠 Меню":
        update.message.reply_text("🏠 Меню", reply_markup=get_organizer_main_menu())
    elif text == "👥 Все":
        update.message.reply_text("Введите текст сообщения")
        user_roles[user_id] = 'all'
        set_user_state(user_id, STATE_WAITING_MESSAGE)
    elif text == "Пользователи":
        set_role_user(update, context)
        update.message.reply_text("Введите текст сообщения")
        set_user_state(user_id, STATE_WAITING_MESSAGE)
    elif text == "🎤 Докладчики":
        set_role_speaker(update, context)
        update.message.reply_text("Введите текст сообщения")
        set_user_state(user_id, STATE_WAITING_MESSAGE)
    elif text == "Администрация":
        set_role_organizer(update, context)
        update.message.reply_text("Введите текст сообщения")
        set_user_state(user_id, STATE_WAITING_MESSAGE)
    elif text == "🏠 Главное меню":
        update.message.reply_text("🏠 Главное меню", reply_markup=get_organizer_main_menu())
    elif text == "Обьявить о мероприятии":
        update.message.reply_text("Для обьявления о новом мероприятии используйте команду /newsletter")


def handle_buttons(update, context):
    user_id = update.effective_user.id
    text = update.message.text
    role = User.objects.get(chat_id=user_id).role
    role = str(role)
    user_state = get_user_state(user_id)
    if user_state == STATE_WAITING_QUESTION:
        handle_user_buttons(update, context)
        return
    print(f"🔘 Пользователь нажал: {text}")
    # РЕЖИМ ЮЗЕРА
    if role == "Пользователь":
        handle_user_buttons(update, context)
    # HT:BV CGBRTHF
    elif role == "Докладчик":
        handle_speaker_buttons(update, context, user_id)
    # РЕЖИМ ОРГАНИЗАТОРА
    elif role == "Администратор":
        handle_organizer_buttons(update, context)


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    newsletter_handler = ConversationHandler(
        entry_points=[CommandHandler('newsletter', newsletter)],
        states={
            FIRST: [MessageHandler(Filters.text, newsletter_first_response)],
            SECOND: [MessageHandler(Filters.text, newsletter_second_response)],
            },
        fallbacks=[]
    )
    dp = updater.dispatcher
    dp.add_handler(newsletter_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", menu))
    dp.add_handler(MessageHandler(Filters.text, handle_buttons))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
