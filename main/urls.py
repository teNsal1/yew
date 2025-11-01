# main/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.decorators.http import require_POST
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Калькулятор стоимости услуг
    path('calculate/', views.calculate_cost, name='calculate'),
    
    # Реквизиты компании
    path('requisites/', views.requisites, name='requisites'),
    path('requisites/download/', views.download_requisites_pdf, name='download_requisites_pdf'),
    
    # Работа с заявками
    path('application/', views.create_application, name='application'),
    path('applications/', views.application_list, name='application_list'),
    path('applications/<int:pk>/update/', views.update_application, name='update_application'),
    path('applications/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    path('applications/<int:pk>/delete/', views.delete_application, name='delete_application'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-applications/<int:pk>/update/', views.update_my_application, name='update_my_application'),
    
    # Работа с новостями
    path('create-news/', views.CreateNewsView.as_view(), name='create_news'),
    path('news/', views.news_list, name='news_list'),
    path('news/delete/<int:pk>/', views.delete_news, name='delete_news'),
    path('news/edit/<int:pk>/', views.edit_news, name='edit_news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    
    # Аутентификация пользователей
    path('login/', LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', require_POST(LogoutView.as_view()), name='logout'),
    path('register/', views.register, name='register'),  # Регистрация нового пользователя

    # Профиль пользователя
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Дополнительные маршруты могут быть добавлены здесь
]