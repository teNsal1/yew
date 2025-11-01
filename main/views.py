# main/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .models import News, Application, NewsImage, CompanyRequisites
from .forms import ApplicationForm, NewsForm, RegistrationForm, ProfileEditForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
import logging
from django.http import HttpRequest
from django.contrib.auth.models import User
from .telegram_utils import send_telegram_message
from django.conf import settings
from django.utils import timezone

# Initialize logger
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Пользовательские утилиты
# -------------------------------------------------------------------
def is_superuser(user: User) -> bool:
    """Проверка, является ли пользователь супер‑администратором."""
    return user.is_superuser

def base_context(request: HttpRequest) -> dict:
    """Контекстный процессор для всех шаблонов."""
    requisites = CompanyRequisites.objects.first()
    return {'requisites': requisites}

def send_new_application_notification(application: Application) -> bool:
    """
    Формирует и отправляет уведомление о новой заявке в Telegram.
    
    Args:
        application: Объект заявки Application
        
    Returns:
        bool: Результат отправки сообщения
    """
    try:
        # Получаем название услуги
        service_display = dict(Application.SERVICE_CHOICES).get(application.service, application.service)
        
        # Определяем тип пользователя
        user_type = "Зарегистрированный пользователь" if application.user else "Анонимный пользователь"
        username = f"@{application.user.username}" if application.user else "Не указан"
        
        # Формируем сообщение
        message = f"""
🚀 <b>НОВАЯ ЗАЯВКА</b>

👤 <b>Имя:</b> {application.name}
📧 <b>Email:</b> {application.email}
📞 <b>Телефон:</b> {application.phone}

🛠 <b>Услуга:</b> {service_display}
📅 <b>Дата:</b> {timezone.localtime(application.created_at).strftime('%d.%m.%Y %H:%M')}

👥 <b>Тип:</b> {user_type}
🔗 <b>Логин:</b> {username}
🆔 <b>ID заявки:</b> #{application.id}
        """
        
        # Отправляем сообщение
        return send_telegram_message(message)
    except Exception as e:
        logger.error(f"Ошибка формирования уведомления в Telegram: {str(e)}")
        return False

# -------------------------------------------------------------------
# Публичные представления
# -------------------------------------------------------------------
def home(request: HttpRequest) -> HttpResponse:
    """Главная страница с последними новостями."""
    latest_news = News.objects.all().order_by('-created_at').prefetch_related('images')[:3]
    return render(request, 'main/home.html', {**{'latest_news': latest_news}, **base_context(request)})

def contacts(request: HttpRequest) -> HttpResponse:
    """Страница контактов."""
    return render(request, 'main/contacts.html', base_context(request))

def documents(request: HttpRequest) -> HttpResponse:
    """Страница документов."""
    return render(request, 'main/documents.html', base_context(request))

def create_application(request: HttpRequest) -> HttpResponse:
    """
    Создание новой заявки с привязкой к пользователю и отправкой в Telegram.
    """
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            if request.user.is_authenticated:
                application.user = request.user
            application.save()
            
            # Отправка уведомления в Telegram
            send_new_application_notification(application)
            
            messages.success(request, 'Ваша заявка успешно отправлена!')
            return redirect('home')
    else:
        # Автоматическое заполнение данных для авторизованных пользователей
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.username,
                'email': request.user.email,
            }
            # Добавляем телефон из профиля, если он есть
            if hasattr(request.user, 'profile') and request.user.profile.phone:
                initial_data['phone'] = request.user.profile.phone
        
        form = ApplicationForm(initial=initial_data)
    
    return render(request, 'main/application.html', {**{'form': form}, **base_context(request)})

def news_list(request: HttpRequest) -> HttpResponse:
    """Список всех новостей с пагинацией."""
    news = News.objects.all().order_by('-created_at').prefetch_related('images')
    paginator = Paginator(news, 5)           # 5 новостей на страницу
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/news_list.html', {**{'page_obj': page_obj}, **base_context(request)})

