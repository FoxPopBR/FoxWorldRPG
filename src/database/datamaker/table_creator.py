# src/database/datamaker/table_creator.py
import sqlite3
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class TableCreator(ABC):
    """Classe abstrata base para criação de tabelas - INTEGRADO COM DatabaseManager EXISTENTE"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.table_name = self.get_table_name()

    @abstractmethod
    def get_table_name(self) -> str:
        """Retorna o nome da tabela"""
        pass

    @abstractmethod
    def get_table_definition(self) -> str:
        """Retorna o SQL para criação da tabela"""
        pass

    @abstractmethod
    def get_base_data(self) -> List[Dict[str, Any]]:
        """Retorna dados base para inserção inicial"""
        pass

    def table_exists(self) -> bool:
        """Verifica se a tabela existe usando o DatabaseManager existente"""
        try:
            self.db_manager._ensure_connection()
            cursor = self.db_manager.connection.cursor()
            cursor.execute(
                f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """,
                (self.table_name,),
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Erro ao verificar tabela {self.table_name}: {e}")
            return False

    def create_table(self) -> bool:
        """Cria a tabela se não existir"""
        try:
            if not self.table_exists():
                self.db_manager._ensure_connection()
                cursor = self.db_manager.connection.cursor()
                cursor.execute(self.get_table_definition())
                self.db_manager.connection.commit()
                # print(f"✅ Tabela {self.table_name} criada com sucesso")
                return True
            else:
                # print(f"📋 Tabela {self.table_name} já existe")
                return True  # Retorna True pois a tabela já existe (estado desejado)
        except Exception as e:
            print(f"❌ Erro ao criar tabela {self.table_name}: {e}")
            return False

    def insert_base_data(self) -> bool:
        """Insere dados base na tabela"""
        try:
            base_data = self.get_base_data()
            if not base_data:
                return True

            self.db_manager._ensure_connection()
            cursor = self.db_manager.connection.cursor()

            for data in base_data:
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])

                cursor.execute(
                    f"INSERT OR REPLACE INTO {self.table_name} ({columns}) VALUES ({placeholders})",
                    list(data.values()),
                )

            self.db_manager.connection.commit()
            # print(
            #     f"✅ Dados base inseridos em {self.table_name}: {len(base_data)} registros"
            # )
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir dados base em {self.table_name}: {e}")
            return False

    def recreate_table(self) -> bool:
        """Recria a tabela (DROP + CREATE) - Para tabelas estáticas"""
        try:
            self.db_manager._ensure_connection()
            cursor = self.db_manager.connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
            self.db_manager.connection.commit()
            return self.create_table() and self.insert_base_data()
        except Exception as e:
            print(f"❌ Erro ao recriar tabela {self.table_name}: {e}")
            return False

    # Marca como tabela estática por padrão (pode ser sobrescrito)
    is_static_table = True
