# src/database/datamaker/players.py
from .table_creator import TableCreator


class PlayersTable(TableCreator):
    """Tabela de jogadores - COM TODOS OS ATRIBUTOS DETALHADOS"""

    def get_table_name(self) -> str:
        return "players"

    def get_table_definition(self) -> str:
        return """
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            hero_class_id INTEGER NOT NULL,
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            experience_to_next_level INTEGER DEFAULT 100,
            
            -- ATRIBUTOS BASE
            forca INTEGER DEFAULT 5,
            destreza INTEGER DEFAULT 5,
            vitalidade INTEGER DEFAULT 5,
            inteligencia INTEGER DEFAULT 5,
            armadura INTEGER DEFAULT 5,
            mana INTEGER DEFAULT 5,
            stamina INTEGER DEFAULT 5,
            
            -- STATUS ATUAL
            vida_atual INTEGER DEFAULT 0,
            mana_atual INTEGER DEFAULT 0,
            stamina_atual INTEGER DEFAULT 0,
            
            -- ATRIBUTOS DERIVADOS BÁSICOS
            vida_maxima INTEGER DEFAULT 0,
            mana_maxima INTEGER DEFAULT 0,
            dano_fisico_min INTEGER DEFAULT 0,
            dano_fisico_max INTEGER DEFAULT 0,
            dano_magico_min INTEGER DEFAULT 0,
            dano_magico_max INTEGER DEFAULT 0,
            defesa_fisica INTEGER DEFAULT 0,
            defesa_magica INTEGER DEFAULT 0,
            
            -- ATRIBUTOS DETALHADOS
            bloqueio REAL DEFAULT 0.0,
            chance_critico REAL DEFAULT 0.0,
            dano_critico REAL DEFAULT 0.0,
            chance_esquiva REAL DEFAULT 0.0,
            velocidade_ataque REAL DEFAULT 0.0,
            precisao REAL DEFAULT 0.0,
            regeneracao_vida REAL DEFAULT 0.0,
            regeneracao_mana REAL DEFAULT 0.0,
            regeneracao_stamina REAL DEFAULT 0.0,
            
            -- Resistências Elementais
            resistencia_fogo REAL DEFAULT 0.0,
            resistencia_gelo REAL DEFAULT 0.0,
            resistencia_eletrico REAL DEFAULT 0.0,
            resistencia_veneno REAL DEFAULT 0.0,
            resistencia_escuro REAL DEFAULT 0.0,
            resistencia_caos REAL DEFAULT 0.0,
            
            -- Resistências a Tipos de Dano
            resistencia_dano_fisico REAL DEFAULT 0.0,
            resistencia_dano_magico REAL DEFAULT 0.0,
            
            -- Penetrações
            penetracao_armadura REAL DEFAULT 0.0,
            penetracao_magica REAL DEFAULT 0.0,
            
            -- Danos Bônus
            dano_fisico_bonus INTEGER DEFAULT 0,
            dano_magico_bonus INTEGER DEFAULT 0,
            
            -- Roubos (Life/Mana Steal)
            roubo_vida REAL DEFAULT 0.0,
            roubo_mana REAL DEFAULT 0.0,
            
            -- Economia
            taxa_ouro REAL DEFAULT 0.0,
            taxa_experiencia REAL DEFAULT 0.0,
            taxa_drop_itens REAL DEFAULT 0.0,
            
            -- Velocidades e Utilidade
            velocidade_lancamento REAL DEFAULT 0.0,
            reducao_cooldown REAL DEFAULT 0.0,
            
            sorte REAL DEFAULT 0.0,
            velocidade_movimento REAL DEFAULT 0.0,
            capacidade_carga INTEGER DEFAULT 0,
            stamina_maxima INTEGER DEFAULT 0,
            
            -- Localização e progresso
            zona_id INTEGER DEFAULT 1,
            posicao_x REAL DEFAULT 0,
            posicao_y REAL DEFAULT 0,
            gold INTEGER DEFAULT 0,
            tempo_jogo INTEGER DEFAULT 0,
            
            -- Equipamento e Inventário (JSON)
            equipment TEXT DEFAULT '{}',
            inventory TEXT DEFAULT '[]',
            attribute_points INTEGER DEFAULT 0,
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (hero_class_id) REFERENCES hero_classes (id)
        )
        """

    def get_base_data(self):
        return []

    is_static_table = False
