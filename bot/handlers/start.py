from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from keyboards.menu import main_menu, scale_keyboard
from services import orca_voice


(
    SLEEP_HOURS,
    SLEEP_LATENCY,
    WAKE_FEELING,
    BEDTIME_REGULARITY,
    STRESS_FREQ,
    THOUGHTS_RACING,
    OVERLOAD,
    FOCUS_DIFFICULTY,
    DISTRACTION,
) = range(9)


CANCEL_TOKENS = {"Отмена", "отмена", "/cancel", "Cancel", "cancel"}


questions = [
    ("sleep_hours",
     "Сколько часов ты обычно спишь? Можно ответить числом, например <b>7.5</b>.",
     SLEEP_HOURS, "free"),
    ("sleep_latency_min",
     "За сколько минут ты обычно засыпаешь?",
     SLEEP_LATENCY, "free"),
    ("wake_feeling",
     "Как ты обычно чувствуешь себя после пробуждения? <b>1</b> — разбито, <b>5</b> — отлично.",
     WAKE_FEELING, "scale"),
    ("bedtime_regularity",
     "Насколько регулярно ты ложишься спать в одно и то же время? <b>1</b> — хаос, <b>5</b> — стабильно.",
     BEDTIME_REGULARITY, "scale"),
    ("stress_freq",
     "Как часто ты чувствуешь стресс? <b>1</b> — редко, <b>5</b> — почти постоянно.",
     STRESS_FREQ, "scale"),
    ("thoughts_racing",
     "Как часто мысли мешают расслабиться? <b>1</b> — редко, <b>5</b> — очень часто.",
     THOUGHTS_RACING, "scale"),
    ("overload",
     "Как часто ты чувствуешь перегруз? <b>1</b> — редко, <b>5</b> — очень часто.",
     OVERLOAD, "scale"),
    ("focus_difficulty",
     "Насколько сложно тебе концентрироваться? <b>1</b> — легко, <b>5</b> — очень сложно.",
     FOCUS_DIFFICULTY, "scale"),
    ("distraction",
     "Как часто отвлекаешься? <b>1</b> — редко, <b>5</b> — постоянно.",
     DISTRACTION, "scale"),
]


WELCOME = (
    "<b>Привет. Я Orca.</b>\n"
    "Косатка, которая плавает рядом и помогает тебе со сном, стрессом и фокусом.\n\n"
    "<i>Сейчас короткий онбординг — 9 вопросов на пару минут. "
    "Из ответов я посчитаю твои индексы Сна, Стресса и Фокуса.</i>\n\n"
    "<blockquote>"
    "Цифры — это начальная точка, от которой "
    "видно прогресс."
    "</blockquote>"
)


def _is_cancel(text: str) -> bool:
    return text.strip() in CANCEL_TOKENS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["onboarding"] = {}
    context.user_data["onboarding_state"] = 0
    await update.message.reply_text(WELCOME, parse_mode="HTML")
    first_q = questions[0]
    await update.message.reply_text(first_q[1], parse_mode="HTML")
    return first_q[2]


def parse_float(text):
    try:
        x = float(text.replace(",", "."))
        if x < 0:
            return None
        return x
    except ValueError:
        return None


def parse_scale(text):
    try:
        x = int(text)
        if 1 <= x <= 5:
            return x
        return None
    except ValueError:
        return None


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("onboarding", None)
    context.user_data.pop("onboarding_state", None)
    await update.message.reply_text(
        "Окей, остановились. Можно вернуться к онбордингу командой /start.",
        reply_markup=main_menu(),
    )
    return ConversationHandler.END


async def save_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if _is_cancel(text):
        return await cancel(update, context)
    state = context.user_data.get("onboarding_state", 0)
    key, _prompt, _state_id, kind = questions[state]

    if kind == "free":
        value = parse_float(text)
        if value is None:
            await update.message.reply_text("Нужно неотрицательное число. Например: <b>7.5</b>",
                                            parse_mode="HTML")
            return _state_id
    else:
        value = parse_scale(text)
        if value is None:
            await update.message.reply_text("Нужно число от 1 до 5.", reply_markup=scale_keyboard())
            return _state_id

    context.user_data["onboarding"][key] = value
    next_state = state + 1

    if next_state >= len(questions):
        user = update.effective_user
        api = context.application.bot_data["api"]
        await update.message.reply_text("Считаю индексы…")
        data = await api.create_user(str(user.id), user.full_name, context.user_data["onboarding"])
        if not data:
            await update.message.reply_text(
                "Не смог сохранить профиль. Проверь, что API Orca запущен.",
                reply_markup=main_menu(),
            )
            return ConversationHandler.END
        context.user_data["uid"] = data["id"]
        result = (
            "<b>Готово · профиль создан</b>\n\n"
            f"Индексы Orca:\n"
            f"• Сон  <b>{data.get('sleep_index')}</b>\n"
            f"• Стресс  <b>{data.get('stress_index')}</b>\n"
            f"• Фокус  <b>{data.get('focus_index')}</b>\n\n"
            f"<i>{orca_voice.greeting()}</i>\n\n"
            "Дальше — кнопки в меню. Подсказка по командам — /help."
        )
        await update.message.reply_text(result, parse_mode="HTML", reply_markup=main_menu())
        context.user_data.pop("onboarding", None)
        context.user_data.pop("onboarding_state", None)
        return ConversationHandler.END

    context.user_data["onboarding_state"] = next_state
    q_key, q_prompt, _, q_kind = questions[next_state]
    markup = scale_keyboard() if q_kind == "scale" else None
    await update.message.reply_text(q_prompt, parse_mode="HTML", reply_markup=markup)
    return next_state


def get_handler():
    step = [MessageHandler(filters.TEXT & ~filters.COMMAND, save_answer)]
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={s: step for s in range(9)},
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex("^Отмена$"), cancel),
        ],
        allow_reentry=True,
    )
