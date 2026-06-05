"""
Бот-визитка для бизнеса
Telegram Bot на Python (aiogram 3.x)
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    FSInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.enums import ParseMode
from config import BOT_TOKEN, COMPANY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from aiogram.client.default import DefaultBotProperties

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# ──────────────────────────────────────────────
# КЛАВИАТУРЫ
# ──────────────────────────────────────────────

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🏢 О компании"),
        KeyboardButton(text="🛠 Услуги"),
    )
    builder.row(
        KeyboardButton(text="📦 Портфолио"),
        KeyboardButton(text="💰 Цены"),
    )
    builder.row(
        KeyboardButton(text="👥 Команда"),
        KeyboardButton(text="📞 Контакты"),
    )
    builder.row(KeyboardButton(text="✍️ Оставить заявку"))
    return builder.as_markup(resize_keyboard=True)


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")]
    ])


def services_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i, service in enumerate(COMPANY["services"]):
        builder.button(text=service["name"], callback_data=f"service_{i}")
    builder.button(text="◀️ Назад", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def portfolio_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i, project in enumerate(COMPANY["portfolio"]):
        builder.button(text=project["title"], callback_data=f"project_{i}")
    builder.button(text="◀️ Назад", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def contact_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    c = COMPANY["contacts"]
    if c.get("website"):
        builder.button(text="🌐 Сайт", url=c["website"])
    if c.get("telegram"):
        builder.button(text="💬 Написать в Telegram", url=f"https://t.me/{c['telegram'].lstrip('@')}")
    if c.get("instagram"):
        builder.button(text="📸 Instagram", url=f"https://instagram.com/{c['instagram'].lstrip('@')}")
    builder.button(text="◀️ Назад", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()


# ──────────────────────────────────────────────
# ХЭНДЛЕРЫ
# ──────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    name = message.from_user.first_name or "друг"
    text = (
        f"👋 Привет, <b>{name}</b>!\n\n"
        f"Добро пожаловать в бот компании <b>{COMPANY['name']}</b>.\n\n"
        f"<i>{COMPANY['tagline']}</i>\n\n"
        f"Выберите раздел в меню ниже 👇"
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
        "Используйте кнопки меню для навигации.\n\n"
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — помощь\n"
        "/contact — контакты\n",
        reply_markup=main_menu_keyboard()
    )


@dp.message(F.text == "🏢 О компании")
async def about_company(message: types.Message):
    c = COMPANY
    text = (
        f"🏢 <b>{c['name']}</b>\n\n"
        f"{c['description']}\n\n"
        f"📅 <b>Год основания:</b> {c['founded']}\n"
        f"👥 <b>Команда:</b> {c['team_size']} специалистов\n"
        f"🏆 <b>Проектов выполнено:</b> {c['projects_done']}+\n"
        f"⭐️ <b>Рейтинг:</b> {c['rating']}/5.0\n\n"
        f"<i>{c['mission']}</i>"
    )
    await message.answer(text, reply_markup=back_keyboard())


@dp.message(F.text == "🛠 Услуги")
async def services_list(message: types.Message):
    text = f"🛠 <b>Наши услуги</b>\n\nВыберите услугу для подробной информации:"
    await message.answer(text, reply_markup=services_keyboard())


@dp.callback_query(F.data.startswith("service_"))
async def service_detail(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    service = COMPANY["services"][idx]
    text = (
        f"<b>{service['name']}</b>\n\n"
        f"{service['description']}\n\n"
        f"⏱ <b>Сроки:</b> {service['duration']}\n"
        f"💵 <b>Стоимость:</b> от {service['price']}\n\n"
        f"✅ <b>Что входит:</b>\n"
        + "\n".join(f"  • {item}" for item in service['includes'])
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Заказать", callback_data=f"order_{idx}")
    builder.button(text="◀️ К услугам", callback_data="back_services")
    builder.adjust(2)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "back_services")
async def back_to_services(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🛠 <b>Наши услуги</b>\n\nВыберите услугу для подробной информации:",
        reply_markup=services_keyboard()
    )
    await callback.answer()


@dp.message(F.text == "📦 Портфолио")
async def portfolio_list(message: types.Message):
    await message.answer(
        "📦 <b>Наше портфолио</b>\n\nВыберите проект для просмотра:",
        reply_markup=portfolio_keyboard()
    )


@dp.callback_query(F.data.startswith("project_"))
async def project_detail(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    project = COMPANY["portfolio"][idx]
    text = (
        f"📌 <b>{project['title']}</b>\n\n"
        f"🏷 <b>Клиент:</b> {project['client']}\n"
        f"📂 <b>Тип:</b> {project['type']}\n"
        f"📅 <b>Год:</b> {project['year']}\n\n"
        f"{project['description']}\n\n"
        f"🔧 <b>Технологии:</b> {', '.join(project['tech'])}"
    )
    builder = InlineKeyboardBuilder()
    if project.get("url"):
        builder.button(text="🔗 Посмотреть", url=project["url"])
    builder.button(text="◀️ К портфолио", callback_data="back_portfolio")
    builder.adjust(1)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "back_portfolio")
async def back_to_portfolio(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📦 <b>Наше портфолио</b>\n\nВыберите проект для просмотра:",
        reply_markup=portfolio_keyboard()
    )
    await callback.answer()


@dp.message(F.text == "💰 Цены")
async def prices(message: types.Message):
    lines = ["💰 <b>Прайс-лист</b>\n"]
    for pkg in COMPANY["pricing"]:
        lines.append(f"<b>{pkg['name']}</b> — <b>{pkg['price']}</b>")
        lines.append(f"<i>{pkg['description']}</i>")
        for feature in pkg["features"]:
            lines.append(f"  ✅ {feature}")
        lines.append("")
    lines.append("📩 Для индивидуального расчёта — <b>Оставить заявку</b>")
    await message.answer("\n".join(lines), reply_markup=back_keyboard())


@dp.message(F.text == "👥 Команда")
async def team(message: types.Message):
    lines = ["👥 <b>Наша команда</b>\n"]
    for member in COMPANY["team"]:
        lines.append(f"<b>{member['name']}</b>")
        lines.append(f"💼 {member['role']}")
        lines.append(f"🎓 {member['experience']}")
        lines.append(f"<i>{member['bio']}</i>\n")
    await message.answer("\n".join(lines), reply_markup=back_keyboard())


@dp.message(F.text == "📞 Контакты")
@dp.message(Command("contact"))
async def contacts(message: types.Message):
    c = COMPANY["contacts"]
    text = (
        f"📞 <b>Контакты</b>\n\n"
        f"📱 <b>Телефон:</b> {c['phone']}\n"
        f"📧 <b>Email:</b> {c['email']}\n"
        f"📍 <b>Адрес:</b> {c['address']}\n"
        f"🕐 <b>Режим работы:</b> {c['working_hours']}\n\n"
        f"Свяжитесь с нами удобным способом 👇"
    )
    await message.answer(text, reply_markup=contact_keyboard())


@dp.message(F.text == "✍️ Оставить заявку")
async def leave_request(message: types.Message):
    await message.answer(
        "✍️ <b>Оставить заявку</b>\n\n"
        "Напишите нам в свободной форме:\n"
        "— что вам нужно\n"
        "— ваш бюджет\n"
        "— сроки\n\n"
        f"Мы ответим в течение 30 минут в рабочее время.\n\n"
        f"📱 Или позвоните: <b>{COMPANY['contacts']['phone']}</b>",
        reply_markup=back_keyboard()
    )


@dp.callback_query(F.data.startswith("order_"))
async def order_service(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    service = COMPANY["services"][idx]
    await callback.message.answer(
        f"✍️ <b>Заявка на услугу: {service['name']}</b>\n\n"
        f"Опишите ваш проект и мы свяжемся с вами в ближайшее время.\n\n"
        f"📱 Телефон: <b>{COMPANY['contacts']['phone']}</b>\n"
        f"📧 Email: <b>{COMPANY['contacts']['email']}</b>",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer("Переходим к заявке!")


@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: types.CallbackQuery):
    await callback.message.answer(
        f"🏠 <b>Главное меню</b>\n\nЧем могу помочь?",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()


@dp.message()
async def unknown_message(message: types.Message):
    await message.answer(
        "❓ Не понимаю эту команду.\n\nВоспользуйтесь кнопками меню 👇",
        reply_markup=main_menu_keyboard()
    )


# ──────────────────────────────────────────────
# ЗАПУСК
# ──────────────────────────────────────────────

async def main():
    logger.info("Бот запущен ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
