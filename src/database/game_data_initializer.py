# src/database/game_data_initializer.py
from src.database.database_manager import DatabaseManager
from src.database.datamaker.hero_classes import HeroClassesTable
from src.database.datamaker.enemies import EnemiesTable
from src.database.datamaker.npcs import NpcsTable
from src.database.datamaker.items import ItemsTable
from src.database.datamaker.quests import QuestsTable
from src.database.datamaker.players import PlayersTable
from src.database.datamaker.shops import ShopsTable
from src.database.datamaker.game_world import GameWorldTable

class GameDataInitializer:
    """Gerenciador principal de inicialização do banco de dados"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.table_creators = []
        self._initialize_creators()
    
    def _initialize_creators(self):
        """Inicializa todos os criadores de tabela"""
        self.table_creators = [
            HeroClassesTable(self.db_manager),    # Tabela estática
            EnemiesTable(self.db_manager),        # Tabela estática  
            NpcsTable(self.db_manager),           # Tabela estática
            ItemsTable(self.db_manager),          # Tabela estática
            QuestsTable(self.db_manager),         # Tabela estática
            PlayersTable(self.db_manager),        # Tabela dinâmica
            ShopsTable(self.db_manager),          # Tabela estática
            GameWorldTable(self.db_manager)       # Tabela estática
        ]
    
    def initialize_database(self, force_recreate_static=False):
        """Inicializa todo o banco de dados"""
        print("🎮 Inicializando banco de dados FoxWorld RPG...")
        
        success_count = 0
        total_tables = len(self.table_creators)
        
        for creator in self.table_creators:
            table_name = creator.get_table_name()
            
            # Determina se é tabela estática ou dinâmica
            is_static = hasattr(creator, 'is_static_table') and creator.is_static_table
            
            if is_static and force_recreate_static:
                # Tabelas estáticas: recria completamente
                if creator.recreate_table():
                    success_count += 1
                else:
                    print(f"⚠️  Falha ao recriar tabela estática {table_name}")
            else:
                # Tabelas dinâmicas: apenas cria se não existir
                if creator.create_table():
                    if is_static:
                        creator.insert_base_data()
                    success_count += 1
                else:
                    print(f"⚠️  Falha ao criar tabela {table_name}")
        
        print(f"🎯 Initialização concluída: {success_count}/{total_tables} tabelas processadas")
        return success_count == total_tables
    
    def get_table_creator(self, table_name):
        """Retorna o criador de tabela pelo nome"""
        for creator in self.table_creators:
            if creator.get_table_name() == table_name:
                return creator
        return None
    
    def check_database_integrity(self):
        """Verifica a integridade do banco de dados"""
        print("🔍 Verificando integridade do banco de dados...")
        
        integrity_issues = []
        
        for creator in self.table_creators:
            if not creator.table_exists():
                integrity_issues.append(f"Tabela {creator.get_table_name()} não existe")
        
        if integrity_issues:
            print(f"❌ Problemas de integridade encontrados: {len(integrity_issues)}")
            for issue in integrity_issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Integridade do banco de dados verificada com sucesso")
            return True