# src/database/datamaker/enemies.py
from .table_creator import TableCreator

class EnemiesTable(TableCreator):
    """Tabela de inimigos - Dados estáticos"""
    
    def get_table_name(self) -> str:
        return "enemies"
    
    def get_table_definition(self) -> str:
        return """
        CREATE TABLE enemies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            level INTEGER DEFAULT 1,
            enemy_type TEXT NOT NULL,  -- 'normal', 'elite', 'boss', 'mini_boss'
            health INTEGER NOT NULL,
            max_health INTEGER NOT NULL,
            damage INTEGER NOT NULL,
            defense INTEGER NOT NULL,
            magic_resistance INTEGER DEFAULT 0,
            experience_value INTEGER NOT NULL,
            gold_min INTEGER DEFAULT 0,
            gold_max INTEGER DEFAULT 0,
            zone_id INTEGER DEFAULT 1,
            spawn_chance REAL DEFAULT 1.0,
            spawn_conditions TEXT,     -- JSON com condições de spawn
            abilities TEXT,            -- JSON com habilidades
            drops TEXT,                -- JSON com itens dropáveis
            resistances TEXT,          -- JSON com resistências
            weaknesses TEXT,           -- JSON com fraquezas
            ai_behavior TEXT DEFAULT 'aggressive', -- 'passive', 'aggressive', 'defensive'
            sprite_path TEXT,
            scale_factor REAL DEFAULT 1.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    def get_base_data(self):
        return [
            {
                'name': 'Goblin',
                'level': 1,
                'enemy_type': 'normal',
                'health': 30,
                'max_health': 30,
                'damage': 8,
                'defense': 3,
                'magic_resistance': 1,
                'experience_value': 15,
                'gold_min': 2,
                'gold_max': 8,
                'zone_id': 1,
                'spawn_chance': 0.7,
                'spawn_conditions': '{"time": "any", "weather": "any"}',
                'abilities': '["basic_attack", "flee_low_health"]',
                'drops': '[{"item_id": 1, "chance": 0.3, "min_quantity": 1, "max_quantity": 1}]',
                'resistances': '{"physical": 0.9}',
                'weaknesses': '{"fire": 1.2}',
                'ai_behavior': 'aggressive',
                'sprite_path': 'assets/images/enemies/goblin.png',
                'scale_factor': 1.0
            },
            {
                'name': 'Orc Warrior',
                'level': 3,
                'enemy_type': 'normal', 
                'health': 65,
                'max_health': 65,
                'damage': 15,
                'defense': 8,
                'magic_resistance': 2,
                'experience_value': 35,
                'gold_min': 5,
                'gold_max': 15,
                'zone_id': 1,
                'spawn_chance': 0.4,
                'spawn_conditions': '{"time": "any", "weather": "any"}',
                'abilities': '["strong_attack", "taunt", "berserk_low_health"]',
                'drops': '[{"item_id": 2, "chance": 0.4, "min_quantity": 1, "max_quantity": 1}]',
                'resistances': '{"physical": 0.8, "fire": 1.1}',
                'weaknesses': '{"ice": 1.3}',
                'ai_behavior': 'aggressive',
                'sprite_path': 'assets/images/enemies/orc_warrior.png',
                'scale_factor': 1.1
            },
            {
                'name': 'Dark Mage',
                'level': 5,
                'enemy_type': 'elite',
                'health': 45,
                'max_health': 45,
                'damage': 22,
                'defense': 4,
                'magic_resistance': 15,
                'experience_value': 60,
                'gold_min': 10,
                'gold_max': 25,
                'zone_id': 2,
                'spawn_chance': 0.2,
                'spawn_conditions': '{"time": "night", "weather": "any"}',
                'abilities': '["fire_ball", "dark_burst", "teleport", "summon_minions"]',
                'drops': '[{"item_id": 3, "chance": 0.6, "min_quantity": 1, "max_quantity": 1}]',
                'resistances': '{"magic": 0.6, "dark": 0.5}',
                'weaknesses': '{"holy": 1.5, "physical": 1.3}',
                'ai_behavior': 'defensive',
                'sprite_path': 'assets/images/enemies/dark_mage.png',
                'scale_factor': 1.0
            },
            {
                'name': 'Forest Wolf',
                'level': 2,
                'enemy_type': 'normal',
                'health': 40,
                'max_health': 40,
                'damage': 12,
                'defense': 5,
                'magic_resistance': 0,
                'experience_value': 20,
                'gold_min': 0,
                'gold_max': 5,
                'zone_id': 1,
                'spawn_chance': 0.5,
                'spawn_conditions': '{"time": "any", "weather": "any"}',
                'abilities': '["quick_attack", "howl", "pack_tactics"]',
                'drops': '[{"item_id": 4, "chance": 0.2, "min_quantity": 1, "max_quantity": 2}]',
                'resistances': '{"ice": 1.2}',
                'weaknesses': '{"fire": 1.3}',
                'ai_behavior': 'aggressive',
                'sprite_path': 'assets/images/enemies/forest_wolf.png',
                'scale_factor': 1.0
            }
        ]