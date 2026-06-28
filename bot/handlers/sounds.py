from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from config import MINIAPP_URL
from services import orca_voice


# id -> (emoji, friendly description)
_SOUND_META = {
    "white-noise":  ("⚪️", "ровный, маскирует шум комнаты"),
    "pink-noise":   ("🌸", "мягче белого, многие лучше засыпают под него"),
    "brown-noise":  ("🟤", "глубокий низкий шум, эффект «гудит океан»"),
    "ocean-waves":  ("🌊", "медленные накатывающие волны"),
    "rain":         ("🌧",  "плотный дождь по крыше"),
    "crackle":      ("🔥",  "треск костра, негромкий и тёплый"),
    "night-drone":  ("🌌",  "ночной гул — как будто город спит"),
    "fan":          ("💨",  "вентилятор: ровный, чуть колеблется"),
}


async def sounds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>Звуки для сна и фокуса</b>\n\n"
        "Воспроизведение — в приложении Orca, с таймером и плавным fade-out.\n\n"
        "Доступны в MiniApp: https://t.me/orca_miniapp_bot/orcathesleepwhale"
    )

    markup = None
    if MINIAPP_URL:
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Открыть Orca", web_app=WebAppInfo(url=MINIAPP_URL))]]
        )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=markup)


def get_handlers():
    return [
        CommandHandler("sounds", sounds),
        MessageHandler(filters.Regex("^Звуки$"), sounds),
    ]
