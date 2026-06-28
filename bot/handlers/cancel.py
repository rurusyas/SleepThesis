from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from keyboards.menu import main_menu


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("onboarding", None)
    context.user_data.pop("onboarding_state", None)
    context.user_data.pop("diary_draft", None)
    context.user_data.pop("focus_min", None)
    await update.message.reply_text(
        "Окей, остановились. Главное меню ниже.",
        reply_markup=main_menu(),
    )


def get_handlers():
    return [
        CommandHandler("cancel", cancel),
        MessageHandler(filters.Regex("^Отмена$"), cancel),
    ]