@login_required
@user_passes_test(is_superuser)
def delete_news(request: HttpRequest, pk: int) -> HttpResponse:
    """Удаление новости (только для суперпользователя)."""
    news = get_object_or_404(News, pk=pk)
    news.delete()
    return redirect('news_list')

class CreateNewsView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создание новости (только для суперпользователя)."""
    model = News
    form_class = NewsForm
    template_name = 'main/create_news.html'
    success_url = reverse_lazy('home')

    def test_func(self) -> bool:
        """Проверка прав доступа."""
        return self.request.user.is_superuser

    def form_valid(self, form: NewsForm) -> HttpResponse:
        """Обработка валидной формы с сохранением изображений."""
        form.instance.author = self.request.user
        response = super().form_valid(form)
        for image in self.request.FILES.getlist('images'):
            NewsImage.objects.create(news=self.object, image=image)
        return response

    def get_context_data(self, **kwargs) -> dict:
        """Добавление базового контекста."""
        ctx = super().get_context_data(**kwargs)
        return {**ctx, **base_context(self.request)}

@login_required
@user_passes_test(is_superuser)
def edit_news(request: HttpRequest, pk: int) -> HttpResponse:
    """Редактирование новости (только для суперпользователя)."""
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            for image in request.FILES.getlist('images'):
                NewsImage.objects.create(news=news, image=image)
            return redirect('news_list')
    else:
        form = NewsForm(instance=news)
    return render(request, 'main/edit_news.html', {**{'form': form, 'news': news}, **base_context(request)})

def news_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Детальная страница новости."""
    try:
        news = get_object_or_404(News.objects.prefetch_related('images'), pk=pk)
        return render(request, 'main/news_detail.html', {**{'news': news}, **base_context(request)})
    except Exception as e:
        return render(request, 'main/news_detail.html', {**{'error': f'Ошибка: {e}'}, **base_context(request)})

def calculate_cost(request: HttpRequest) -> HttpResponse:
    """Страница калькулятора стоимости."""
    return render(request, 'main/calculate.html', base_context(request))

def requisites(request: HttpRequest) -> HttpResponse:
    """Страница реквизитов компании."""
    # Дублируемый код, но оставляем для совместимости
    requisites = CompanyRequisites.objects.first()
    return render(request, 'main/requisites.html', {**{'requisites': requisites}, **base_context(request)})

def download_requisites_pdf(request: HttpRequest) -> HttpResponse:
    """Скачивание реквизитов компании в формате PDF."""
    requisites = CompanyRequisites.objects.first()
    if not requisites:
        return HttpResponse("Реквизиты не найдены", status=404)
    html_string = render_to_string('main/requisites_pdf.html', {'requisites': requisites})
    result = HTML(string=html_string).write_pdf()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="company_requisites.pdf"'
    response.write(result)
    return response

