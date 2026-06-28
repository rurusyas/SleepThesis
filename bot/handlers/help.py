from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from keyboards.menu import main_menu
from services import orca_voice


HELP_TEXT = (
    "<b>Orca · справка</b>\n"
    f"<i>{orca_voice.NARR_HELP}</i>\n\n"
    "<b>Главные действия</b>\n"
    "• <b>Дневник</b> — три цифры за минуту: настроение, энергия, стресс, сон.\n"
    "• <b>История</b> — последние записи и стрик за 30 дней.\n"
    "• <b>Статистика</b> — средние за неделю, индексы Orca, график.\n"
    "• <b>Профиль</b> — твоя глубина погружения и индексы из онбординга.\n\n"
    "<b>Глубже</b>\n"
    "• <b>Апноэ</b> — пришли голосовое или аудио, модель проверит дыхание.\n"
    "• <b>Фокус</b> — запиши минуты концентрации (25 / 50 / своё).\n"
    "• <b>Звуки</b> — список процедурных звуков для сна и работы.\n"
    "• <b>Советы по сну</b> — десять карточек: сон, циркадные ритмы, апноэ, фокус.\n"
    "• <b>Лидерборд</b> — топ по среднему качеству сна за 7 дней.\n\n"
    "<b>Команды</b>\n"
    "<code>/start</code>  — заново пройти онбординг\n"
    "<code>/diary</code>  — открыть дневник\n"
    "<code>/history</code>  — посмотреть свои записи\n"
    "<code>/stats</code>  — статистика недели\n"
    "<code>/profile</code>  — индексы и глубина\n"
    "<code>/apnea</code>  — анализ апноэ\n"
    "<code>/focus</code>  — добавить фокус-сессию\n"
    "<code>/sounds</code>  — звуки\n"
    "<code>/sleep_tips</code>  — карточки\n"
    "<code>/leaderboard</code>  — лидерборд\n"
    "<code>/help</code>  — этот экран\n"
    "<code>/cancel</code>  — выйти из текущего диалога\n\n"
    "<blockquote expandable>"
    "Orca - не врач и не диагностический инструмент. Если что-то серьёзно "
    "беспокоит со сном или дыханием, обращайся к специалисту. Бот создан, чтобы наладить режим, "
    "рефлексию и привычки."
    "</blockquote>"
)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML", reply_markup=main_menu())


def get_handlers():
    return [
        CommandHandler("help", help_cmd),
        MessageHandler(filters.Regex("^Помощь$"), help_cmd),
    ]
