import os
import django
import sys
from django.core.exceptions import ObjectDoesNotExist

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EventBotDjango.settings')
django.setup()

from datacenter.models import User, Role, Event, Talk, Question


def toggle_subscription(chat_id, update):
    user = User.objects.get(chat_id=chat_id)
    if user.subscription:
        update.message.reply_text("❌ Вы отписались от обновлений!")
        user.subscription = False
    else:
        update.message.reply_text("✅ Вы подписались на обновления!")
        user.subscription = True
    user.save()


def get_current_event():
    try:
        event = Event.objects.filter(is_active=True).first()
        if event:
            print(f"Активное мероприятие: {event.title}")
        return event
    except ObjectDoesNotExist:
        print("Активных мероприятий нет")
        return None


def get_event_program(event_id=None):
    try:
        if event_id:
            event = Event.objects.get(id=event_id)
        else:
            event = get_current_event()
        if event:
            talks = Talk.objects.filter(event=event).order_by('queue')
            return event, talks
        return None, []
    except ObjectDoesNotExist:
        return None, []


def create_question_for_current_speaker(question_text):
    try:
        current_talk = Talk.objects.filter(
            started_at__isnull=False,
            finished_at__isnull=True
        ).first()  
        if not current_talk:
            return None, "Сейчас нет активных выступлений"
        question = Question.objects.create(
            talk=current_talk,
            text=question_text
        )
        print(f"Создан вопрос для докладчика '{current_talk.speaker}': {question_text}")
        return question, None
    except Exception as e:
        print(f"Ошибка при создании вопроса: {e}")
        return None, "Ошибка при отправке вопроса"


def is_talk_active():
    try:
        return Talk.objects.filter(
            started_at__isnull=False,
            finished_at__isnull=True
        ).exists()
    except Exception as e:
        print(f"Ошибка при проверке активного выступления: {e}")
        return False


def get_questions_list():
    talk = Talk.objects.get(is_active=True)
    questions_list = []
    for question in talk.questions.all():
        message = f"{question.created_at.time().isoformat(timespec='seconds')} — {question.text}"
        questions_list.append(message)
    return questions_list


def get_current_speaker():
    try:
        talk = Talk.objects.get(is_active=True)
        speaker = talk.speaker
        message = f"{speaker} — {talk.title}"
    except Talk.DoesNotExist:
        message = "Никто"
    return message
