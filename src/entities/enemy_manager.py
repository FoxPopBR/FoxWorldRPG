import pygame
from typing import Dict, List, Optional
from .enemy import Enemy


class EnemyManager:
    """Gerencia inimigos e seus assets"""

    def __init__(self, database, resource_manager=None):
        self.database = database
        self.resource_manager = resource_manager
        self.enemies_cache: Dict[int, Enemy] = {}

    def get_enemy(self, enemy_id: int) -> Optional[Enemy]:
        """Retorna uma instância de inimigo pelo ID"""
        # Não cacheamos instâncias únicas para batalha, pois cada batalha deve ter sua instância
        # Mas podemos cachear protótipos se necessário.
        # Por enquanto, cria nova instância sempre para garantir estado limpo (HP cheio)

        data = self.database.get_enemy_by_id(enemy_id)
        if data:
            enemy = Enemy(data)
            self._load_enemy_assets(enemy)
            return enemy
        return None

    def get_all_enemies(self) -> List[Enemy]:
        """Retorna lista de todos os inimigos (para bestiário ou debug)"""
        data_list = self.database.get_all_enemies()
        enemies = []
        for data in data_list:
            enemy = Enemy(data)
            self._load_enemy_assets(enemy)
            enemies.append(enemy)
        return enemies

    def _load_enemy_assets(self, enemy: Enemy):
        """Carrega a imagem do inimigo"""
        if self.resource_manager:
            enemy.image = self.resource_manager.get_enemy_image(enemy.name)
