from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game_logic import GameLogic
from database import Database

db = Database()
logic = GameLogic()

async def battle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = await db.get_player(user.id)
    if not player:
        await db.create_player(user.id, user.username)
        player = await db.get_player(user.id)

    enemy_name, enemy_stats = logic.get_random_enemy(player["level"])
    context.user_data["current_enemy"] = {"name": enemy_name, "stats": enemy_stats}

    keyboard = [
        [InlineKeyboardButton("⚔️ Атаковать", callback_data="attack:normal")],
        [InlineKeyboardButton("🛡️ Защита", callback_data="defend:shield")],
        [InlineKeyboardButton("🏃 Бежать", callback_data="flee:escape")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    battle_text = (
        f"⚡ **БОЙ НАЧАЛСЯ!** ⚡\n\n"
        f"Противник: **{enemy_name}**\n"
        f"❤️ HP: {enemy_stats['hp']} | ⚔️ Атака: {enemy_stats['attack']} | 🛡️ Защита: {enemy_stats['defense']}\n\n"
        f"Ваши характеристики:\n"
        f"❤️ HP: {player['hp']}/{player['max_hp']} | ⚔️ Атака: {player['attack']} | 🛡️ Защита: {player['defense']}"
    )
    await update.message.reply_text(battle_text, reply_markup=reply_markup, parse_mode="Markdown")

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    player = await db.get_player(user.id)
    enemy = context.user_data.get("current_enemy")

    if not enemy:
        await query.edit_message_text("Бой окончен. Используйте /battle для нового сражения.")
        return

    player_damage = logic.calculate_damage(player["attack"], enemy["stats"]["defense"])
    enemy["stats"]["hp"] -= player_damage

    if enemy["stats"]["hp"] <= 0:
        xp, gold = logic.calculate_battle_reward(enemy["name"])
        new_xp = player["xp"] + xp
        leveled_up, new_level, remaining_xp = logic.check_level_up(new_xp, player["level"])

        await db.update_player(user.id, xp=new_xp if not leveled_up else remaining_xp, level=new_level, gold=player["gold"] + gold)

        result = (
            f"🎉 **ПОБЕДА!** {enemy['name']} повержен!\n\n"
            f"Получено:\n"
            f"⭐ Опыт: +{xp}\n"
            f"💰 Золото: +{gold}\n"
            f"❤️ HP: {player['hp']}/{player['max_hp']}"
        )
        if leveled_up:
            result += f"\n\n🆙 **НОВЫЙ УРОВЕНЬ: {new_level}!**"
            await db.update_player(user.id, max_hp=player["max_hp"] + 25, hp=player["max_hp"] + 25, attack=player["attack"] + 3, defense=player["defense"] + 2)

        context.user_data.pop("current_enemy", None)
        await query.edit_message_text(result, parse_mode="Markdown")
        return

    enemy_damage = logic.calculate_damage(enemy["stats"]["attack"], player["defense"])
    new_player_hp = player["hp"] - enemy_damage

    if new_player_hp <= 0:
        await db.update_player(user.id, hp=1, gold=max(0, player["gold"] - player["gold"] // 4))
        await query.edit_message_text(f"💀 **ПОРАЖЕНИЕ!** {enemy['name']} одолел вас.\nПотеряно 25% золота. HP восстановлено до 1.", parse_mode="Markdown")
        return

    await db.update_player(user.id, hp=new_player_hp)

    keyboard = [
        [InlineKeyboardButton("⚔️ Атаковать", callback_data="attack:normal")],
        [InlineKeyboardButton("🛡️ Защита", callback_data="defend:shield")],
        [InlineKeyboardButton("🏃 Бежать", callback_data="flee:escape")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    battle_text = (
        f"Вы нанесли {player_damage} урона. У {enemy['name']} осталось {enemy['stats']['hp']} HP.\n"
        f"Вам нанесли {enemy_damage} урона. Ваше HP: {new_player_hp}/{player['max_hp']}"
    )
    await query.edit_message_text(battle_text, reply_markup=reply_markup)

async def defend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    player = await db.get_player(user.id)
    enemy = context.user_data.get("current_enemy")

    reduced_damage = max(1, enemy["stats"]["attack"] - player["defense"] * 2)
    new_hp = player["hp"] - reduced_damage

    if new_hp <= 0:
        await db.update_player(user.id, hp=1)
        await query.edit_message_text("💀 Поражение, несмотря на защиту.")
        return

    await db.update_player(user.id, hp=new_hp)
    await query.edit_message_text(f"🛡️ Защита уменьшила урон до {reduced_damage}. Ваше HP: {new_hp}/{player['max_hp']}")