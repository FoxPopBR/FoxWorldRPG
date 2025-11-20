# src/database/datamaker/quests.py
from .table_creator import TableCreator

class QuestsTable(TableCreator):
    """Tabela de missões - Dados estáticos"""
    
    def get_table_name(self) -> str:
        return "quests"
    
    def get_table_definition(self) -> str:
        return """
        CREATE TABLE quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            quest_giver TEXT NOT NULL,   -- Nome do NPC que dá a missão
            zone_id INTEGER DEFAULT 1,
            
            -- Requisitos
            required_level INTEGER DEFAULT 1,
            required_quests TEXT,        -- JSON com IDs de pré-requisitos
            required_faction TEXT,       -- Fação necessária
            required_reputation INTEGER DEFAULT 0,
            
            -- Objetivos (JSON)
            objectives TEXT NOT NULL,
            
            -- Recompensas (JSON)
            rewards TEXT NOT NULL,
            
            -- Progresso e tracking
            is_repeatable BOOLEAN DEFAULT FALSE,
            cooldown_hours INTEGER DEFAULT 0, -- Para missões repetíveis
            time_limit_minutes INTEGER DEFAULT 0, -- 0 = sem limite de tempo
            
            -- Categorização
            quest_type TEXT DEFAULT 'main', -- 'main', 'side', 'daily', 'event'
            difficulty TEXT DEFAULT 'normal', -- 'easy', 'normal', 'hard', 'epic'
            
            -- Flags especiais
            is_auto_start BOOLEAN DEFAULT FALSE,
            is_hidden BOOLEAN DEFAULT FALSE,
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    def get_base_data(self):
        return [
            {
                'title': 'Ameaça Goblin',
                'description': 'Os goblins estão atacando viajantes perto da vila. Derrote 5 goblins para proteger a região.',
                'quest_giver': 'Capitão da Guarda',
                'zone_id': 1,
                'required_level': 1,
                'required_quests': '[]',
                'objectives': '{"kill_goblins": {"target": "Goblin", "count": 5, "current": 0}}',
                'rewards': '{"experience": 100, "gold": 50, "items": [1]}',
                'is_repeatable': False,
                'cooldown_hours': 0,
                'time_limit_minutes': 0,
                'quest_type': 'main',
                'difficulty': 'easy',
                'is_auto_start': False,
                'is_hidden': False
            },
            {
                'title': 'Peles de Lobo',
                'description': 'Os lobos da floresta estão se tornando agressivos. Colete 3 peles de lobo para o ferreiro.',
                'quest_giver': 'Ferreiro Gunnar',
                'zone_id': 1,
                'required_level': 2,
                'required_quests': '[1]',
                'objectives': '{"collect_wolf_hides": {"item_id": 4, "count": 3, "current": 0}}',
                'rewards': '{"experience": 150, "gold": 75, "items": [2]}',
                'is_repeatable': True,
                'cooldown_hours': 24,
                'time_limit_minutes': 0,
                'quest_type': 'side',
                'difficulty': 'normal',
                'is_auto_start': False,
                'is_hidden': False
            },
            {
                'title': 'Ervas Medicinais',
                'description': 'A curandeira precisa de ervas raras para preparar remédios. Encontre 5 ervas brilhantes na floresta.',
                'quest_giver': 'Curandeira Elara',
                'zone_id': 1,
                'required_level': 1,
                'required_quests': '[]',
                'objectives': '{"collect_herbs": {"item_id": 5, "count": 5, "current": 0}}',
                'rewards': '{"experience": 80, "gold": 40, "items": [6, 7]}',
                'is_repeatable': False,
                'cooldown_hours': 0,
                'time_limit_minutes': 60,  # 1 hora para completar
                'quest_type': 'side',
                'difficulty': 'easy',
                'is_auto_start': True,
                'is_hidden': False
            },
            {
                'title': 'O Feiticeiro das Trevas',
                'description': 'Um poderoso feiticeiro das trevas está ameaçando a região. Derrote-o para restaurar a paz.',
                'quest_giver': 'Capitão da Guarda',
                'zone_id': 2,
                'required_level': 5,
                'required_quests': '[1, 2]',
                'objectives': '{"defeat_dark_mage": {"target": "Dark Mage", "count": 1, "current": 0}}',
                'rewards': '{"experience": 300, "gold": 150, "items": [3], "reputation": 50}',
                'is_repeatable': False,
                'cooldown_hours': 0,
                'time_limit_minutes': 0,
                'quest_type': 'main',
                'difficulty': 'hard',
                'is_auto_start': False,
                'is_hidden': False
            }
        ]