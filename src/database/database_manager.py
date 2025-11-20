# src/database/database_manager.py - VERSÃO COMPLETA E CORRIGIDA
import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional  # ✅ IMPORT CORRETO

import pygame

class DatabaseManager:
    """Gerenciador do banco de dados SQLite com conexão robusta"""
    
    def __init__(self):
        self.db_path = Path("saves/game_data.sqlite")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._init_database()
        self._migrate_old_data()
    
    def _ensure_connection(self):
        """✅ CORREÇÃO: Garante que a conexão está ativa antes de operações"""
        try:
            if self.connection is None:
                self._init_database()
                return
            
            # Testa a conexão executando uma query simples
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
        except sqlite3.Error:
            # Se falhar, reconecta
            try:
                if self.connection:
                    self.connection.close()
            except:
                pass
            self._init_database()
    
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
            print("✅ Banco de dados inicializado com sucesso")
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            raise
    
    def _migrate_old_data(self):
        """Migra dados antigos que podem estar com tipos incorretos"""
        self._ensure_connection()
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
                    print(f"🔧 Migrado: {category}.{key} de '{data_type}:{value}' para 'bool:{new_value}'")
            
            if migrated_count > 0:
                self.connection.commit()
                print(f"🎯 Migração concluída: {migrated_count} configurações corrigidas")
                
        except sqlite3.Error as e:
            print(f"❌ Erro durante migração: {e}")
    
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
        self._ensure_connection()
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
            print(f"❌ Erro ao obter configuração {category}.{key}: {e}")
            return default
    
    def set_setting(self, category: str, key: str, value: Any):
        """Define uma configuração no banco de dados"""
        self._ensure_connection()
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
            print(f"❌ Erro ao definir configuração {category}.{key}: {e}")
            raise
    
    def get_all_settings(self, category: str) -> Dict[str, Any]:
        """Obtém todas as configurações de uma categoria"""
        self._ensure_connection()
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
            print(f"❌ Erro ao obter configurações da categoria {category}: {e}")
            return {}
    
    def delete_all_settings(self, category: str = None):
        """Deleta todas as configurações (útil para reset)"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            if category:
                cursor.execute("DELETE FROM settings WHERE category = ?", (category,))
                print(f"🗑️ Todas as configurações da categoria '{category}' foram deletadas")
            else:
                cursor.execute("DELETE FROM settings")
                print("🗑️ Todas as configurações foram deletadas")
            
            self.connection.commit()
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao deletar configurações: {e}")
            raise

    def save_character(self, character_data: Dict[str, Any]):
        """Salva dados completos do personagem"""
        self._ensure_connection()
        try:
            # Converte dados complexos para JSON
            character_data['saved_at'] = pygame.time.get_ticks()
            
            self.set_setting(
                'characters',
                f"character_{character_data['name'].lower()}",
                character_data
            )
            print(f"✅ Personagem {character_data['name']} salvo com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao salvar personagem: {e}")

    def load_character(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Carrega dados do personagem"""
        return self.get_setting('characters', f"character_{character_name.lower()}")

    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Retorna todos os personagens salvos"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT value FROM settings WHERE category = 'characters'"
            )
            results = cursor.fetchall()
            
            characters = []
            for row in results:
                character_data = self._smart_convert_value(row['value'], 'json')
                if isinstance(character_data, dict):
                    characters.append(character_data)
            
            return characters
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao carregar personagens: {e}")
            return []

    def delete_character(self, character_name: str):
        """Remove um personagem salvo"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM settings WHERE category = 'characters' AND key = ?",
                (f"character_{character_name.lower()}",)
            )
            self.connection.commit()
            print(f"🗑️ Personagem {character_name} removido")
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao remover personagem: {e}")

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            self.connection = None
        print("💾 Conexão com o banco de dados fechada")

    # ===== NOVOS MÉTODOS PARA INICIALIZAÇÃO DE TABELAS =====
    
    def initialize_game_tables(self, force_recreate_static: bool = False) -> bool:
        """Inicializa todas as tabelas do jogo usando o sistema TableCreator"""
        print("🎮 Inicializando tabelas do jogo...")
        
        try:
            from src.database.datamaker.hero_classes import HeroClassesTable
            from src.database.datamaker.players import PlayersTable
            from src.database.datamaker.enemies import EnemiesTable
            from src.database.datamaker.items import ItemsTable
            from src.database.datamaker.npcs import NpcsTable
            from src.database.datamaker.quests import QuestsTable
            from src.database.datamaker.shops import ShopsTable
            from src.database.datamaker.game_world import GameWorldTable
            
            table_creators = [
                HeroClassesTable(self),    # Tabela estática
                PlayersTable(self),        # Tabela dinâmica
                EnemiesTable(self),        # Tabela estática
                ItemsTable(self),          # Tabela estática
                NpcsTable(self),           # Tabela estática
                QuestsTable(self),         # Tabela estática
                ShopsTable(self),          # Tabela estática
                GameWorldTable(self)       # Tabela estática
            ]
            
            success_count = 0
            for creator in table_creators:
                table_name = creator.get_table_name()
                is_static = getattr(creator, 'is_static_table', True)
                
                if is_static and force_recreate_static:
                    # Tabelas estáticas: recria completamente
                    if creator.recreate_table():
                        success_count += 1
                    else:
                        print(f"⚠️  Falha ao recriar tabela estática {table_name}")
                else:
                    # Cria tabela se não existir
                    if creator.create_table():
                        # Para tabelas estáticas, insere dados base
                        if is_static:
                            creator.insert_base_data()
                        success_count += 1
                    else:
                        print(f"⚠️  Falha ao criar tabela {table_name}")
            
            print(f"🎯 Tabelas inicializadas: {success_count}/{len(table_creators)}")
            return success_count == len(table_creators)
            
        except Exception as e:
            print(f"❌ Erro na inicialização das tabelas: {e}")
            return False

    # ===== MÉTODOS DE ACESSO PARA HERÓIS =====
    
    def get_hero_classes(self) -> List[Dict[str, Any]]:
        """Retorna todas as classes de heróis do banco"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM hero_classes ORDER BY id")
            classes = cursor.fetchall()
            return [dict(cls) for cls in classes]
        except Exception as e:
            print(f"❌ Erro ao buscar classes: {e}")
            return []
    
    def get_hero_class_by_key(self, class_key: str) -> Optional[Dict[str, Any]]:
        """Retorna uma classe específica pela chave"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM hero_classes WHERE class_key = ?", (class_key,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar classe {class_key}: {e}")
            return None

    # ===== MÉTODOS DE ACESSO PARA JOGADORES =====
    
    def save_player(self, player_data: Dict[str, Any]) -> bool:
        """Salva um jogador na tabela players (substitui o save_character)"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            
            # Converte dados para inserção
            columns = []
            values = []
            placeholders = []
            
            for key, value in player_data.items():
                columns.append(key)
                values.append(value)
                placeholders.append('?')
            
            columns_str = ', '.join(columns)
            placeholders_str = ', '.join(placeholders)
            
            # Verifica se o jogador já existe
            cursor.execute("SELECT id FROM players WHERE name = ?", (player_data['name'],))
            existing = cursor.fetchone()
            
            if existing:
                # UPDATE
                set_clause = ', '.join([f"{col} = ?" for col in columns])
                cursor.execute(
                    f"UPDATE players SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                    values + [player_data['name']]
                )
            else:
                # INSERT
                cursor.execute(
                    f"INSERT INTO players ({columns_str}) VALUES ({placeholders_str})",
                    values
                )
            
            self.connection.commit()
            print(f"✅ Jogador {player_data['name']} salvo na tabela players")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar jogador: {e}")
            return False
    
    def get_player(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Carrega um jogador da tabela players"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM players WHERE name = ?", (player_name,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao carregar jogador {player_name}: {e}")
            return None
    
    def get_all_players(self) -> List[Dict[str, Any]]:
        """Retorna todos os jogadores da tabela players"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM players ORDER BY created_at")
            players = cursor.fetchall()
            return [dict(player) for player in players]
        except Exception as e:
            print(f"❌ Erro ao carregar jogadores: {e}")
            return []
    
    # ===== MÉTODOS DE ACESSO PARA INIMIGOS =====
    
    def get_all_enemies(self) -> List[Dict[str, Any]]:
        """Retorna todos os inimigos"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM enemies ORDER BY level")
            enemies = cursor.fetchall()
            return [dict(enemy) for enemy in enemies]
        except Exception as e:
            print(f"❌ Erro ao buscar inimigos: {e}")
            return []
    
    def get_enemy_by_id(self, enemy_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um inimigo pelo ID"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM enemies WHERE id = ?", (enemy_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar inimigo {enemy_id}: {e}")
            return None
    
    def get_zone_enemies(self, zone_id: int) -> List[Dict[str, Any]]:
        """Retorna inimigos de uma zona específica"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM enemies WHERE zone_id = ? ORDER BY level", (zone_id,))
            enemies = cursor.fetchall()
            return [dict(enemy) for enemy in enemies]
        except Exception as e:
            print(f"❌ Erro ao buscar inimigos da zona {zone_id}: {e}")
            return []
    
    # ===== MÉTODOS DE ACESSO PARA ITENS =====
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Retorna todos os itens"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM items ORDER BY item_type, name")
            items = cursor.fetchall()
            return [dict(item) for item in items]
        except Exception as e:
            print(f"❌ Erro ao buscar itens: {e}")
            return []
    
    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um item pelo ID"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar item {item_id}: {e}")
            return None
    
    def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Retorna itens por tipo"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM items WHERE item_type = ? ORDER BY name", (item_type,))
            items = cursor.fetchall()
            return [dict(item) for item in items]
        except Exception as e:
            print(f"❌ Erro ao buscar itens do tipo {item_type}: {e}")
            return []
    
    # ===== MÉTODOS DE ACESSO PARA NPCS =====
    
    def get_all_npcs(self) -> List[Dict[str, Any]]:
        """Retorna todos os NPCs"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM npcs ORDER BY zone_id, name")
            npcs = cursor.fetchall()
            return [dict(npc) for npc in npcs]
        except Exception as e:
            print(f"❌ Erro ao buscar NPCs: {e}")
            return []
    
    def get_npc_by_id(self, npc_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um NPC pelo ID"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM npcs WHERE id = ?", (npc_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar NPC {npc_id}: {e}")
            return None
    
    def get_zone_npcs(self, zone_id: int) -> List[Dict[str, Any]]:
        """Retorna NPCs de uma zona específica"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM npcs WHERE zone_id = ? ORDER BY name", (zone_id,))
            npcs = cursor.fetchall()
            return [dict(npc) for npc in npcs]
        except Exception as e:
            print(f"❌ Erro ao buscar NPCs da zona {zone_id}: {e}")
            return []
    
    # ===== MÉTODOS DE ACESSO PARA MISSÕES =====
    
    def get_all_quests(self) -> List[Dict[str, Any]]:
        """Retorna todas as missões"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM quests ORDER BY required_level, id")
            quests = cursor.fetchall()
            return [dict(quest) for quest in quests]
        except Exception as e:
            print(f"❌ Erro ao buscar missões: {e}")
            return []
    
    def get_quest_by_id(self, quest_id: int) -> Optional[Dict[str, Any]]:
        """Retorna uma missão pelo ID"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM quests WHERE id = ?", (quest_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar missão {quest_id}: {e}")
            return None
    
    def get_quests_by_zone(self, zone_id: int) -> List[Dict[str, Any]]:
        """Retorna missões de uma zona específica"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM quests WHERE zone_id = ? ORDER BY required_level", (zone_id,))
            quests = cursor.fetchall()
            return [dict(quest) for quest in quests]
        except Exception as e:
            print(f"❌ Erro ao buscar missões da zona {zone_id}: {e}")
            return []
    
    # ===== MÉTODOS DE ACESSO PARA LOJAS =====
    
    def get_all_shops(self) -> List[Dict[str, Any]]:
        """Retorna todas as lojas"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM shops ORDER BY id")
            shops = cursor.fetchall()
            return [dict(shop) for shop in shops]
        except Exception as e:
            print(f"❌ Erro ao buscar lojas: {e}")
            return []
    
    def get_shop_by_id(self, shop_id: int) -> Optional[Dict[str, Any]]:
        """Retorna uma loja pelo ID"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM shops WHERE id = ?", (shop_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar loja {shop_id}: {e}")
            return None
    
    def get_shop_by_npc(self, npc_id: int) -> Optional[Dict[str, Any]]:
        """Retorna a loja de um NPC específico"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM shops WHERE owner_npc_id = ?", (npc_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar loja do NPC {npc_id}: {e}")
            return None
    
    # ===== MÉTODOS DE ACESSO PARA MUNDO DO JOGO =====
    
    def get_all_zones(self) -> List[Dict[str, Any]]:
        """Retorna todas as zonas do mundo"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM game_world ORDER BY level_min")
            zones = cursor.fetchall()
            return [dict(zone) for zone in zones]
        except Exception as e:
            print(f"❌ Erro ao buscar zonas: {e}")
            return []
    
    def get_zone_by_id(self, zone_id: int) -> Optional[Dict[str, Any]]:
        """Retorna uma zona pelo ID"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM game_world WHERE id = ?", (zone_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar zona {zone_id}: {e}")
            return None
    
    def get_zone_by_name(self, zone_name: str) -> Optional[Dict[str, Any]]:
        """Retorna uma zona pelo nome"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM game_world WHERE zone_name = ?", (zone_name,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar zona {zone_name}: {e}")
            return None
        
    def delete_player(self, player_name: str) -> bool:
        """Remove um jogador da tabela players"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM players WHERE name = ?", (player_name,))
            self.connection.commit()
            print(f"🗑️ Jogador {player_name} removido da tabela players")
            return True
        except Exception as e:
            print(f"❌ Erro ao remover jogador {player_name}: {e}")
            return False
    
    def get_hero_class_by_id(self, class_id: int) -> Optional[Dict[str, Any]]:
        """Retorna uma classe de herói pelo ID"""
        self._ensure_connection()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM hero_classes WHERE id = ?", (class_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Erro ao buscar classe por ID {class_id}: {e}")
            return None