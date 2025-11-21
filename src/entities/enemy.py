import pygame
from typing import Dict, Any, Optional


class Enemy:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.name = data.get("name", "Unknown")
        self.level = data.get("level", 1)
        self.enemy_type = data.get("enemy_type", "normal")

        # Stats
        self.health = data.get("health", 10)
        self.max_health = data.get("max_health", 10)
        self.damage = data.get("damage", 1)
        self.defense = data.get("defense", 0)
        self.magic_resistance = data.get("magic_resistance", 0)

        # Rewards
        self.experience_value = data.get("experience_value", 0)
        self.gold_min = data.get("gold_min", 0)
        self.gold_max = data.get("gold_max", 0)

        # Runtime state
        self.current_health = self.max_health
        self.image: Optional[pygame.Surface] = None

    def take_damage(self, amount: int) -> int:
        """Aplica dano ao inimigo e retorna o dano real causado"""
        actual_damage = max(1, amount - self.defense)
        self.current_health = max(0, self.current_health - actual_damage)
        return actual_damage

    def is_alive(self) -> bool:
        return self.current_health > 0
