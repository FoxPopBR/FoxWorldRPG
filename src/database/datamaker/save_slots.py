# src/database/datamaker/save_slots.py
from .table_creator import TableCreator


class SaveSlotsTable(TableCreator):
    """Tabela de slots de save do jogo"""

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def get_table_name(self) -> str:
        """Retorna o nome da tabela"""
        return "save_slots"

    def get_table_definition(self) -> str:
        """Define o schema da tabela save_slots"""
        return """
            CREATE TABLE IF NOT EXISTS save_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_slot_id INTEGER NOT NULL CHECK(game_slot_id IN (1, 2, 3, 4, 5)),
                save_slot_id INTEGER NOT NULL CHECK(save_slot_id IN (1, 2, 3)),
                slot_type TEXT NOT NULL CHECK(slot_type IN ('auto', 'manual')),
                save_type TEXT DEFAULT 'manual',
                save_title TEXT DEFAULT 'Save sem título',
                save_description TEXT DEFAULT '',
                hero_name TEXT,
                hero_level INTEGER DEFAULT 1,
                hero_class TEXT,
                zone_name TEXT DEFAULT 'Início',
                zone_id INTEGER DEFAULT 1,
                playtime INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 0,
                FOREIGN KEY (game_slot_id) REFERENCES game_slots(slot_id) ON DELETE CASCADE,
                FOREIGN KEY (hero_name) REFERENCES players(name) ON DELETE SET NULL,
                UNIQUE(game_slot_id, save_slot_id)
            )
        """

    def get_base_data(self) -> list:
        """Saves são criados dinamicamente quando um game slot é usado"""
        return []
