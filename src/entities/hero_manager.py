# src/entities/hero_manager.py
import pygame
from typing import Dict, List, Optional, Any
from pathlib import Path
from .hero import Hero, HeroClass, HeroStats


class HeroManager:
    """Gerencia todos os heróis do jogo usando a tabela players do banco de dados"""

    def __init__(self, database, resource_manager=None):
        self.database = database
        self.resource_manager = resource_manager
        self.heroes: Dict[str, Hero] = {}
        self.current_hero: Optional[Hero] = None
        self._load_all_heroes()

    def _load_all_heroes(self):
        """Carrega todos os heróis da tabela players do banco de dados"""
        try:
            players_data = self.database.get_all_players()

            for player_data in players_data:
                try:
                    hero = self._convert_db_player_to_hero(player_data)
                    self.heroes[hero.name.lower()] = hero
                    # print(f"✅ Herói carregado da tabela players: {hero.name}")
                except Exception as e:
                    print(
                        f"❌ Erro ao carregar herói {player_data.get('name', 'Unknown')}: {e}"
                    )

            # print(f"🎯 Total de heróis carregados: {len(self.heroes)}")

        except Exception as e:
            print(f"❌ Erro ao carregar heróis do banco: {e}")
            self.heroes = {}

    def get_active_hero(self) -> Optional[Hero]:
        """Retorna o herói atualmente ativo"""
        return self.current_hero

    def _convert_db_player_to_hero(self, player_data: Dict[str, Any]) -> Hero:
        """Converte dados da tabela players para objeto Hero"""
        # Obtém a classe do herói
        class_data = self.database.get_hero_class_by_id(player_data["hero_class_id"])
        if not class_data:
            raise ValueError(f"Classe ID {player_data['hero_class_id']} não encontrada")

        # Converte string para enum HeroClass
        hero_class = HeroClass(class_data["class_key"])

        # Cria o herói
        hero = Hero(player_data["name"], hero_class, player_data.get("level", 1))
        hero.experience = player_data.get("experience", 0)

        # Carrega dados de localização e progresso
        hero.zone_id = player_data.get("zona_id", 1)
        hero.posicao_x = player_data.get("posicao_x", 0.0)
        hero.posicao_y = player_data.get("posicao_y", 0.0)
        hero.gold = player_data.get("gold", 0)
        hero.tempo_jogo = player_data.get("tempo_jogo", 0)

        # Define todos os atributos do banco
        base_stats = HeroStats()
        all_attributes = [
            # Atributos base
            "forca",
            "destreza",
            "vitalidade",
            "inteligencia",
            "armadura",
            "energia",  # Mantido para compatibilidade com DB
            "mana",  # Novo nome
            "stamina",
            # Atributos derivados básicos
            "vida_maxima",
            "mana_maxima",
            "vida_atual",
            "mana_atual",
            "dano_fisico_min",
            "dano_fisico_max",
            "dano_magico_min",
            "dano_magico_max",
            "defesa_fisica",
            "defesa_magica",
            # Atributos detalhados
            "bloqueio",
            "chance_critico",
            "dano_critico",
            "chance_esquiva",
            "velocidade_ataque",
            "precisao",
            "regeneracao_vida",
            "regeneracao_mana",
            "resistencia_fogo",
            "resistencia_gelo",
            "resistencia_eletrico",
            "resistencia_veneno",
            "resistencia_escuro",
            "sorte",
            "velocidade_movimento",
            "capacidade_carga",
        ]

        for attr in all_attributes:
            if attr in player_data and player_data[attr] is not None:
                setattr(base_stats, attr, player_data[attr])

        hero.stats = base_stats

        hero.stats = base_stats

        # Carrega assets se disponível
        self._load_hero_assets(hero)

        return hero

    def _load_hero_assets(self, hero: Hero):
        """Carrega os assets visuais do herói"""
        if self.resource_manager:
            hero.image_face = self.resource_manager.get_hero_image(
                hero.hero_class.value, "face"
            )
            hero.image_body = self.resource_manager.get_hero_image(
                hero.hero_class.value, "body"
            )

    def _convert_hero_to_db_player(self, hero: Hero) -> Dict[str, Any]:
        """Converte objeto Hero para dados da tabela players"""
        # Obtém ID da classe do banco
        class_data = self.database.get_hero_class_by_key(hero.hero_class.value)
        if not class_data:
            raise ValueError(f"Classe {hero.hero_class.value} não encontrada no banco")

        # Prepara todos os dados para o banco
        player_data = {
            "name": hero.name,
            "hero_class_id": class_data["id"],
            "level": hero.level,
            "experience": hero.experience,
            "experience_to_next_level": hero.experience + 100,
            # Atributos base
            "forca": hero.stats.forca,
            "destreza": hero.stats.destreza,
            "vitalidade": hero.stats.vitalidade,
            "inteligencia": hero.stats.inteligencia,
            "armadura": hero.stats.armadura,
            "mana": hero.stats.mana,  # Novo atributo
            "stamina": hero.stats.stamina,
            # Status atual
            "vida_atual": hero.stats.vida_atual,
            "mana_atual": hero.stats.mana_atual,
            "stamina_atual": hero.stats.stamina_atual,
            # Atributos derivados básicos
            "vida_maxima": hero.stats.vida_maxima,
            "mana_maxima": hero.stats.mana_maxima,
            "dano_fisico_min": hero.stats.dano_fisico_min,
            "dano_fisico_max": hero.stats.dano_fisico_max,
            "dano_magico_min": hero.stats.dano_magico_min,
            "dano_magico_max": hero.stats.dano_magico_max,
            "defesa_fisica": hero.stats.defesa_fisica,
            "defesa_magica": hero.stats.defesa_magica,
            # Atributos detalhados
            "bloqueio": hero.stats.bloqueio,
            "chance_critico": hero.stats.chance_critico,
            "dano_critico": hero.stats.dano_critico,
            "chance_esquiva": hero.stats.chance_esquiva,
            "velocidade_ataque": hero.stats.velocidade_ataque,
            "precisao": hero.stats.precisao,
            "regeneracao_vida": hero.stats.regeneracao_vida,
            "regeneracao_mana": hero.stats.regeneracao_mana,
            "resistencia_fogo": hero.stats.resistencia_fogo,
            "resistencia_gelo": hero.stats.resistencia_gelo,
            "resistencia_eletrico": hero.stats.resistencia_eletrico,
            "resistencia_veneno": hero.stats.resistencia_veneno,
            "resistencia_escuro": hero.stats.resistencia_escuro,
            "sorte": hero.stats.sorte,
            "velocidade_movimento": hero.stats.velocidade_movimento,
            "capacidade_carga": hero.stats.capacidade_carga,
            # Localização e progresso
            "zona_id": hero.zone_id,
            "posicao_x": hero.posicao_x,
            "posicao_y": hero.posicao_y,
            "gold": hero.gold,
            "tempo_jogo": hero.tempo_jogo,
            "equipamento": "{}",
        }

        return player_data

    def create_hero(
        self, name: str, hero_class: HeroClass, base_attributes: Dict[str, int]
    ) -> Hero:
        """Cria um novo herói e salva na tabela players"""
        hero = Hero(name, hero_class)

        # Aplica atributos base
        for attr, value in base_attributes.items():
            if hasattr(hero.stats, attr):
                setattr(hero.stats, attr, value)

        # Recalcula atributos derivados
        hero._calculate_derived_stats()

        # Carrega assets
        self._load_hero_assets(hero)

        # Salva na tabela players
        self._save_hero_to_db(hero)

        # Adiciona ao cache
        self.heroes[hero.name.lower()] = hero

        # Define como herói ativo
        self.current_hero = hero

        print(
            f"🎮 Novo herói criado e salvo na tabela players: {hero.name} ({hero_class.value})"
        )
        return hero

    def _save_hero_to_db(self, hero: Hero):
        """Salva um herói na tabela players"""
        try:
            player_data = self._convert_hero_to_db_player(hero)
            success = self.database.save_player(player_data)
            if success:
                print(f"💾 Herói salvo na tabela players: {hero.name}")
            else:
                print(f"❌ Falha ao salvar herói na tabela players: {hero.name}")
        except Exception as e:
            print(f"❌ Erro ao salvar herói {hero.name}: {e}")

    def get_hero(self, name: str) -> Optional[Hero]:
        """Retorna um herói pelo nome"""
        return self.heroes.get(name.lower())

    def get_all_heroes(self) -> List[Hero]:
        """Retorna lista de todos os heróis"""
        return list(self.heroes.values())

    def delete_hero(self, name: str) -> bool:
        """Remove um herói da tabela players"""
        try:
            hero_name_lower = name.lower()
            if hero_name_lower in self.heroes:
                del self.heroes[hero_name_lower]

                # Remove da tabela players
                success = self.database.delete_player(name)
                if success:
                    print(f"🗑️ Herói removido da tabela players: {name}")
                    return True
                else:
                    print(f"❌ Falha ao remover herói da tabela players: {name}")
                    return False
            return False
        except Exception as e:
            print(f"❌ Erro ao remover herói {name}: {e}")
            return False

    def set_current_hero(self, hero: Hero):
        """Define o herói atual"""
        self.current_hero = hero
        print(f"🎯 Herói atual definido: {hero.name}")

    def get_current_hero(self) -> Optional[Hero]:
        """Retorna o herói atual"""
        return self.current_hero

    def update_hero(self, hero: Hero):
        """Atualiza um herói na tabela players"""
        self._save_hero_to_db(hero)
        print(f"📊 Herói atualizado na tabela players: {hero.name}")

    def update_hero_stats(self, hero: Hero, new_stats: Dict[str, Any]):
        """Atualiza estatísticas de um herói"""
        try:
            for stat, value in new_stats.items():
                if hasattr(hero.stats, stat):
                    setattr(hero.stats, stat, value)

            hero._calculate_derived_stats()
            self.update_hero(hero)
            print(f"📊 Estatísticas atualizadas para: {hero.name}")

        except Exception as e:
            print(f"❌ Erro ao atualizar estatísticas de {hero.name}: {e}")

    def get_hero_summary(self, hero: Hero) -> Dict[str, Any]:
        """Retorna um resumo das informações do herói"""
        return {
            "name": hero.name,
            "class": hero.hero_class.value,
            "level": hero.level,
            "experience": hero.experience,
            "health": f"{hero.stats.vida_atual}/{hero.stats.vida_maxima}",
            "mana": f"{hero.stats.mana_atual}/{hero.stats.mana_maxima}",
            "primary_stats": {
                "forca": hero.stats.forca,
                "destreza": hero.stats.destreza,
                "vitalidade": hero.stats.vitalidade,
                "inteligencia": hero.stats.inteligencia,
            },
        }
