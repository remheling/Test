import re
from datetime import datetime
import json
import os
from typing import Optional, List, Dict, Any, Union, Tuple
import logging

logger = logging.getLogger(__name__)

# ========== ПАРСИНГ ВРЕМЕНИ ==========

def parse_time(time_str: str) -> int:
    """
    Парсит время из формата "6h", "12h", "24h" в часы
    Возвращает количество часов или 24 по умолчанию
    
    Args:
        time_str: Строка с временем (например: "6h", "12h", "24h")
    
    Returns:
        int: Количество часов (6, 12, 24) или 24 по умолчанию
    """
    if not time_str or not isinstance(time_str, str):
        return 24
    
    match = re.match(r'^(\d+)h$', time_str.lower().strip())
    if match:
        hours = int(match.group(1))
        if hours in [6, 12, 24]:
            return hours
    return 24

def parse_days(days_str: str) -> int:
    """
    Парсит дни из формата "7d", "30d" в дни
    Возвращает количество дней или 7 по умолчанию
    
    Args:
        days_str: Строка с днями (например: "7d", "30d")
    
    Returns:
        int: Количество дней (7, 30) или 7 по умолчанию
    """
    if not days_str or not isinstance(days_str, str):
        return 7
    
    match = re.match(r'^(\d+)d$', days_str.lower().strip())
    if match:
        days = int(match.group(1))
        if days in [7, 30]:
            return days
    return 7

# ========== ВАЛИДАЦИЯ USERNAME ==========

def format_username(text: str) -> Optional[str]:
    """
    Извлекает username из текста (убирает @ если есть)
    
    Args:
        text: Текст с username (например: "@username" или "username")
    
    Returns:
        Optional[str]: Очищенный username или None если невалидный
    """
    if not text:
        return None
    
    # Убираем @ если есть в начале
    clean = text.strip().replace('@', '')
    
    # Проверяем, что остальное похоже на username (буквы, цифры, подчеркивания)
    if re.match(r'^[a-zA-Z0-9_]{5,32}$', clean):
        return clean
    return None

def is_valid_username(username: str) -> bool:
    """
    Проверяет, является ли строка валидным username
    
    Args:
        username: Строка для проверки
    
    Returns:
        bool: True если валидный username
    """
    if not username:
        return False
    return bool(re.match(r'^@?[a-zA-Z0-9_]{5,32}$', username))

# ========== ФОРМАТИРОВАНИЕ ==========

def format_time(timestamp: Union[int, float]) -> str:
    """
    Форматирует timestamp в читаемую дату
    
    Args:
        timestamp: Unix timestamp
    
    Returns:
        str: Отформатированная дата (YYYY-MM-DD HH:MM)
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return "Неизвестно"

def format_days_left(timestamp: Union[int, float]) -> str:
    """
    Форматирует оставшиеся дни из timestamp
    
    Args:
        timestamp: Unix timestamp окончания
    
    Returns:
        str: Отформатированное время (например: "5 дней", "истек")
    """
    try:
        days = int((timestamp - datetime.now().timestamp()) / 86400)
        if days < 0:
            return "истек"
        elif days == 0:
            return "менее дня"
        elif days == 1:
            return "1 день"
        elif 2 <= days <= 4:
            return f"{days} дня"
        else:
            return f"{days} дней"
    except:
        return "неизвестно"

def get_user_mention(user_id: int, first_name: str, username: Optional[str] = None) -> str:
    """
    Создает упоминание пользователя для HTML
    
    Args:
        user_id: ID пользователя
        first_name: Имя пользователя
        username: Username (если есть)
    
    Returns:
        str: HTML код для упоминания
    """
    if username:
        return f"@{username}"
    return f"<a href='tg://user?id={user_id}'>{first_name}</a>"

# ========== РАБОТА С КАНАЛАМИ ==========

def clean_channel_name(channel: str) -> str:
    """
    Очищает название канала от @ для ссылок
    
    Args:
        channel: Название канала (например: "@channel" или "channel")
    
    Returns:
        str: Очищенное название
    """
    if not channel:
        return ""
    return channel.replace('@', '').strip()

def get_channel_url(channel: str) -> str:
    """
    Формирует URL канала
    
    Args:
        channel: Название канала (например: "@channel")
    
    Returns:
        str: Полный URL канала или "#" если ошибка
    """
    clean = clean_channel_name(channel)
    if clean:
        return f"https://t.me/{clean}"
    return "#"

def validate_channel_input(channel: str) -> Optional[str]:
    """
    Валидирует и форматирует ввод канала
    
    Args:
        channel: Введенный пользователем канал
    
    Returns:
        Optional[str]: Отформатированный канал или None если невалидный
    """
    if not channel:
        return None
    
    # Убираем пробелы
    channel = channel.strip()
    
    # Добавляем @ если нужно
    if not channel.startswith('@'):
        channel = '@' + channel
    
    # Проверяем длину и символы
    clean = channel.replace('@', '')
    if re.match(r'^[a-zA-Z0-9_]{5,32}$', clean):
        return channel
    
    return None

# ========== РАБОТА С JSON ==========

def load_json_data(file_path: str, default: Any = None) -> Any:
    """
    Загружает данные из JSON файла
    
    Args:
        file_path: Путь к JSON файлу
        default: Значение по умолчанию если файл не найден
    
    Returns:
        Any: Загруженные данные или default
    """
    if default is None:
        default = {}
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Ошибка загрузки JSON из {file_path}: {e}")
            return default
    return default

def save_json_data(file_path: str, data: Any) -> bool:
    """
    Сохраняет данные в JSON файл
    
    Args:
        file_path: Путь к JSON файлу
        data: Данные для сохранения
    
    Returns:
        bool: True если успешно, False если ошибка
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, TypeError) as e:
        logger.error(f"Ошибка сохранения JSON в {file_path}: {e}")
        return False

