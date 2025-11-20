# src/database/datamaker/game_world.py
from .table_creator import TableCreator

class GameWorldTable(TableCreator):
    """Tabela do mundo do jogo - Dados estáticos"""
    
    def get_table_name(self) -> str:
        return "game_world"
    
    def get_table_definition(self) -> str:
        return """
        CREATE TABLE game_world (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_name TEXT NOT NULL UNIQUE,
            description TEXT,
            
            -- Níveis e dificuldade
            level_min INTEGER DEFAULT 1,
            level_max INTEGER DEFAULT 10,
            recommended_level INTEGER DEFAULT 1,
            difficulty TEXT DEFAULT 'easy',
            
            -- Conteúdo da zona
            enemies TEXT,           -- JSON com IDs de inimigos
            npcs TEXT,              -- JSON com IDs de NPCs
            resources TEXT,         -- JSON com recursos disponíveis
            points_of_interest TEXT, -- JSON com pontos de interesse
            
            -- Ambiente e clima
            environment_type TEXT DEFAULT 'forest', -- 'forest', 'desert', 'mountain', 'city', 'dungeon'
            weather_patterns TEXT,  -- JSON com padrões de clima
            music_track TEXT,
            ambient_sounds TEXT,    -- JSON com sons ambientes
            
            -- Mecânicas de zona
            is_safe_zone BOOLEAN DEFAULT FALSE,
            has_fast_travel BOOLEAN DEFAULT FALSE,
            respawn_time INTEGER DEFAULT 30, -- Tempo de respawn em segundos
            
            -- Visual
            background_image TEXT,
            minimap_image TEXT,
            parallax_layers TEXT,   -- JSON com layers para parallax
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    def get_base_data(self):
        return [
            {
                'zone_name': 'Vila das Sombras',
                'description': 'Uma pacata vila à beira da floresta, ponto de partida para aventureiros.',
                'level_min': 1,
                'level_max': 5,
                'recommended_level': 1,
                'difficulty': 'easy',
                'enemies': '[1, 4]',  # Goblins e Lobos
                'npcs': '[1, 2, 3, 4]', # Todos os NPCs iniciais
                'resources': '["herbs", "wood", "stone"]',
                'points_of_interest': '{"fountain": "Centro da vila", "inn": "Pousada do Viajante", "blacksmith": "Forja de Gunnar"}',
                'environment_type': 'village',
                'weather_patterns': '["clear", "rain", "fog"]',
                'music_track': 'assets/music/village_peaceful.ogg',
                'ambient_sounds': '["birds", "wind", "villager_voices"]',
                'is_safe_zone': True,
                'has_fast_travel': True,
                'respawn_time': 0,
                'background_image': 'assets/images/zones/village_background.png',
                'minimap_image': 'assets/images/zones/village_minimap.png',
                'parallax_layers': '["background", "middleground", "foreground"]'
            },
            {
                'zone_name': 'Floresta dos Sussurros',
                'description': 'Uma floresta densa e misteriosa, habitada por criaturas perigosas.',
                'level_min': 2,
                'level_max': 8,
                'recommended_level': 3,
                'difficulty': 'normal',
                'enemies': '[1, 2, 4]',  # Goblins, Orcs e Lobos
                'npcs': '[]',
                'resources': '["rare_herbs", "magic_plants", "animal_hides"]',
                'points_of_interest': '{"ancient_tree": "Árvore Milenar", "waterfall": "Cachoeira Escondida", "ruins": "Ruínas Antigas"}',
                'environment_type': 'forest',
                'weather_patterns': '["clear", "rain", "storm", "fog"]',
                'music_track': 'assets/music/forest_mysterious.ogg',
                'ambient_sounds': '["forest_animals", "wind_in_trees", "creek_water"]',
                'is_safe_zone': False,
                'has_fast_travel': False,
                'respawn_time': 45,
                'background_image': 'assets/images/zones/forest_background.png',
                'minimap_image': 'assets/images/zones/forest_minimap.png',
                'parallax_layers': '["far_trees", "near_trees", "ground"]'
            },
            {
                'zone_name': 'Ruínas Proibidas',
                'description': 'Antigas ruínas amaldiçoadas, lar do temido Feiticeiro das Trevas.',
                'level_min': 5,
                'level_max': 15,
                'recommended_level': 8,
                'difficulty': 'hard',
                'enemies': '[3]',  # Apenas Dark Mage (boss)
                'npcs': '[]',
                'resources': '["ancient_relics", "magic_crystals", "dark_essence"]',
                'points_of_interest': '{"main_chamber": "Câmara Principal", "library": "Biblioteca Proibida", "ritual_room": "Sala de Rituais"}',
                'environment_type': 'dungeon',
                'weather_patterns': '["dark", "cursed_rain"]',
                'music_track': 'assets/music/dungeon_dark.ogg',
                'ambient_sounds': '["echoes", "dripping_water", "whispers"]',
                'is_safe_zone': False,
                'has_fast_travel': False,
                'respawn_time': 60,
                'background_image': 'assets/images/zones/dungeon_background.png',
                'minimap_image': 'assets/images/zones/dungeon_minimap.png',
                'parallax_layers': '["background_pillars", "foreground_debris"]'
            }
        ]