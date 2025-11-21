import random
from enum import Enum


class BattleState(Enum):
    PLAYER_TURN = 0
    ENEMY_TURN = 1
    VICTORY = 2
    DEFEAT = 3
    RUN_AWAY = 4


class BattleManager:
    """Gerenciador de lógica de batalha"""

    def __init__(self, hero, enemy):
        self.hero = hero
        self.enemy = enemy
        self.state = BattleState.PLAYER_TURN
        self.turn_count = 0
        self.log = []

    def next_turn(self):
        """Avança para o próximo turno"""
        self.turn_count += 1
        if self.state == BattleState.PLAYER_TURN:
            self.state = BattleState.ENEMY_TURN
            return self.enemy_action()
        elif self.state == BattleState.ENEMY_TURN:
            self.state = BattleState.PLAYER_TURN
            return "Sua vez!"

    def player_attack(self):
        """Executa ataque do jogador"""
        if self.state != BattleState.PLAYER_TURN:
            return "Não é seu turno!"

        # Cálculo de dano simples (TODO: Usar atributos reais)
        damage = max(1, self.hero.stats.strength * 2 - self.enemy.defense)
        damage = int(damage * random.uniform(0.8, 1.2))

        # Crítico
        is_crit = random.random() < 0.1  # 10% chance
        if is_crit:
            damage *= 2

        self.enemy.current_hp = max(0, self.enemy.current_hp - damage)

        msg = f"Você causou {damage} de dano!"
        if is_crit:
            msg += " (CRÍTICO!)"

        if self.enemy.current_hp <= 0:
            self.state = BattleState.VICTORY
            msg += " Inimigo derrotado!"
        else:
            self.state = BattleState.ENEMY_TURN

        self.log.append(msg)
        return msg

    def enemy_action(self):
        """Executa ação do inimigo"""
        if self.state != BattleState.ENEMY_TURN:
            return

        # Inimigo ataca
        damage = max(1, self.enemy.attack - self.hero.stats.defense)
        damage = int(damage * random.uniform(0.8, 1.2))

        self.hero.current_hp = max(0, self.hero.current_hp - damage)

        msg = f"{self.enemy.name} causou {damage} de dano!"

        if self.hero.current_hp <= 0:
            self.state = BattleState.DEFEAT
            msg += " Você foi derrotado!"
        else:
            self.state = BattleState.PLAYER_TURN

        self.log.append(msg)
        return msg

    def try_run(self):
        """Tenta fugir da batalha"""
        if self.state != BattleState.PLAYER_TURN:
            return "Não é seu turno!"

        chance = 0.5  # 50% chance
        if random.random() < chance:
            self.state = BattleState.RUN_AWAY
            msg = "Você fugiu com sucesso!"
        else:
            self.state = BattleState.ENEMY_TURN
            msg = "Falha ao fugir!"

        self.log.append(msg)
        return msg
