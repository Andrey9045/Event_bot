from django.contrib import admin
from .models import User, Role, Talk, Event, Question


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'chat_id', 'role')
    list_filter = ('role',)
    search_fields = ['nickname', 'chat_id']
    readonly_fields = ('chat_id', 'created_at')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_active')
    list_filter = ['is_active']
    search_fields = ('title', 'description')


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'queue', 'event')
    search_fields = ('title', 'speaker', 'event', 'description', 'speaker_id')
    readonly_fields = ('started_at', 'finished_at')
    raw_id_fields = ('speaker_id',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('talk', 'text')
    search_fields = ('text',)
    readonly_fields = ('created_at',)
    raw_id_fields = ('talk',)


admin.site.register(Role)
