# src/entities/hero.py
import pygame
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class HeroClass(Enum):
    BARBARIAN = "barbaro"
    PALADIN = "paladino"
    DRUID = "druida"
    SORCERER = "feiticeiro"
    NECROMANCER = "necromante"


@dataclass
class HeroStats:
    # Atributos base
    forca: int = 5
    destreza: int = 5
    vitalidade: int = 5
    inteligencia: int = 5
    armadura: int = 5
    energia: int = 5  # Mantido para compatibilidade com DB
    mana: int = 5  # Novo nome
    stamina: int = 5

    # Atributos derivados
    vida_maxima: int = 0
    mana_maxima: int = 0
    vida_atual: int = 0
    mana_atual: int = 0
    stamina_atual: int = 0
    dano_fisico_min: int = 0
    dano_fisico_max: int = 0
    dano_magico_min: int = 0
    dano_magico_max: int = 0
    defesa_fisica: int = 0
    defesa_magica: int = 0
    bloqueio: float = 0.0
    chance_critico: float = 0.0
    dano_critico: float = 0.0
    chance_esquiva: float = 0.0
    velocidade_ataque: float = 0.0
    precisao: float = 0.0
    regeneracao_vida: float = 0.0
    regeneracao_mana: float = 0.0
    resistencia_fogo: float = 0.0
    resistencia_gelo: float = 0.0
    resistencia_eletrico: float = 0.0
    resistencia_veneno: float = 0.0
    resistencia_escuro: float = 0.0
    sorte: float = 0.0
    velocidade_movimento: float = 0.0
    capacidade_carga: int = 0


class Hero:
    def __init__(self, name: str, hero_class: HeroClass, level: int = 1):
        self.name = name
        self.hero_class = hero_class
        self.level = level
        self.experience = 0
        self.stats = HeroStats()

        # Localização e Progresso
        self.zone_id: int = 1
        self.posicao_x: float = 0.0
        self.posicao_y: float = 0.0
        self.gold: int = 0
        self.gold: int = 0
        self.tempo_jogo: int = 0
        self.inventory: List[Dict[str, Any]] = []  # Lista de itens

        # Assets (Runtime only)
        self.image_face: Any = None  # pygame.Surface
        self.image_body: Any = None  # pygame.Surface

        self._calculate_derived_stats()

    def _calculate_derived_stats(self):
        """Calcula todos os atributos derivados baseados nos atributos base"""
        base = self.stats

        # Bônus de classe
        class_bonus = self._get_class_bonus()
        effective_stats = self._apply_class_bonus(base, class_bonus)

        # Atributos derivados
        base.vida_maxima = effective_stats.vitalidade * 12 + effective_stats.forca * 3
        base.mana_maxima = effective_stats.inteligencia * 10 + effective_stats.mana * 5
        base.vida_atual = base.vida_maxima
        base.mana_atual = base.mana_maxima
        base.dano_fisico_min = effective_stats.forca * 2
        base.dano_fisico_max = effective_stats.forca * 3 + effective_stats.destreza
        base.dano_magico_min = effective_stats.inteligencia * 2
        base.dano_magico_max = effective_stats.inteligencia * 3
        base.defesa_fisica = (
            effective_stats.armadura * 3 + effective_stats.vitalidade // 2
        )
        base.defesa_magica = effective_stats.inteligencia * 2 + effective_stats.mana
        base.bloqueio = effective_stats.armadura * 0.5
        base.chance_critico = effective_stats.destreza * 0.6
        base.dano_critico = 150 + effective_stats.destreza * 1.5
        base.chance_esquiva = effective_stats.destreza * 0.4
        base.velocidade_ataque = 1.0 + effective_stats.destreza * 0.03
        base.precisao = 80 + effective_stats.destreza * 2
        base.regeneracao_vida = effective_stats.vitalidade * 0.15
        base.regeneracao_mana = effective_stats.mana * 0.25
        base.resistencia_fogo = effective_stats.vitalidade * 0.6
        base.resistencia_gelo = effective_stats.vitalidade * 0.6
        base.resistencia_eletrico = effective_stats.vitalidade * 0.6
        base.resistencia_veneno = effective_stats.vitalidade * 1.0
        base.resistencia_escuro = effective_stats.inteligencia * 0.5
        base.sorte = effective_stats.destreza * 0.4
        base.velocidade_movimento = 100 + effective_stats.destreza * 2
        base.capacidade_carga = (
            effective_stats.forca * 10 + effective_stats.vitalidade * 5
        )

        # Arredonda valores float
        for attr_name in dir(base):
            if not attr_name.startswith("_"):
                value = getattr(base, attr_name)
                if isinstance(value, float):
                    setattr(base, attr_name, round(value, 2))

    def _get_class_bonus(self) -> Dict[str, int]:
        """Retorna bônus da classe"""
        bonuses = {
            HeroClass.BARBARIAN: {"forca": 3, "vitalidade": 2, "stamina": 2},
            HeroClass.PALADIN: {"armadura": 3, "forca": 2, "mana": 1},
            HeroClass.DRUID: {"inteligencia": 2, "mana": 2, "vitalidade": 1},
            HeroClass.SORCERER: {"inteligencia": 3, "mana": 3, "forca": -2},
            HeroClass.NECROMANCER: {"inteligencia": 3, "mana": 2, "vitalidade": -1},
        }
        return bonuses.get(self.hero_class, {})

    def _apply_class_bonus(self, stats: HeroStats, bonus: Dict[str, int]) -> HeroStats:
        """Aplica bônus da classe aos stats"""
        effective_stats = HeroStats()

        # Copia atributos base
        for attr_name in dir(stats):
            if not attr_name.startswith("_") and not callable(
                getattr(stats, attr_name)
            ):
                setattr(effective_stats, attr_name, getattr(stats, attr_name))

        # Aplica bônus
        for attr, value in bonus.items():
            if hasattr(effective_stats, attr):
                current = getattr(effective_stats, attr)
                setattr(effective_stats, attr, max(1, current + value))

        return effective_stats

    def to_dict(self) -> Dict[str, Any]:
        """Converte herói para dicionário para salvar no banco"""
        return {
            "name": self.name,
            "class": self.hero_class.value,
            "level": self.level,
            "experience": self.experience,
            "stats": self._stats_to_dict(),
        }

    def _stats_to_dict(self) -> Dict[str, Any]:
        """Converte stats para dicionário"""
        stats_dict = {}
        for attr_name in dir(self.stats):
            if not attr_name.startswith("_") and not callable(
                getattr(self.stats, attr_name)
            ):
                stats_dict[attr_name] = getattr(self.stats, attr_name)
        return stats_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Cria herói a partir de dicionário"""
        hero = cls(data["name"], HeroClass(data["class"]), data.get("level", 1))
        hero.experience = data.get("experience", 0)
        hero._load_stats_from_dict(data.get("stats", {}))
        return hero

    def _load_stats_from_dict(self, stats_data: Dict[str, Any]):
        """Carrega stats do dicionário"""
        for attr_name, value in stats_data.items():
            if hasattr(self.stats, attr_name):
                setattr(self.stats, attr_name, value)
