import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота и ID владельца
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))

# Настройки групп и каналов
MAX_CHANNELS = 3  # Максимум каналов на группу
MAX_TARGET_GROUPS = 5  # Максимум целевых групп на одну группу

# Временные настройки
SERVICE_MSG_DELETE = 60  # секунд до автоудаления предупреждения
DEFAULT_CHECK_HOURS = 24  # часов проверки по умолчанию
DEFAULT_VIP_DAYS = 30  # дней VIP по умолчанию

# Доступные языки
LANGUAGES = {
    'ru': {
        'name': 'Русский',
        'emoji': '🇷🇺'
    },
    'en': {
        'name': 'English',
        'emoji': '🇬🇧'
    }
}

# Тексты для разных языков
WARNING_TEXTS = {
    'ru': "❗ {mention}, подпишитесь на эти каналы/группы чтобы писать в чат:",
    'en': "❗ {mention}, please subscribe to these channels/groups to write in the chat:"
}

BUTTON_TEXTS = {
    'channel': {
        'ru': "📢 Перейти в {name}",
        'en': "📢 Join {name}"
    },
    'group': {
        'ru': "👥 Вступить в {name}",
        'en': "👥 Join {name}"
    }
}

# Сообщения об ошибках
ERROR_MESSAGES = {
    'ru': {
        'no_group': "❌ Сначала выберите группу: /group число",
        'invalid_number': "❌ Неверный номер",
        'no_groups': "❌ Бот не добавлен ни в одну группу",
        'max_channels': "❌ Максимум {max} каналов на группу",
        'channel_exists': "❌ Канал {channel} уже существует",
        'channel_not_found': "❌ Канал {channel} не найден",
        'invalid_time': "❌ Время должно быть в формате: 6h, 12h, 24h",
        'invalid_days': "❌ Дни должны быть в формате: 7d, 30d",
        'invalid_lang': "❌ Доступные языки: ru (русский), en (английский)",
        'not_admin': "❌ Бот не является администратором в целевой группе",
        'no_targets': "📭 Нет добавленных целевых групп",
        'target_exists': "❌ Целевая группа уже добавлена",
        'max_targets': "❌ Максимум {max} целевых групп"
    },
    'en': {
        'no_group': "❌ First select a group: /group number",
        'invalid_number': "❌ Invalid number",
        'no_groups': "❌ Bot is not added to any group",
        'max_channels': "❌ Maximum {max} channels per group",
        'channel_exists': "❌ Channel {channel} already exists",
        'channel_not_found': "❌ Channel {channel} not found",
        'invalid_time': "❌ Time must be in format: 6h, 12h, 24h",
        'invalid_days': "❌ Days must be in format: 7d, 30d",
        'invalid_lang': "❌ Available languages: ru (Russian), en (English)",
        'not_admin': "❌ Bot is not an administrator in the target group",
        'no_targets': "📭 No target groups added",
        'target_exists': "❌ Target group already exists",
        'max_targets': "❌ Maximum {max} target groups"
    }
}

# Успешные сообщения
SUCCESS_MESSAGES = {
    'ru': {
        'channel_added': "✅ Канал {channel} добавлен",
        'channel_deleted': "✅ {channel} удален",
        'channels_deleted': "✅ Все каналы удалены",
        'time_set': "✅ Для канала {channel} установлено время проверки: {hours} часов",
        'lang_changed': "✅ Язык группы изменен на {lang}",
        'vip_added': "✅ {user} добавлен в VIP на {days} дней",
        'global_added': "✅ {user} добавлен в ГЛОБАЛЬНЫЙ VIP на {days} дней",
        'vip_deleted': "✅ {user} удален из VIP",
        'target_added': "✅ Целевая группа {name} добавлена",
        'target_deleted': "✅ Целевая группа {name} удалена",
        'targets_deleted': "✅ Все целевые группы удалены"
    },
    'en': {
        'channel_added': "✅ Channel {channel} added",
        'channel_deleted': "✅ {channel} deleted",
        'channels_deleted': "✅ All channels deleted",
        'time_set': "✅ For channel {channel} set check time: {hours} hours",
        'lang_changed': "✅ Group language changed to {lang}",
        'vip_added': "✅ {user} added to VIP for {days} days",
        'global_added': "✅ {user} added to GLOBAL VIP for {days} days",
        'vip_deleted': "✅ {user} removed from VIP",
        'target_added': "✅ Target group {name} added",
        'target_deleted': "✅ Target group {name} removed",
        'targets_deleted': "✅ All target groups removed"
    }
}