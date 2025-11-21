# src/database/datamaker/game_slots.py
from .table_creator import TableCreator


class GameSlotsTable(TableCreator):
    """Tabela de slots de jogo (5 slots para diferentes jogos/personagens)"""

    def __init__(self, db_manager):
        super().__init__(db_manager)

    def get_table_name(self) -> str:
        """Retorna o nome da tabela"""
        return "game_slots"

    def get_table_definition(self) -> str:
        """Define o schema da tabela game_slots"""
        return """
            CREATE TABLE IF NOT EXISTS game_slots (
                slot_id INTEGER PRIMARY KEY CHECK(slot_id IN (1, 2, 3, 4, 5)),
                player_name TEXT,
                player_class TEXT,
                player_level INTEGER DEFAULT 1,
                zone_name TEXT DEFAULT 'Início',
                playtime INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 0,
                FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
            )
        """

    def get_base_data(self) -> list:
        """Retorna dados base para os 5 slots vazios"""
        return [
            {"slot_id": 1, "player_name": None, "is_active": 0},
            {"slot_id": 2, "player_name": None, "is_active": 0},
            {"slot_id": 3, "player_name": None, "is_active": 0},
            {"slot_id": 4, "player_name": None, "is_active": 0},
            {"slot_id": 5, "player_name": None, "is_active": 0},
        ]

    def insert_base_data(self) -> bool:
        """
        Sobrescreve o método padrão para usar INSERT OR IGNORE.
        Isso evita que os slots existentes sejam resetados a cada reinício.
        """
        try:
            base_data = self.get_base_data()
            if not base_data:
                return True

            self.db_manager._ensure_connection()
            cursor = self.db_manager.connection.cursor()

            for data in base_data:
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])

                # USA INSERT OR IGNORE PARA NÃO SOBRESCREVER DADOS EXISTENTES
                cursor.execute(
                    f"INSERT OR IGNORE INTO {self.table_name} ({columns}) VALUES ({placeholders})",
                    list(data.values()),
                )

            self.db_manager.connection.commit()
            # print(f"✅ Slots de jogo verificados/inicializados")
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir dados base em {self.table_name}: {e}")
            return False
