# src/database/datamaker/shops.py
from .table_creator import TableCreator

class ShopsTable(TableCreator):
    """Tabela de lojas - Dados estáticos"""
    
    def get_table_name(self) -> str:
        return "shops"
    
    def get_table_definition(self) -> str:
        return """
        CREATE TABLE shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            owner_npc_id INTEGER NOT NULL,
            shop_type TEXT NOT NULL,     -- 'general', 'weapon', 'armor', 'potion', 'magic'
            
            -- Itens à venda (JSON com array de objetos item)
            inventory TEXT NOT NULL,
            
            -- Preços e economia
            buy_multiplier REAL DEFAULT 1.0,   -- Multiplicador de preço de compra
            sell_multiplier REAL DEFAULT 0.5,  -- Multiplicador de preço de venda
            restock_interval_hours INTEGER DEFAULT 24,
            last_restock DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Limitações
            max_items INTEGER DEFAULT 20,
            level_requirement INTEGER DEFAULT 0,
            reputation_requirement INTEGER DEFAULT 0,
            
            -- Horário de funcionamento
            opens_at_hour INTEGER DEFAULT 6,   -- 6:00 AM
            closes_at_hour INTEGER DEFAULT 22,  -- 10:00 PM
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    def get_base_data(self):
        return [
            {
                'name': 'Forja de Gunnar',
                'owner_npc_id': 2,  # Ferreiro Gunnar
                'shop_type': 'weapon',
                'inventory': '[{"item_id": 1, "stock": 5, "restock_amount": 5}, {"item_id": 2, "stock": 3, "restock_amount": 3}]',
                'buy_multiplier': 1.2,
                'sell_multiplier': 0.4,
                'restock_interval_hours': 24,
                'max_items': 15,
                'level_requirement': 0,
                'reputation_requirement': 0,
                'opens_at_hour': 6,
                'closes_at_hour': 20
            },
            {
                'name': 'Casa de Cura de Elara',
                'owner_npc_id': 3,  # Curandeira Elara
                'shop_type': 'potion',
                'inventory': '[{"item_id": 6, "stock": 10, "restock_amount": 10}, {"item_id": 7, "stock": 8, "restock_amount": 8}]',
                'buy_multiplier': 1.1,
                'sell_multiplier': 0.5,
                'restock_interval_hours': 12,
                'max_items': 25,
                'level_requirement': 0,
                'reputation_requirement': 0,
                'opens_at_hour': 8,
                'closes_at_hour': 22
            }
        ]