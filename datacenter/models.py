from django.db import models


class Role(models.Model):
    title = models.CharField("Название", max_length=20)

    class Meta:
        ordering = ('title',)
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.title


class User(models.Model):
    nickname = models.CharField("Имя пользователя")
    chat_id = models.CharField("ChatID", max_length=50)
    role = models.ForeignKey(Role, verbose_name="Роль", on_delete=models.SET_DEFAULT, default=1, related_name="users")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('nickname',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.nickname


class Event(models.Model):
    title = models.CharField("Название мероприятия")
    date = models.DateTimeField("Дата проведения", auto_now=False, auto_now_add=False)
    description = models.TextField("Описание")
    is_active = models.BooleanField(("Активно?"), default=None, blank=True, null=True)
    image = models.ImageField(("Изображение"), null=True, blank=True)

    class Meta:
        ordering = ('date',)
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return self.title


class Talk(models.Model):
    speaker = models.CharField("Имя выступающего")
    speaker_id = models.ForeignKey(User, verbose_name="ID выступающего", on_delete=models.CASCADE)
    title = models.CharField("Название доклада")
    description = models.TextField("Описание")
    queue = models.PositiveIntegerField("Порядок в расписании")
    event = models.ForeignKey(Event, verbose_name="Мероприятие", on_delete=models.CASCADE, null=True)
    started_at = models.DateTimeField("Начало выступления", auto_now=False, auto_now_add=False, blank=True, null=True)
    finished_at = models.DateTimeField("Начало выступления", auto_now=False, auto_now_add=False, blank=True, null=True)

    class Meta:
        verbose_name = 'Доклад'
        verbose_name_plural = 'Доклады'

    def __str__(self):
        return self.title


class Question(models.Model):
    talk = models.ForeignKey(Talk, verbose_name="Вопрос к", on_delete=models.CASCADE, related_name='questions')
    text = models.TextField("Текст вопроса")
    created_at = models.DateTimeField("Когда был задан вопрос", auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return (f"Вопрос к {self.talk.title} {self.created_at}")
