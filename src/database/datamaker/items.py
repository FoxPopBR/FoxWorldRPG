# src/database/datamaker/items.py
from .table_creator import TableCreator

class ItemsTable(TableCreator):
    """Tabela de itens - Dados estáticos"""
    
    def get_table_name(self) -> str:
        return "items"
    
    def get_table_definition(self) -> str:
        return """
        CREATE TABLE items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            item_type TEXT NOT NULL,      -- 'weapon', 'armor', 'consumable', 'material', 'quest'
            subtype TEXT,                 -- 'sword', 'potion', 'herb', etc.
            rarity TEXT DEFAULT 'common', -- 'common', 'uncommon', 'rare', 'epic', 'legendary'
            description TEXT,
            
            -- Atributos de equipamento
            equip_slot TEXT,              -- 'weapon', 'head', 'chest', 'legs', 'accessory'
            required_level INTEGER DEFAULT 1,
            
            -- Modificadores de atributos (JSON)
            stat_bonuses TEXT,            -- {"forca": 2, "defesa": 5}
            
            -- Para armas
            damage_min INTEGER DEFAULT 0,
            damage_max INTEGER DEFAULT 0,
            damage_type TEXT DEFAULT 'physical', -- 'physical', 'magic', 'fire', 'ice', etc.
            attack_speed REAL DEFAULT 1.0,
            
            -- Para armaduras
            defense INTEGER DEFAULT 0,
            magic_defense INTEGER DEFAULT 0,
            
            -- Para consumíveis
            use_effect TEXT,              -- JSON com efeitos ao usar
            cooldown INTEGER DEFAULT 0,   -- Cooldown em segundos
            
            -- Propriedades gerais
            stackable BOOLEAN DEFAULT FALSE,
            max_stack INTEGER DEFAULT 1,
            value INTEGER DEFAULT 0,      -- Valor de venda
            weight REAL DEFAULT 0.0,
            
            -- Visual
            icon_path TEXT,
            color_hex TEXT DEFAULT '#FFFFFF',
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    def get_base_data(self):
        return [
            # ===== ARMAS =====
            {
                'name': 'Espada de Ferro',
                'item_type': 'weapon',
                'subtype': 'sword',
                'rarity': 'common',
                'description': 'Uma espada básica de ferro, confiável para iniciantes.',
                'equip_slot': 'weapon',
                'required_level': 1,
                'stat_bonuses': '{"forca": 1}',
                'damage_min': 8,
                'damage_max': 12,
                'damage_type': 'physical',
                'attack_speed': 1.0,
                'stackable': False,
                'max_stack': 1,
                'value': 50,
                'weight': 2.5,
                'icon_path': 'assets/images/items/iron_sword.png',
                'color_hex': '#C8C8C8'
            },
            {
                'name': 'Cajado do Aprendiz',
                'item_type': 'weapon', 
                'subtype': 'staff',
                'rarity': 'common',
                'description': 'Cajado simples para praticantes de magia.',
                'equip_slot': 'weapon',
                'required_level': 1,
                'stat_bonuses': '{"inteligencia": 2}',
                'damage_min': 4,
                'damage_max': 8,
                'damage_type': 'magic',
                'attack_speed': 1.2,
                'stackable': False,
                'max_stack': 1,
                'value': 45,
                'weight': 1.8,
                'icon_path': 'assets/images/items/apprentice_staff.png',
                'color_hex': '#E8D8A0'
            },
            
            # ===== ARMADURAS =====
            {
                'name': 'Armadura de Couro',
                'item_type': 'armor',
                'subtype': 'chest',
                'rarity': 'common',
                'description': 'Armadura leve feita de couro endurecido.',
                'equip_slot': 'chest',
                'required_level': 1,
                'stat_bonuses': '{"defesa": 8, "destreza": 1}',
                'defense': 8,
                'magic_defense': 2,
                'stackable': False,
                'max_stack': 1,
                'value': 35,
                'weight': 3.0,
                'icon_path': 'assets/images/items/leather_armor.png',
                'color_hex': '#8B4513'
            },
            {
                'name': 'Elmo de Ferro',
                'item_type': 'armor',
                'subtype': 'head',
                'rarity': 'common',
                'description': 'Elmo básico de proteção.',
                'equip_slot': 'head',
                'required_level': 1,
                'stat_bonuses': '{"defesa": 5}',
                'defense': 5,
                'magic_defense': 1,
                'stackable': False,
                'max_stack': 1,
                'value': 20,
                'weight': 1.5,
                'icon_path': 'assets/images/items/iron_helmet.png',
                'color_hex': '#A0A0A0'
            },
            
            # ===== CONSUMÍVEIS =====
            {
                'name': 'Poção de Cura Pequena',
                'item_type': 'consumable',
                'subtype': 'potion',
                'rarity': 'common',
                'description': 'Restaura 50 pontos de vida.',
                'use_effect': '{"restore_health": 50}',
                'cooldown': 10,
                'stackable': True,
                'max_stack': 10,
                'value': 15,
                'weight': 0.5,
                'icon_path': 'assets/images/items/health_potion_small.png',
                'color_hex': '#FF4444'
            },
            {
                'name': 'Poção de Mana Pequena',
                'item_type': 'consumable',
                'subtype': 'potion', 
                'rarity': 'common',
                'description': 'Restaura 30 pontos de mana.',
                'use_effect': '{"restore_mana": 30}',
                'cooldown': 10,
                'stackable': True,
                'max_stack': 10,
                'value': 20,
                'weight': 0.5,
                'icon_path': 'assets/images/items/mana_potion_small.png',
                'color_hex': '#4444FF'
            },
            
            # ===== MATERIAIS =====
            {
                'name': 'Pele de Goblin',
                'item_type': 'material',
                'subtype': 'hide',
                'rarity': 'common',
                'description': 'Pele resistente de Goblin, usada em fabricação.',
                'stackable': True,
                'max_stack': 20,
                'value': 5,
                'weight': 0.3,
                'icon_path': 'assets/images/items/goblin_hide.png',
                'color_hex': '#8FBC8F'
            },
            {
                'name': 'Dente de Lobo',
                'item_type': 'material',
                'subtype': 'tooth',
                'rarity': 'common',
                'description': 'Dente afiado de lobo, útil para artesanato.',
                'stackable': True,
                'max_stack': 30,
                'value': 3,
                'weight': 0.1,
                'icon_path': 'assets/images/items/wolf_tooth.png',
                'color_hex': '#F0F0F0'
            }
        ]