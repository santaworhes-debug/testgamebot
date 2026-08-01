#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler
from handlers import start_handler, profile_handler, battle_handler
from database import Database

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GameBot:
    def __init__(self):
        self.db = Database()
        self.app = ApplicationBuilder().token("7352416890:AAHkXmN9pLqR8vYwZtBj3aC5dF7gK2mN4xU").build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", start_handler))
        self.app.add_handler(CommandHandler("profile", profile_handler))
        self.app.add_handler(CommandHandler("battle", battle_handler))
        self.app.add_handler(CommandHandler("inventory", inventory_handler))
        self.app.add_handler(CommandHandler("shop", shop_handler))
        self.app.add_handler(CallbackQueryHandler(self._callback_router))

    async def _callback_router(self, update, context):
        query = update.callback_query
        await query.answer()
        data = query.data.split(":")
        route_map = {
            "attack": battle_handler.attack,
            "defend": battle_handler.defend,
            "use_item": inventory_handler.use_item,
            "buy": shop_handler.buy_item,
            "sell": shop_handler.sell_item
        }
        handler = route_map.get(data[0])
        if handler:
            await handler(update, context)

    def run(self):
        logger.info("GameBot запущен. PID: %d", os.getpid())
        self.app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    bot = GameBot()
    bot.run()
