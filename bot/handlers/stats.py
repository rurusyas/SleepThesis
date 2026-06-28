from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from keyboards.menu import main_menu
from services import orca_voice
from services.charts import weekly_diary_chart
from services.gamification import current_streak, depth_card_no_bar as depth_card


def _val(x, suffix=""):
    if x is None:
        return "нет данных"
    return f"{x}{suffix}"


async def _get_uid(update, context):
    if context.user_data.get("uid"):
        return context.user_data["uid"]
    user = update.effective_user
    uid = await context.application.bot_data["api"].ensure_user(str(user.id), user.full_name)
    if uid:
        context.user_data["uid"] = uid
    return uid


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = await _get_uid(update, context)
    if not uid:
        await update.message.reply_text(
            "Не смог получить профиль. Проверь API Orca.", reply_markup=main_menu()
        )
        return
    api = context.application.bot_data["api"]
    data = await api.get_stats(uid)
    if data is None:
        await update.message.reply_text(
            "Не смог получить статистику. Проверь API Orca.", reply_markup=main_menu()
        )
        return

    entries = await api.get_diary(uid) or []
    streak = current_streak([e.get("created_at") for e in entries])

    text = (
        "<b>Статистика недели</b>\n"
        f"<i>{orca_voice.NARR_STATS}</i>\n\n"
        f"{depth_card(streak)}\n\n"
        "<b>Дневник за 7 дней</b>\n"
        f"• Среднее качество сна  <b>{_val(data.get('avg_sleep_quality_7d'))}</b>\n"
        f"• Среднее настроение  <b>{_val(data.get('avg_mood_7d'))}</b>\n"
        f"• Средний стресс  <b>{_val(data.get('avg_stress_7d'))}</b>\n"
        f"• Записей всего  <b>{_val(data.get('entries'))}</b>\n\n"
        "<b>Фокус и апноэ</b>\n"
        f"• Минут фокуса за 7 дней  <b>{_val(data.get('focus_minutes_7d'))}</b>\n"
        f"• Проверок апноэ всего  <b>{_val(data.get('apnea_checks'))}</b>"
    )

    chart = None
    if entries:
        try:
            chart = weekly_diary_chart(entries)
        except Exception:
            chart = None

    if chart is not None and len(text) <= 1024:
        await update.message.reply_photo(
            photo=chart, caption=text, parse_mode="HTML", reply_markup=main_menu()
        )
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())
        if chart is not None:
            await update.message.reply_photo(photo=chart)


def get_handlers():
    return [
        CommandHandler("stats", stats),
        MessageHandler(filters.Regex("^Статистика$"), stats),
    ]
