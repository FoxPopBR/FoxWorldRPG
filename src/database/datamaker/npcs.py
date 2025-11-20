# src/database/datamaker/npcs.py
from .table_creator import TableCreator

class NpcsTable(TableCreator):
    """Tabela de NPCs - Dados estáticos"""
    
    def get_table_name(self) -> str:
        return "npcs"
    
    def get_table_definition(self) -> str:
        return """
        CREATE TABLE npcs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            npc_type TEXT NOT NULL,      -- 'quest_giver', 'merchant', 'trainer', 'story', 'crafting'
            faction TEXT DEFAULT 'neutral', -- 'friendly', 'neutral', 'hostile', 'guard'
            zone_id INTEGER DEFAULT 1,
            position_x REAL DEFAULT 0,
            position_y REAL DEFAULT 0,
            
            -- Diálogo e interação
            dialogue_tree TEXT,          -- JSON com árvore de diálogos
            default_greeting TEXT,
            default_farewell TEXT,
            
            -- Serviços oferecidos
            services TEXT,               -- JSON com serviços: ['shop', 'train', 'quest', 'craft']
            shop_id INTEGER,             -- Referência à loja (se merchant)
            training_skills TEXT,        -- JSON com habilidades que pode ensinar
            quests_offered TEXT,         -- JSON com IDs de missões oferecidas
            
            -- Status e aparência
            is_essential BOOLEAN DEFAULT TRUE, -- Não pode morrer
            respawn_time INTEGER DEFAULT 0, -- Tempo para respawn em segundos
            level INTEGER DEFAULT 1,
            health INTEGER DEFAULT 100,
            
            -- Visual
            sprite_path TEXT,
            scale_factor REAL DEFAULT 1.0,
            animation_set TEXT,          -- JSON com configurações de animação
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    def get_base_data(self):
        return [
            {
                'name': 'Aldeão',
                'npc_type': 'story',
                'faction': 'friendly',
                'zone_id': 1,
                'position_x': 150.0,
                'position_y': 200.0,
                'dialogue_tree': '{"greeting": "Olá, viajante! A vila está tranquila hoje.", "topics": {"vila": "Nossa vila é pacífica, mas tome cuidado com os goblins na floresta."}}',
                'default_greeting': 'Olá, viajante!',
                'default_farewell': 'Cuidado por aí!',
                'services': '[]',
                'is_essential': True,
                'respawn_time': 0,
                'level': 1,
                'health': 100,
                'sprite_path': 'assets/images/npcs/villager.png',
                'scale_factor': 1.0,
                'animation_set': '{"idle": "idle", "walk": "walk"}'
            },
            {
                'name': 'Ferreiro Gunnar',
                'npc_type': 'merchant',
                'faction': 'friendly', 
                'zone_id': 1,
                'position_x': 300.0,
                'position_y': 180.0,
                'dialogue_tree': '{"greeting": "Precisa de equipamentos? Tenho as melhores armas da região!", "topics": {"armas": "Minhas espadas são forjadas com o melhor aço!"}}',
                'default_greeting': 'Bem-vindo à minha forja!',
                'default_farewell': 'Volte sempre!',
                'services': '["shop", "repair"]',
                'shop_id': 1,
                'is_essential': True,
                'respawn_time': 0,
                'level': 5,
                'health': 150,
                'sprite_path': 'assets/images/npcs/blacksmith.png',
                'scale_factor': 1.1,
                'animation_set': '{"idle": "hammer_idle", "work": "hammer_work"}'
            },
            {
                'name': 'Curandeira Elara',
                'npc_type': 'merchant',
                'faction': 'friendly',
                'zone_id': 1,
                'position_x': 250.0,
                'position_y': 250.0,
                'dialogue_tree': '{"greeting": "As ervas da floresta têm grande poder medicinal.", "topics": {"ervas": "Cuidado ao coletar ervas, algumas são venenosas."}}',
                'default_greeting': 'Que as bênçãos da natureza estejam com você.',
                'default_farewell': 'Cuide-se, viajante.',
                'services': '["shop", "heal"]',
                'shop_id': 2,
                'is_essential': True,
                'respawn_time': 0,
                'level': 3,
                'health': 120,
                'sprite_path': 'assets/images/npcs/healer.png',
                'scale_factor': 1.0,
                'animation_set': '{"idle": "idle", "cast": "cast_spell"}'
            },
            {
                'name': 'Capitão da Guarda',
                'npc_type': 'quest_giver',
                'faction': 'friendly',
                'zone_id': 1,
                'position_x': 400.0,
                'position_y': 150.0,
                'dialogue_tree': '{"greeting": "A guarda está sempre recrutando bravos aventureiros.", "topics": {"goblins": "Esses malditos goblins estão atacando os viajantes!"}}',
                'default_greeting': 'Salve, cidadão!',
                'default_farewell': 'Mantenha-se vigilante!',
                'services': '["quest"]',
                'quests_offered': '[1, 2]',
                'is_essential': True,
                'respawn_time': 0,
                'level': 10,
                'health': 200,
                'sprite_path': 'assets/images/npcs/guard_captain.png',
                'scale_factor': 1.1,
                'animation_set': '{"idle": "guard_idle", "alert": "guard_alert"}'
            }
        ]