# ========== РАБОТА С СООБЩЕНИЯМИ ==========

def split_message(text: str, max_length: int = 4096) -> List[str]:
    """
    Разбивает длинное сообщение на части для Telegram
    
    Args:
        text: Текст сообщения
        max_length: Максимальная длина одной части (по умолчанию 4096)
    
    Returns:
        List[str]: Список частей сообщения
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    for line in text.split('\n'):
        if len(current_part) + len(line) + 1 <= max_length:
            if current_part:
                current_part += '\n' + line
            else:
                current_part = line
        else:
            if current_part:
                parts.append(current_part)
            current_part = line
    
    if current_part:
        parts.append(current_part)
    
    return parts

def escape_markdown(text: str) -> str:
    """
    Экранирует специальные символы для Markdown
    
    Args:
        text: Текст для экранирования
    
    Returns:
        str: Экранированный текст
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# ========== РАБОТА С ЯЗЫКАМИ ==========

def get_language_emoji(lang: str) -> str:
    """
    Возвращает эмодзи для языка
    
    Args:
        lang: Код языка ('ru' или 'en')
    
    Returns:
        str: Эмодзи флага
    """
    from config import LANGUAGES
    return LANGUAGES.get(lang, {}).get('emoji', '🌐')

def get_warning_text(lang: str, mention: str) -> str:
    """
    Возвращает текст предупреждения на нужном языке
    
    Args:
        lang: Код языка
        mention: Упоминание пользователя
    
    Returns:
        str: Текст предупреждения
    """
    from config import WARNING_TEXTS
    template = WARNING_TEXTS.get(lang, WARNING_TEXTS['ru'])
    return template.format(mention=mention)

def get_button_text(lang: str, item_type: str, name: str) -> str:
    """
    Возвращает текст кнопки на нужном языке
    
    Args:
        lang: Код языка
        item_type: Тип ('channel' или 'group')
        name: Название канала/группы
    
    Returns:
        str: Текст кнопки
    """
    from config import BUTTON_TEXTS
    template = BUTTON_TEXTS.get(item_type, {}).get(lang, BUTTON_TEXTS['channel']['ru'])
    return template.format(name=name)

def get_error_message(lang: str, key: str, **kwargs) -> str:
    """
    Возвращает сообщение об ошибке на нужном языке
    
    Args:
        lang: Код языка
        key: Ключ сообщения
        **kwargs: Параметры для форматирования
    
    Returns:
        str: Сообщение об ошибке
    """
    from config import ERROR_MESSAGES
    template = ERROR_MESSAGES.get(lang, ERROR_MESSAGES['ru']).get(key, "❌ Ошибка")
    return template.format(**kwargs)

def get_success_message(lang: str, key: str, **kwargs) -> str:
    """
    Возвращает сообщение об успехе на нужном языке
    
    Args:
        lang: Код языка
        key: Ключ сообщения
        **kwargs: Параметры для форматирования
    
    Returns:
        str: Сообщение об успехе
    """
    from config import SUCCESS_MESSAGES
    template = SUCCESS_MESSAGES.get(lang, SUCCESS_MESSAGES['ru']).get(key, "✅ Успешно")
    return template.format(**kwargs)

# ========== ПАРСИНГ ID ==========

def parse_telegram_id(text: str) -> Optional[int]:
    """
    Парсит Telegram ID из текста
    
    Args:
        text: Текст с ID (например: "123456789" или "-1001234567890")
    
    Returns:
        Optional[int]: ID или None если невалидный
    """
    if not text:
        return None
    
    # Убираем @ если есть
    clean = text.strip().replace('@', '')
    
    # Проверяем формат ID (число, может начинаться с -100)
    if re.match(r'^-?\d+$', clean):
        try:
            return int(clean)
        except:
            return None
    return None

def is_group_id(chat_id: int) -> bool:
    """
    Проверяет, является ли ID ID группы
    
    Args:
        chat_id: ID чата
    
    Returns:
        bool: True если это группа
    """
    return chat_id < 0 and str(chat_id).startswith('-100')

# ========== ЛОГИРОВАНИЕ ==========

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Настраивает логгер
    
    Args:
        name: Имя логгера
        level: Уровень логирования
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Создаем обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчик
    logger.addHandler(console_handler)
    
    return logger

# ========== ДЕКОРАТОРЫ ==========

def async_timer(func):
    """
    Декоратор для измерения времени выполнения асинхронной функции
    """
    async def wrapper(*args, **kwargs):
        start = datetime.now()
        result = await func(*args, **kwargs)
        end = datetime.now()
        logger.debug(f"{func.__name__} выполнена за {(end - start).total_seconds():.2f} сек")
        return result
    return wrapper

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """
    Декоратор для повторной попытки при ошибке
    
    Args:
        max_retries: Максимальное количество попыток
        delay: Задержка между попытками
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Попытка {attempt + 1} не удалась: {e}. Повтор через {delay} сек")
                    await asyncio.sleep(delay)
            return None
        return wrapper
    return decorator