from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone

from address_app.models import City


User = get_user_model()


class Promotion(models.Model):
    category = models.ForeignKey('PromoCategory', on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name='категория')
    name = models.CharField(max_length=255, verbose_name='название')
    price = models.PositiveIntegerField(verbose_name='стоимость')
    description = models.TextField(blank=True, null=True, verbose_name='описание',
                                   help_text="""Главное! Чтобы не запутаться, следуйте по порядку в инструкции! 
                                   Общая идея делится на четыре основных шага: 1.позиционируем весь текст => 2. делим на абзацы => 3. задаем красную строку => 4. внутри абзацев редактируем стили
                                   Все символы пишите маленькими буквами, без пробелов, ровно так как они написаны в инструкции.
                                   Для страховки их можно копировать, чтобы точно ничего лишнего не написать. 
                                   Все символы написаны на английской раскладке клавиатуры!
                                   1. Позиционирование текста "<l>" : "по левому краю"; "<r>" : "по правому краю"; "<j>" : "растянуть на всю ширину контейнера"; "<m>" : "отцентровать"
                                   По умолчанию: слева. Позиционируется весь текст сразу. Только один раз. Ставим обозначение перед самым началом текста, без повторений. Если не напишете, то будет по умолчанию: слева.
                                   2. Делим текст да абзацы, всегда по 2 строки разделения! символ: <br2>
                                   3. В каждом абзаце можно сделать красную строку, красная строка может быть с разным отступом: <p0> - нет отступа, далее цифры по возрастанию увеличивают отступ
                                    Внимание! не все цифры можно использовать! цифры, которые можно использовать: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 20, 24, 28, 32, 36, 40.
                                    напирмер <p40>, <p20>, <p32>. Использовать ТОЛЬКО ОДИН РАЗ в самом начале абзаца. Без повторений.
                                   4. теперь в каждом из абзацев можно приемнять другие символы:
                                   <b></b> - выделяет текст жирным, пример: <b>текст</b> => этот текст будет написан жирным шрифтом (может быть внутри других типов написания текста, например
                                   <i><b>текст</b></i> - жирный и курсив одновременно; <u><b>текст</b></u> - жирный и подчеркнутый одновременно; <с><b>текст</b></с> - жирный и зачеркнутый одновременно;)
                                   <i></i> - выделяет текст курсивом, пример: <i>текст</i> => этот текст будет написан курсивом ( НЕ МОЖЕТ быть внутри других типов написания текста)
                                   <u></u> - подчеркивает текст, пример: <u>текст</u> => этот текст будет подчеркнут ( НЕ МОЖЕТ быть внутри других типов написания текста)
                                   <с></с> - перечеркивает текст, пример: <c>текст</c> => этот текст будет перечеркнут ( НЕ МОЖЕТ быть внутри других типов написания текста)
                                   <br1> - делает перенос строки, например: Долой беду – дари еду!<br1>🤍 => сердечно будет перенесено на новую строку.
                                    Можно ставить сколько угодно подряд, один такой "символ" создает один перенос строки
                                    Бонус ссылка: <link><link>, например <link>любая ссылка на ваш выбор без пробелов и других лишних символов<link>.
                                    ссылка может быть только один раз в одном абзаце, и вся вот эта строка (<link>любая ссылка на ваш выбор без пробелов и других лишних символов<link>)
                                    будет заменена словом "тут" по нажатию на которую будет переход по ссылке, так, что ссылку нужно вписать в логическое предложение:
                                    А <link>любая ссылка на ваш выбор без пробелов и других лишних символов<link> вы найдете дополнительную информацию о мероприятии. итог => А тут вы найдете дополнительную информацию о мероприятии.""")
    start_date = models.DateTimeField(default=timezone.now, verbose_name='дата начала')
    quantity = models.PositiveIntegerField(verbose_name='Общее количество', default=1)
    available_quantity = models.PositiveIntegerField(verbose_name='доступное количество', default=1,
                                                     help_text='Изначально должно быть равно количеству. '
                                                               'Будет меняться автоматически')
    for_curators_only = models.BooleanField(default=False, verbose_name='только для кураторов')
    is_active = models.BooleanField(default=True, verbose_name='активная')
    ticket_file = models.URLField(blank=True, null=True, verbose_name='файл')  # TODO: upload to where ?
    about_tickets = models.TextField(blank=True, null=True, verbose_name='информация о билетах')

    # Срок действия поощрения.
    # Если поощрение бессрочное, устанавливается `is_permanent = True`, а поле `end_date`
    # можно оставить пустым.
    # Если у поощрения есть конкретный срок действия, поле `is_permanent` будет `False`, и
    # нужно указать дату в `end_date`.
    is_permanent = models.BooleanField(default=False, verbose_name='бессрочное поощрение')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='дата окончания',
                                    help_text='Только если поощрение не бессрочное')

    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='город')
    users = models.ManyToManyField(User, through='Participation', blank=True, verbose_name='получатель')
    picture = models.ImageField(blank=True, null=True, upload_to='promo_pictures/', verbose_name='картинка',
                                help_text='Ширина 328px, высота 205px')
    address = models.CharField(max_length=255, verbose_name='адрес', blank=True, null=True)
    contact_person = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='contact_persons',
                                       verbose_name='контактное лицо', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_available_promotions(user):
        if user.is_staff:
            # Куратор видит все активные поощрения
            promotions = Promotion.objects.filter(is_active=True)
        else:
            #  волонтёр видит только поощрения, не предназначенные только для кураторов
            promotions = Promotion.objects.filter(is_active=True, for_curators_only=False)
        return promotions

    def clean(self):
        if not self.is_permanent and not self.end_date:
            raise ValidationError("Укажите срок действия или отметьте поощрение как бессрочное.")
        if self.is_permanent and self.end_date:
            raise ValidationError("Бессрочное поощрение не должно иметь срока действия.")
        if self.available_quantity > self.quantity:
            raise ValidationError("Доступное количество не может быть больше общего количества.")

    def save(self, *args, **kwargs):
        if not self.pk:  # Если поощрение создаётся впервые, синхронизируем available_quantity с quantity
            self.available_quantity = self.quantity
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('admin:promo_app_promotion_change', args=[self.pk])

    # Подсчет числа участников поощрений
    def volunteers_count(self):
        return self.participation_set.count()

    @admin.display(description="участники")
    def display_volunteers(self):
        verbose_name = "участник" if self.volunteers_count() == 1 else "участники"
        return format_html("<br>".join([str(user) for user in self.users.all()]))

    class Meta:
        verbose_name = 'поощрение'
        verbose_name_plural = 'поощрения'


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='волонтёр')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, verbose_name='поощрение')
    received_at = models.DateTimeField(auto_now_add=True, verbose_name='дата получения')
    is_active = models.BooleanField(default=False, verbose_name='подтверждение')

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        # Проверяем, есть ли доступные поощрения
        if self.promotion.available_quantity <= 0:
            raise ValidationError("Нет доступных поощрений.")

        # Уменьшаем доступное количество поощрений
        self.promotion.available_quantity -= 1
        self.promotion.save()

        super().save(*args, **kwargs)

    def save_without_reward_check(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Возвращаем поощрение в доступное количество
        self.promotion.available_quantity += 1
        self.promotion.save()

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'участники'
        verbose_name_plural = 'участники'


class PromoCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name='название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория поощрений'
        verbose_name_plural = 'категории поощрений'


