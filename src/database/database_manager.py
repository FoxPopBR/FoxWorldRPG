import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class DatabaseManager:
    """Gerenciador do banco de dados SQLite para o jogo com migração automática"""
    
    def __init__(self):
        self.db_path = Path("saves/game_data.sqlite")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._init_database()
        self._migrate_old_data()  # Migração de dados antigos
    
    def _init_database(self):
        """Inicializa o banco de dados com todas as tabelas necessárias"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            cursor = self.connection.cursor()
            
            # Tabela de configurações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    PRIMARY KEY (category, key)
                )
            ''')
            
            # Tabela de save games
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS save_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slot INTEGER NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    player_data TEXT NOT NULL,
                    world_state TEXT NOT NULL,
                    game_version TEXT NOT NULL
                )
            ''')
            
            self.connection.commit()
            print("Banco de dados inicializado com sucesso")
            
        except sqlite3.Error as e:
            print(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def _migrate_old_data(self):
        """Migra dados antigos que podem estar com tipos incorretos"""
        try:
            cursor = self.connection.cursor()
            
            # Busca configurações problemáticas
            cursor.execute("SELECT category, key, value, data_type FROM settings")
            settings = cursor.fetchall()
            
            migrated_count = 0
            for category, key, value, data_type in settings:
                # CORREÇÃO: Se o tipo está errado, corrige
                if data_type == 'int' and value in ('True', 'False', 'true', 'false'):
                    new_data_type = 'bool'
                    new_value = 'True' if value.lower() == 'true' else 'False'
                    
                    cursor.execute('''
                        UPDATE settings SET data_type = ?, value = ? 
                        WHERE category = ? AND key = ?
                    ''', (new_data_type, new_value, category, key))
                    migrated_count += 1
                    print(f"Migrado: {category}.{key} de '{data_type}:{value}' para 'bool:{new_value}'")
            
            if migrated_count > 0:
                self.connection.commit()
                print(f"Migração concluída: {migrated_count} configurações corrigidas")
                
        except sqlite3.Error as e:
            print(f"Erro durante migração: {e}")
    
    def _smart_convert_value(self, value: str, data_type: str) -> Any:
        """Conversão inteligente que detecta automaticamente o tipo real"""
        # Primeiro, tenta converter baseado no data_type declarado
        try:
            if data_type == 'int':
                return int(value)
            elif data_type == 'float':
                return float(value)
            elif data_type == 'bool':
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                else:
                    return bool(value)
            elif data_type == 'json':
                return json.loads(value)
            elif data_type == 'tuple':
                data = json.loads(value)
                return tuple(data) if isinstance(data, list) else data
            else:  # string
                return value
        except (ValueError, json.JSONDecodeError):
            # Se falhar, tenta detectar o tipo automaticamente
            return self._auto_detect_type(value)
    
    def _auto_detect_type(self, value: str) -> Any:
        """Detecta automaticamente o tipo do valor"""
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '').isdigit():
            return float(value)
        else:
            try:
                # Tenta parsear como JSON
                return json.loads(value)
            except (ValueError, json.JSONDecodeError):
                # Mantém como string
                return value
    
    def _get_data_type(self, value: Any) -> str:
        """Determina o tipo de dado para armazenamento"""
        if isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, tuple):
            return 'tuple'
        elif isinstance(value, (dict, list)):
            return 'json'
        else:
            return 'string'
    
    def _convert_for_storage(self, value: Any, data_type: str) -> str:
        """Converte valor para string para armazenamento"""
        if data_type == 'json':
            return json.dumps(value, ensure_ascii=False)
        elif data_type == 'tuple':
            return json.dumps(list(value), ensure_ascii=False)
        else:
            return str(value)
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Obtém uma configuração do banco de dados"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT value, data_type FROM settings WHERE category = ? AND key = ?",
                (category, key)
            )
            result = cursor.fetchone()
            
            if result:
                value, data_type = result
                return self._smart_convert_value(value, data_type)
            else:
                return default
                
        except sqlite3.Error as e:
            print(f"Erro ao obter configuração {category}.{key}: {e}")
            return default
    
    def set_setting(self, category: str, key: str, value: Any):
        """Define uma configuração no banco de dados"""
        try:
            data_type = self._get_data_type(value)
            stored_value = self._convert_for_storage(value, data_type)
            
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (category, key, value, data_type)
                VALUES (?, ?, ?, ?)
            ''', (category, key, stored_value, data_type))
            
            self.connection.commit()
            
        except sqlite3.Error as e:
            print(f"Erro ao definir configuração {category}.{key}: {e}")
            raise
    
    def get_all_settings(self, category: str) -> Dict[str, Any]:
        """Obtém todas as configurações de uma categoria"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT key, value, data_type FROM settings WHERE category = ?",
                (category,)
            )
            results = cursor.fetchall()
            
            settings = {}
            for row in results:
                key = row['key']
                value = row['value']
                data_type = row['data_type']
                settings[key] = self._smart_convert_value(value, data_type)
            
            return settings
            
        except sqlite3.Error as e:
            print(f"Erro ao obter configurações da categoria {category}: {e}")
            return {}
    
    def delete_all_settings(self, category: str = None):
        """Deleta todas as configurações (útil para reset)"""
        try:
            cursor = self.connection.cursor()
            if category:
                cursor.execute("DELETE FROM settings WHERE category = ?", (category,))
                print(f"Todas as configurações da categoria '{category}' foram deletadas")
            else:
                cursor.execute("DELETE FROM settings")
                print("Todas as configurações foram deletadas")
            
            self.connection.commit()
            
        except sqlite3.Error as e:
            print(f"Erro ao deletar configurações: {e}")
            raise
    
    # ... (outros métodos permanecem iguais) ...

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            self.connection = None