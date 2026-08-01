import random
from typing import Tuple, Dict
from config import BASE_XP, XP_MULTIPLIER, MAX_LEVEL

class GameLogic:
    ENEMIES = {
        "Гоблин": {"hp": 30, "attack": 8, "defense": 2, "xp_reward": 25, "gold_reward": (5, 15)},
        "Скелет": {"hp": 45, "attack": 12, "defense": 4, "xp_reward": 40, "gold_reward": (10, 25)},
        "Орк": {"hp": 70, "attack": 18, "defense": 8, "xp_reward": 75, "gold_reward": (20, 50)},
        "Тролль": {"hp": 120, "attack": 25, "defense": 12, "xp_reward": 150, "gold_reward": (50, 120)},
        "Дракон": {"hp": 300, "attack": 45, "defense": 25, "xp_reward": 500, "gold_reward": (200, 600)}
    }

    ITEMS = {
        "healing_potion": {"name": "Зелье здоровья", "type": "consumable", "hp_restore": 50, "buy_price": 30, "sell_price": 15},
        "mana_potion": {"name": "Зелье маны", "type": "consumable", "mp_restore": 30, "buy_price": 25, "sell_price": 12},
        "iron_sword": {"name": "Железный меч", "type": "weapon", "attack_bonus": 15, "buy_price": 150, "sell_price": 75},
        "steel_armor": {"name": "Стальная броня", "type": "armor", "defense_bonus": 10, "buy_price": 200, "sell_price": 100},
        "fire_scroll": {"name": "Свиток огня", "type": "consumable", "damage": 80, "buy_price": 100, "sell_price": 50}
    }

    @staticmethod
    def calculate_damage(attack: int, defense: int) -> int:
        base_damage = max(1, attack - defense // 2)
        variance = random.uniform(0.85, 1.15)
        return max(1, int(base_damage * variance))

    @staticmethod
    def xp_for_level(level: int) -> int:
        return int(BASE_XP * (level ** XP_MULTIPLIER))

    @classmethod
    def get_random_enemy(cls, player_level: int) -> Tuple[str, Dict]:
        available = [e for e in cls.ENEMIES.items() if cls.ENEMIES[e[0]]["xp_reward"] <= player_level * 50]
        if not available:
            return random.choice(list(cls.ENEMIES.items()))
        weights = [1 / (abs( enemy[1]["xp_reward"] - player_level * 25) + 1) for enemy in available]
        return random.choices(available, weights=weights, k=1)[0]

    @classmethod
    def calculate_battle_reward(cls, enemy_name: str) -> Tuple[int, int]:
        enemy = cls.ENEMIES[enemy_name]
        xp = enemy["xp_reward"]
        gold = random.randint(*enemy["gold_reward"])
        return xp, gold

    @staticmethod
    def check_level_up(current_xp: int, current_level: int) -> Tuple[bool, int, int]:
        required_xp = GameLogic.xp_for_level(current_level)
        if current_xp >= required_xp and current_level < MAX_LEVEL:
            new_level = current_level + 1
            remaining_xp = current_xp - required_xp
            return True, new_level, remaining_xp
        return False, current_level, current_xp