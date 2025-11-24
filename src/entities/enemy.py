from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class EnemyStats:
    """Atributos de combate do inimigo"""

    vida_maxima: int = 100
    vida_atual: int = 100
    mana_maxima: int = 50
    mana_atual: int = 50
    dano_fisico: int = 10
    dano_magico: int = 5
    defesa_fisica: int = 5
    defesa_magica: int = 2
    velocidade: int = 10
    xp_reward: int = 20
    gold_reward: int = 10


class Enemy:
    """Representa um inimigo em batalha"""

    def __init__(
        self,
        name: str,
        image_path: str,
        stats: Optional[EnemyStats] = None,
        level: int = 1,
    ):
        self.name = name
        self.image_path = image_path
        self.stats = stats if stats else EnemyStats()
        self.level = level
        self.image = None  # Carregado posteriormente

    @classmethod
    def create_rat(cls):
        """Factory method para criar um Rato (exemplo)"""
        stats = EnemyStats(
            vida_maxima=50,
            vida_atual=50,
            dano_fisico=8,
            defesa_fisica=2,
            xp_reward=15,
            gold_reward=5,
        )
        return cls("Rato Gigante", "assets/images/enemy/rato.png", stats)
