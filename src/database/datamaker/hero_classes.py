# src/database/datamaker/hero_classes.py
from .table_creator import TableCreator


class HeroClassesTable(TableCreator):
    """Tabela de classes de heróis - INTEGRADO COM HeroClass enum existente"""

    def get_table_name(self) -> str:
        return "hero_classes"

    def get_table_definition(self) -> str:
        return """
        CREATE TABLE hero_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_key TEXT NOT NULL UNIQUE,  -- Corresponde ao HeroClass enum
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            strength_bonus INTEGER DEFAULT 0,
            dexterity_bonus INTEGER DEFAULT 0,
            vitality_bonus INTEGER DEFAULT 0,
            intelligence_bonus INTEGER DEFAULT 0,
            armor_bonus INTEGER DEFAULT 0,
            energy_bonus INTEGER DEFAULT 0,
            stamina_bonus INTEGER DEFAULT 0,
            primary_attribute TEXT NOT NULL,
            color_hex TEXT NOT NULL,
            icon_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

    def get_base_data(self):
        """Dados base que correspondem ao HeroClass enum e character_creation_state.py"""
        return [
            {
                "id": 1,
                "class_key": "barbaro",
                "name": "BARBARO",
                "description": "Guerreiro feroz com força bruta e resistencia inigualavel.",
                "strength_bonus": 3,
                "dexterity_bonus": 1,
                "vitality_bonus": 2,
                "intelligence_bonus": 0,
                "armor_bonus": 1,
                "energy_bonus": 0,
                "stamina_bonus": 2,
                "primary_attribute": "forca",
                "color_hex": "#B43C3C",
                "icon_path": "assets/images/classes/barbarian_icon.png",
            },
            {
                "id": 2,
                "class_key": "paladino",
                "name": "PALADINO",
                "description": "Cavaleiro sagrado abencoado com poderes divinos.",
                "strength_bonus": 2,
                "dexterity_bonus": 1,
                "vitality_bonus": 2,
                "intelligence_bonus": 1,
                "armor_bonus": 3,
                "energy_bonus": 1,
                "stamina_bonus": 1,
                "primary_attribute": "armadura",
                "color_hex": "#F0C850",
                "icon_path": "assets/images/classes/paladin_icon.png",
            },
            {
                "id": 3,
                "class_key": "druida",
                "name": "DRUIDA",
                "description": "Mestre da natureza com poderes de transformacao e cura.",
                "strength_bonus": 1,
                "dexterity_bonus": 2,
                "vitality_bonus": 1,
                "intelligence_bonus": 2,
                "armor_bonus": 1,
                "energy_bonus": 2,
                "stamina_bonus": 1,
                "primary_attribute": "inteligencia",
                "color_hex": "#3C9650",
                "icon_path": "assets/images/classes/druid_icon.png",
            },
            {
                "id": 4,
                "class_key": "feiticeiro",
                "name": "FEITICEIRO",
                "description": "Conjurador de magias arcanas elementais.",
                "strength_bonus": 0,
                "dexterity_bonus": 2,
                "vitality_bonus": 1,
                "intelligence_bonus": 3,
                "armor_bonus": 0,
                "energy_bonus": 3,
                "stamina_bonus": 0,
                "primary_attribute": "inteligencia",
                "color_hex": "#5064C8",
                "icon_path": "assets/images/classes/sorcerer_icon.png",
            },
            {
                "id": 5,
                "class_key": "necromante",
                "name": "NECROMANTE",
                "description": "Manipulador das trevas com dominio sobre a vida e morte.",
                "strength_bonus": 0,
                "dexterity_bonus": 1,
                "vitality_bonus": 1,
                "intelligence_bonus": 3,
                "armor_bonus": 1,
                "energy_bonus": 2,
                "stamina_bonus": 0,
                "primary_attribute": "inteligencia",
                "color_hex": "#643296",
                "icon_path": "assets/images/classes/necromancer_icon.png",
            },
        ]
