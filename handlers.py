from aiogram import types, Bot
from aiogram.filters import Command
from config import OWNER_ID, SERVICE_MSG_DELETE, MAX_TARGET_GROUPS
from database import *
import asyncio
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)

bot = None
current_group = None

# Загружаем сохраненные времена каналов
channel_times = {}
if os.path.exists('channel_times.json'):
    try:
        with open('channel_times.json', 'r') as f:
            channel_times = json.load(f)
        channel_times = {int(k): v for k, v in channel_times.items()}
    except Exception as e:
        logger.error(f"Ошибка загрузки channel_times: {e}")
        channel_times = {}

def save_channel_times():
    try:
        with open('channel_times.json', 'w') as f:
            json.dump(channel_times, f)
    except Exception as e:
        logger.error(f"Ошибка сохранения channel_times: {e}")

def register_handlers(dp, bot_instance):
    global bot
    bot = bot_instance
    
    # Команды для OWNER_ID
    dp.message.register(cmd_start, Command('start'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_list, Command('list'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_group, Command('group'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_status, Command('status'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_add, Command('add'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_del, Command('del'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_delall, Command('delall'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_time, Command('time'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_lang, Command('lang'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_addvip, Command('addvip'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_addglobal, Command('addglobal'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_delvip, Command('delvip'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_delglobal, Command('delglobal'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_delallvip, Command('delallvip'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_delallglobal, Command('delallglobal'), lambda msg: msg.from_user.id == OWNER_ID)
    
    # Команды для целевых групп
    dp.message.register(cmd_addtarget, Command('addtarget'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_deltarget, Command('deltarget'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_delalltarget, Command('delalltarget'), lambda msg: msg.from_user.id == OWNER_ID)
    dp.message.register(cmd_listtarget, Command('listtarget'), lambda msg: msg.from_user.id == OWNER_ID)
    
    # Обработчик всех сообщений (для всех пользователей)
    dp.message.register(check_message)
    
    # Обработчик новых участников
    dp.chat_member.register(on_chat_member)

async def cmd_start(message: types.Message):
    await message.answer("✅ Бот работает\n/list - список групп\n/listtarget - список целевых групп")

async def cmd_list(message: types.Message):
    groups = get_groups()
    if not groups:
        await message.answer("❌ Бот не добавлен ни в одну группу")
        return
    
    text = "📋 **СПИСОК ГРУПП**\n\n"
    for i, group in enumerate(groups, 1):
        group_id, name, username, language = group
        lang_emoji = "🇷🇺" if language == 'ru' else "🇬🇧"
        text += f"{i}. **{name}** {lang_emoji}\n"
        text += f"   ID: `{group_id}`\n"
        if username:
            text += f"   @{username}\n"
        text += "\n"
    
    await message.answer(text, parse_mode="Markdown")

async def cmd_group(message: types.Message):
    global current_group
    try:
        num = int(message.text.split()[1]) - 1
        groups = get_groups()
        if 0 <= num < len(groups):
            current_group = groups[num][0]
            group_lang = get_group_language(current_group)
            lang_text = "🇷🇺 Русский" if group_lang == 'ru' else "🇬🇧 English"
            await message.answer(f"✅ Выбрана: **{groups[num][1]}**\nЯзык группы: {lang_text}", parse_mode="Markdown")
        else:
            await message.answer("❌ Неверный номер")
    except:
        await message.answer("Используйте: /group число")

async def cmd_lang(message: types.Message):
    global current_group
    if not current_group:
        await message.answer("❌ Сначала выберите группу: /group число")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer("❌ Используйте: /lang ru или /lang en")
            return
        
        lang = parts[1].lower()
        if lang not in ['ru', 'en']:
            await message.answer("❌ Доступные языки: ru (русский), en (английский)")
            return
        
        if set_group_language(current_group, lang):
            lang_text = "русский" if lang == 'ru' else "английский"
            await message.answer(f"✅ Язык группы изменен на {lang_text}")
        else:
            await message.answer("❌ Ошибка при смене языка")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

async def cmd_addtarget(message: types.Message):
    """Добавить целевую группу для проверки"""
    global current_group
    if not current_group:
        await message.answer("❌ Сначала выберите группу: /group число")
        return
    
    try:
        target_input = message.text.split()[1]
        
        # Получаем информацию о целевой группе
        try:
            if target_input.startswith('@'):
                # Это username
                chat = await bot.get_chat(target_input)
                target_id = chat.id
                target_name = chat.title
                target_username = chat.username
            else:
                # Это ID
                target_id = int(target_input)
                chat = await bot.get_chat(target_id)
                target_name = chat.title
                target_username = chat.username
        except Exception as e:
            await message.answer(f"❌ Не удалось получить информацию о группе: {e}")
            return
        
        # Проверяем, что бот админ в целевой группе
        try:
            bot_member = await bot.get_chat_member(target_id, (await bot.me()).id)
            if bot_member.status not in ['administrator', 'creator']:
                await message.answer(
                    "❌ Бот не является администратором в целевой группе!\n"
                    "Добавьте бота по ссылке с минимальными правами:\n"
                    f"https://t.me/{(await bot.me()).username}?startgroup=bot&admin=invite_users+manage_chat"
                )
                return
        except Exception as e:
            await message.answer(f"❌ Не удалось проверить права бота: {e}")
            return
        
        # Сохраняем
        success, msg = add_target_group(current_group, target_id, target_name, target_username)
        await message.answer(msg)
            
    except IndexError:
        await message.answer(
            "❌ Используйте:\n"
            "/addtarget @username_группы\n"
            "/addtarget -1001234567890"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

async def cmd_listtarget(message: types.Message):
    """Список целевых групп"""
    global current_group
    if not current_group:
        await message.answer("❌ Сначала выберите группу: /group число")
        return
    
    targets = get_target_groups(current_group)
    if not targets:
        await message.answer("📭 Нет добавленных целевых групп")
        return
    
    text = f"🎯 **ЦЕЛЕВЫЕ ГРУППЫ**\n(для текущей группы)\n\n"
    for i, (tg_id, tg_name, tg_username) in enumerate(targets, 1):
        text += f"{i}. **{tg_name}**\n"
        text += f"   ID: `{tg_id}`\n"
        if tg_username:
            text += f"   @{tg_username}\n"
        text += "\n"
    
    await message.answer(text, parse_mode="Markdown")

async def cmd_deltarget(message: types.Message):
    """Удалить целевую группу"""
    global current_group
    if not current_group:
        await message.answer("❌ Сначала выберите группу: /group число")
        return
    
    try:
        target_input = message.text.split()[1]
        
        # Определяем, что ввели: номер, ID или username
        if target_input.isdigit():
            # По номеру из списка
            num = int(target_input) - 1
            targets = get_target_groups(current_group)
            if 0 <= num < len(targets):
                target_id = targets[num][0]
                target_name = targets[num][1]
            else:
                await message.answer("❌ Неверный номер")
                return
        else:
            # По ID или username
            if target_input.startswith('-100') or target_input.startswith('100'):
                target_id = int(target_input)
                target_name = f"ID {target_id}"
            elif target_input.startswith('@'):
                # По username
                target_username = target_input.replace('@', '')
                targets = get_target_groups(current_group)
                found = False
                for tg_id, tg_name, tg_username in targets:
                    if tg_username and tg_username.lower() == target_username.lower():
                        target_id = tg_id
                        target_name = tg_name
                        found = True
                        break
                if not found:
                    await message.answer(f"❌ Группа @{target_username} не найдена")
                    return
            else:
                await message.answer("❌ Неверный формат")
                return
        
        if del_target_group(current_group, target_id):
            await message.answer(f"✅ Целевая группа **{target_name}** удалена", parse_mode="Markdown")
        else:
            await message.answer("❌ Ошибка при удалении")
            
    except IndexError:
        await message.answer(
            "❌ Используйте:\n"
            "/deltarget 1 (по номеру из списка)\n"
            "/deltarget -1001234567890 (по ID)\n"
            "/deltarget @username (по username)"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

async def cmd_delalltarget(message: types.Message):
    """Удалить все целевые группы"""
    global current_group
    if not current_group:
        await message.answer("❌ Сначала выберите группу: /group число")
        return
    
    if del_all_target_groups(current_group):
        await message.answer("✅ Все целевые группы удалены")
    else:
        await message.answer("❌ Ошибка при удалении")

# ... (остальные команды cmd_add, cmd_del, cmd_time, cmd_addvip, cmd_addglobal и т.д. без изменений) ...

async def on_chat_member(update: types.ChatMemberUpdated):
    """Обработчик новых участников"""
    if update.new_chat_member.user.id == (await bot.me()).id:
        add_group(update.chat.id, update.chat.title, update.chat.username)
        await bot.send_message(OWNER_ID, f"✅ Бот добавлен в группу: {update.chat.title}")

async def get_unsubscribed_items(user_id, group_id):
    """Проверяет подписку на каналы и группы"""
    unsubscribed_items = []  # (type, name, url_or_id)
    
    # 1. Проверяем каналы
    channels = get_channels(group_id)
    for channel in channels:
        try:
            channel_username = channel.replace('@', '')
            chat_member = await bot.get_chat_member(f"@{channel_username}", user_id)
            if chat_member.status in ['left', 'kicked']:
                unsubscribed_items.append(('channel', channel, f"https://t.me/{channel_username}"))
        except:
            unsubscribed_items.append(('channel', channel, f"https://t.me/{channel_username}"))
    
    # 2. Проверяем целевые группы
    target_groups = get_target_groups(group_id)
    for tg_id, tg_name, tg_username in target_groups:
        try:
            member = await bot.get_chat_member(tg_id, user_id)
            if member.status in ['left', 'kicked']:
                if tg_username:
                    unsubscribed_items.append(('group', tg_name, f"https://t.me/{tg_username}"))
                else:
                    unsubscribed_items.append(('group', tg_name, None))
        except:
            if tg_username:
                unsubscribed_items.append(('group', tg_name, f"https://t.me/{tg_username}"))
            else:
                unsubscribed_items.append(('group', tg_name, None))
    
    return unsubscribed_items

async def check_message(message: types.Message):
    """Проверка каждого сообщения"""
    if message.chat.type not in ['group', 'supergroup']:
        return
    
    # Сохраняем группу
    add_group(message.chat.id, message.chat.title, message.chat.username)
    
    # Проверяем админов
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ['administrator', 'creator']:
            logger.info(f"Админ {message.from_user.id} пропущен")
            return
    except:
        pass
    
    # Проверяем OWNER и VIP
    if message.from_user.id == OWNER_ID:
        logger.info(f"Owner {message.from_user.id} пропущен")
        return
    
    if is_vip(message.from_user.id, message.chat.id):
        logger.info(f"VIP {message.from_user.id} пропущен")
        return
    
    # Получаем неподписанные элементы (каналы и группы)
    unsubscribed_items = await get_unsubscribed_items(message.from_user.id, message.chat.id)
    
    if not unsubscribed_items:
        logger.info(f"Пользователь {message.from_user.id} подписан на всё")
        return
    
    # Удаляем сообщение
    try:
        await message.delete()
        logger.info(f"Сообщение удалено")
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
    
    # Получаем язык группы
    group_lang = get_group_language(message.chat.id)
    
    # Создаем клавиатуру
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
    
    for item_type, item_name, item_url in unsubscribed_items:
        if item_type == 'channel':
            button_text = f"📢 Перейти в {item_name}" if group_lang == 'ru' else f"📢 Join {item_name}"
            if item_url:
                keyboard.inline_keyboard.append([
                    types.InlineKeyboardButton(text=button_text, url=item_url)
                ])
        else:  # group
            button_text = f"👥 Вступить в {item_name}" if group_lang == 'ru' else f"👥 Join {item_name}"
            if item_url:
                keyboard.inline_keyboard.append([
                    types.InlineKeyboardButton(text=button_text, url=item_url)
                ])
            else:
                # Если нет ссылки, добавляем как текст
                keyboard.inline_keyboard.append([
                    types.InlineKeyboardButton(text=f"🔒 {item_name}", callback_data="no_link")
                ])
    
    # Упоминание пользователя
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    
    # Текст предупреждения
    if group_lang == 'en':
        warning_text = f"❗ {mention}, please subscribe to these channels/groups to write in the chat:"
    else:
        warning_text = f"❗ {mention}, подпишитесь на эти каналы/группы чтобы писать в чат:"
    
    # Отправляем предупреждение
    warning_msg = await message.answer(
        warning_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    # Удаляем предупреждение через 60 секунд
    await asyncio.sleep(SERVICE_MSG_DELETE)
    try:
        await warning_msg.delete()
    except:
        pass

# Заглушка для callback
async def cmd_no_link(callback: types.CallbackQuery):
    await callback.answer("❌ У этой группы нет публичной ссылки", show_alert=True)