import requests
from django.conf import settings
import logging
from typing import Optional

# Настройка логгера для текущего модуля
logger = logging.getLogger(__name__)

def send_telegram_message(message: str) -> bool:
    """
    Отправляет сообщение в Telegram чат с использованием бота.
    
    Args:
        message (str): Текст сообщения для отправки в Telegram
        
    Returns:
        bool: True если сообщение успешно отправлено, False в случае ошибки
        
    Raises:
        Логирует ошибки, но не вызывает исключения для внешнего использования
    """
    # Проверка наличия необходимых настроек
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram bot token or chat ID not configured")
        return False
    
    # Формирование URL для API Telegram
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Подготовка данных для отправки
    payload = {
        'chat_id': settings.TELEGRAM_CHAT_ID,  # ID чата для отправки сообщения
        'text': message,                       # Текст сообщения
        'parse_mode': 'HTML'                   # Режим парсинга (HTML разметка)
    }
    
    try:
        # Отправка POST запроса к API Telegram
        response = requests.post(url, data=payload, timeout=10)
        
        # Проверка статуса ответа (вызывает исключение при ошибке HTTP)
        response.raise_for_status()
        
        logger.info("Telegram message sent successfully")
        return True
        
    except requests.exceptions.Timeout:
        # Обработка ошибки таймаута
        logger.error("Timeout error while sending Telegram message")
        return False
        
    except requests.exceptions.HTTPError as e:
        # Обработка HTTP ошибок (404, 500, etc.)
        logger.error(f"HTTP error while sending Telegram message: {e}")
        return False
        
    except requests.exceptions.RequestException as e:
        # Общая обработка ошибок запроса
        logger.error(f"Error sending Telegram message: {e}")
        return False