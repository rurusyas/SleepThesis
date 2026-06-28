from telegram.ext import ApplicationBuilder
from config import API_BASE, BOT_TOKEN
from services.api_client import ApiClient
from handlers import (
    apnea,
    cancel,
    diary,
    focus,
    help as help_handler,
    history,
    leaderboard,
    profile,
    sounds,
    start,
    stats,
    tips,
)


async def post_init(application):
    application.bot_data["api"] = ApiClient(API_BASE)


async def post_shutdown(application):
    api = application.bot_data.get("api")
    if api:
        await api.close()


def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Conversation handlers (multi-step)
    app.add_handler(start.get_handler())
    app.add_handler(diary.get_handler())
    app.add_handler(apnea.get_handler())
    app.add_handler(focus.get_handler())

    # Single-shot handlers
    for h in tips.get_handlers():
        app.add_handler(h)
    for h in sounds.get_handlers():
        app.add_handler(h)
    for h in stats.get_handlers():
        app.add_handler(h)
    for h in leaderboard.get_handlers():
        app.add_handler(h)
    for h in profile.get_handlers():
        app.add_handler(h)
    for h in history.get_handlers():
        app.add_handler(h)
    for h in help_handler.get_handlers():
        app.add_handler(h)

    for h in cancel.get_handlers():
        app.add_handler(h)

    app.run_polling()


if __name__ == "__main__":
    main()