def application_view(request: HttpRequest) -> HttpResponse:
    """Обработка заявки с сообщением об успехе."""
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            if request.user.is_authenticated:
                application.user = request.user
            application.save()
            
            # Отправка уведомления в Telegram
            send_new_application_notification(application)
            
            messages.success(request, 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.')
            return redirect('application')
    else:
        form = ApplicationForm()
    return render(request, 'main/application.html', {'form': form})

def register(request: HttpRequest) -> HttpResponse:
    """
    Регистрация нового пользователя.
    
    Args:
        request: HTTP-запрос
        
    Returns:
        HttpResponse: Ответ с формой регистрации или перенаправление на главную
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('home')
        else:
            # Если форма невалидна, остаемся на странице регистрации
            return render(request, 'main/registration.html', {**{'form': form}, **base_context(request)})
    else:
        form = RegistrationForm()
    
    return render(request, 'main/registration.html', {**{'form': form}, **base_context(request)})

@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """Просмотр профиля пользователя."""
    return render(request, 'main/profile.html', {**{'user': request.user}, **base_context(request)})

@login_required
def edit_profile(request: HttpRequest) -> HttpResponse:
    """
    Редактирование профиля пользователя.
    
    Args:
        request: HTTP-запрос с данными формы
        
    Returns:
        HttpResponse: Ответ с формой редактирования или перенаправление на профиль
    """
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            # Сохраняем пользователя
            user = form.save()
            
            # Если пароль был изменен, обновляем сессию аутентификации
            if form.cleaned_data.get('new_password1'):
                # Обновляем хэш сессии для предотвращения выхода из системы
                update_session_auth_hash(request, user)
                # Дополнительно логиним пользователя для обновления сессии
                login(request, user)
                messages.success(request, 'Пароль успешно изменен!')
            
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'main/edit_profile.html', {**{'form': form}, **base_context(request)})

# -------------------------------------------------------------------
# Представления для пользовательских заявок
# -------------------------------------------------------------------
@login_required
def my_applications(request):
    """Список заявок текущего пользователя"""
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/my_applications.html', {
        **{'applications': applications}, 
        **base_context(request)
    })

@login_required
def update_my_application(request, pk):
    """Редактирование заявки пользователем"""
    application = get_object_or_404(Application, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заявка успешно обновлена!')
            return redirect('my_applications')
    else:
        form = ApplicationForm(instance=application)
    
    return render(request, 'main/update_my_application.html', {
        **{'form': form, 'application': application}, 
        **base_context(request)
    })

# -------------------------------------------------------------------
# Админская панель (заявки)
# -------------------------------------------------------------------
@login_required
@user_passes_test(is_superuser)
def application_list(request: HttpRequest) -> HttpResponse:
    """Список всех заявок (только для суперпользователя)."""
    applications = Application.objects.all().order_by('-created_at')
    return render(request, 'main/application_list.html', {**{'applications': applications}, **base_context(request)})

@login_required
@user_passes_test(is_superuser)
def update_application(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Обновление заявки.
    • При обычном POST – сохраняем данные и перенаправляем на список заявок.
    • При AJAX‑запросе – сохраняем и возвращаем JSON‑ответ с обновлёнными полями.
    """
    application = get_object_or_404(Application, pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Ajax‑ответ
                return JsonResponse({
                    'success': True,
                    'fields': {
                        'name': application.name,
                        'email': application.email,
                        'phone': application.phone,
                        'service_display': application.get_service_display(),
                        'is_processed': application.is_processed,
                    }
                })

            messages.success(request, 'Заявка успешно обновлена!')
            return redirect('application_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ApplicationForm(instance=application)

    context = {'form': form, 'application': application}
    return render(request, 'main/update_application.html', {**context, **base_context(request)})

@login_required
@user_passes_test(is_superuser)
def update_application_status(request: HttpRequest, pk: int) -> JsonResponse:
    """Обновление статуса заявки через AJAX."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            application = get_object_or_404(Application, pk=pk)
            new_status = request.POST.get('status')
            
            # Получаем доступные статусы из модели
            available_statuses = dict(Application.STATUS_CHOICES).keys()
            
            if new_status in available_statuses:
                application.status = new_status
                application.save()
                
                return JsonResponse({
                    'success': True,
                    'status': application.status,
                    'status_display': application.get_status_display(),
                    'status_color': dict(Application.STATUS_COLORS).get(application.status, 'secondary')
                })
            
            return JsonResponse({
                'success': False,
                'error': f'Invalid status. Allowed: {", ".join(available_statuses)}'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error updating status: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only AJAX POST requests allowed'
    }, status=400)

@login_required
@user_passes_test(is_superuser)
def delete_application(request: HttpRequest, pk: int) -> HttpResponse:
    """Удаление заявки."""
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        application.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
            
        messages.success(request, 'Заявка успешно удалена!')
        return redirect('application_list')
    
    return JsonResponse({'success': False, 'error': 'Only POST requests allowed'}, status=400)