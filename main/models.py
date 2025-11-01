from django.db import models
from django.contrib.auth.models import User

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    short_description = models.TextField(verbose_name="Краткое описание", help_text="Этот текст будет отображаться в списке новостей")
    content = models.TextField(verbose_name="Полный текст новости")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news_images/', verbose_name="Изображение")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Изображение для {self.news.title}"

    class Meta:
        verbose_name = "Изображение новости"
        verbose_name_plural = "Изображения новостей"


class Application(models.Model):
    SERVICE_CHOICES = [
        ('container_reception', 'Прием груженых и порожних контейнеров'),
        ('documents_clearance', 'Раскредитовка документов на станции'),
        ('container_delivery', 'Доставка контейнеров автотранспортом'),
        ('loading_unloading', 'Организация погрузки-выгрузки'),
        ('container_storage', 'Хранение контейнеров на терминале'),
        ('container_shipping', 'Отправка контейнеров по России/экспорт'),
        ('shipping_docs', 'Оформление перевозочных документов'),
        ('cargo_insurance', 'Страхование грузов'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В процессе'),
        ('pending', 'В ожидании'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    
    STATUS_COLORS = {
        'new': 'secondary',
        'in_progress': 'primary',
        'pending': 'warning',
        'completed': 'success',
        'cancelled': 'danger',
    }
    
    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, verbose_name='Услуга')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка от {self.name} ({self.service})'
    
    def get_status_color(self):
        return self.STATUS_COLORS.get(self.status, 'secondary')

class Document(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

class CompanyRequisites(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="Полное наименование", 
                               default='Общество с ограниченной ответственностью "Трансагентство"')
    short_name = models.CharField(max_length=100, verbose_name="Краткое наименование", 
                                default='ООО «ТрА»')
    legal_address = models.TextField(verbose_name="Юридический адрес",
                                   default='РТ, 422772, м. р-н Пестречинский, с.п. Кощаковское, д.Званка, ул.Лазурная д.2А')
    postal_address = models.TextField(verbose_name="Почтовый адрес",
                                    default='РТ, 422772, м. р-н Пестречинский, с.п. Кощаковское, д.Званка, ул.Лазурная д.2А')
    phone = models.CharField(max_length=20, verbose_name="Телефон",
                           default='+7 (904) 768-70-89')
    email = models.EmailField(verbose_name="Эл. почта",
                            default='tra.info@mail.ru')
    inn = models.CharField(max_length=12, verbose_name="ИНН",
                         default='1651092275')
    kpp = models.CharField(max_length=9, verbose_name="КПП",
                          default='168601001')
    ogrn = models.CharField(max_length=15, verbose_name="ОГРН",
                           default='1221600078809')
    okpo = models.CharField(max_length=10, verbose_name="ОКПО",
                           default='75376496')
    railway_code = models.CharField(max_length=10, verbose_name="Код жд",
                                   default='4231')
    els_code = models.CharField(max_length=15, verbose_name="Код ЕЛС",
                               default='1006546099')
    
    # Рублёвый счёт
    bank_name_rub = models.CharField(max_length=200, verbose_name="Банк (руб)",
                                    default='ФИЛИАЛ «НИЖЕГОРОДСКИЙ» АО «АЛЬФА-БАНК»')
    account_rub = models.CharField(max_length=20, verbose_name="Рублёвый р/с",
                                  default='40702810629140008516')
    corr_account_rub = models.CharField(max_length=20, verbose_name="Корр. счёт (руб)",
                                       default='30101810200000000824')
    bik_rub = models.CharField(max_length=9, verbose_name="БИК (руб)",
                              default='042202824')
    
    # Валютный счёт
    bank_name_curr = models.CharField(max_length=200, verbose_name="Банк (вал)",
                                     default='ООО Банк Аверс')
    account_curr = models.CharField(max_length=20, verbose_name="Валютный счёт",
                                   default='4070216300390000051')
    corr_account_curr = models.CharField(max_length=20, verbose_name="Корр. счёт (вал)",
                                        default='30101810500000000774')
    bik_curr = models.CharField(max_length=9, verbose_name="БИК (вал)",
                               default='049205774')
    
    director = models.CharField(max_length=100, verbose_name="Генеральный директор",
                               default='Давлетшина Алсу Ринатовна')

    def __str__(self):
        return self.short_name

    class Meta:
        verbose_name = "Реквизиты компании"
        verbose_name_plural = "Реквизиты компании"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f'Профиль {self.user.username}'

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

# Сигнал для автоматического создания профиля при создании пользователя
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()