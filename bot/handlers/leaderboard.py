from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from keyboards.menu import main_menu
from services import orca_voice
from services.charts import leaderboard_chart


async def _get_uid(update, context):
    if context.user_data.get("uid"):
        return context.user_data["uid"]
    user = update.effective_user
    uid = await context.application.bot_data["api"].ensure_user(str(user.id), user.full_name)
    if uid:
        context.user_data["uid"] = uid
    return uid


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = await _get_uid(update, context)
    api = context.application.bot_data["api"]
    rows = await api.get_leaderboard()

    if rows is None:
        await update.message.reply_text(
            "Не смог получить лидерборд. Проверь API Orca.", reply_markup=main_menu()
        )
        return

    if not rows:
        text = (
            "<b>Лидерборд Orca</b>\n"
            f"<i>{orca_voice.NARR_LEADERBOARD}</i>\n\n"
            "Пока пусто. Будь первым — заполни дневник за неделю, и появишься в топе."
        )
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu())
        return

    # Build textual top with user's place
    you_idx = None
    for i, row in enumerate(rows, start=1):
        if uid and row.get("user_id") == uid:
            you_idx = i
            break

    lines = [
        "<b>Лидерборд Orca</b>",
        f"<i>{orca_voice.NARR_LEADERBOARD}</i>",
        "",
        "\n<b>Топ-10</b>\n",
    ]
    for i, row in enumerate(rows[:10], start=1):
        name = row.get("name") or "Без имени"
        score = row.get("score")
        marker = " ←  ты" if uid and row.get("user_id") == uid else ""
        rank = f"<b>{i}.</b>" if i > 3 else ["★", "✦", "✧"][i - 1]
        lines.append(f"{rank}  {name}  —  <b>{score}</b>{marker}")

    if you_idx is None and uid is not None:
        # Find user beyond top 10
        for i, row in enumerate(rows, start=1):
            if row.get("user_id") == uid:
                you_idx = i
                break

    if you_idx is not None and you_idx > 10:
        lines.append("")
        lines.append(f"<i>Твоё место: {you_idx} из {len(rows)}.</i>")
    elif you_idx is None and uid is not None:
        lines.append("")
        lines.append("<i>Тебя ещё нет в рейтинге — нужно хотя бы одну запись в дневнике за 7 дней.</i>")

    lines.append("\n")
    lines.append(
        "<blockquote>Балл — среднее качество сна (1-5) "
        "за последние 7 дней по твоим записям в дневнике.</blockquote>"
    )
    text = "\n".join(lines)

    chart = None
    try:
        chart = leaderboard_chart(rows, current_uid=uid)
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
        CommandHandler("leaderboard", leaderboard),
        MessageHandler(filters.Regex("^Лидерборд$"), leaderboard),
    ]
