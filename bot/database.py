import os
import django
import sys
from django.core.exceptions import ObjectDoesNotExist

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EventBotDjango.settings')
django.setup()

from datacenter.models import User, Role, Event, Talk, Question


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
