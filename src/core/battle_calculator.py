import random


class BattleCalculator:
    """Calculadora de dano e efeitos de batalha"""

    @staticmethod
    def calculate_physical_damage(attacker_stats, defender_stats):
        """
        Calcula dano físico:
        (Dano Base + Força/2) * Variação - (Defesa * 0.5)
        """
        # Atacante pode ser HeroStats ou EnemyStats
        # Normaliza acesso a atributos (Hero usa 'forca', Enemy usa 'dano_fisico' direto)

        # Fórmula Conservadora: (Dano - Defesa * 0.5)
        # Garante dano mínimo de 1

        # 1. Dano Base do Atacante
        min_dmg = getattr(attacker_stats, "dano_fisico_min", 0)
        max_dmg = getattr(attacker_stats, "dano_fisico_max", 0)

        # Fallback para inimigos que usam dano fixo
        if max_dmg == 0:
            base_dmg = getattr(attacker_stats, "dano_fisico", 5)
            min_dmg = int(base_dmg * 0.8)
            max_dmg = int(base_dmg * 1.2)

        raw_dmg = random.randint(min_dmg, max_dmg)

        # 2. Mitigação pela Defesa
        defense = getattr(defender_stats, "defesa_fisica", 0)
        mitigation = int(defense * 0.5)  # Mitiga 50% do valor da defesa

        final_dmg = max(1, raw_dmg - mitigation)

        # 3. Crítico (Dano x1.5)
        crit_chance = getattr(attacker_stats, "chance_critico", 0.05)
        is_crit = random.random() < crit_chance
        if is_crit:
            crit_mult = (
                getattr(attacker_stats, "dano_critico", 150) / 100.0
            )  # Ex: 150 -> 1.5x
            final_dmg = int(final_dmg * crit_mult)

        return final_dmg, is_crit
