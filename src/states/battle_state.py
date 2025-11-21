import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager
from src.ui.responsive_ui import ResponsiveUI
from src.core.battle_manager import BattleManager, BattleState


class BattleState(BaseState):
    """Estado de Batalha por Turnos"""

    def __init__(self, game, enemy):
        super().__init__(game)
        self.hero = self.game.game_config.hero_manager.get_active_hero()
        self.enemy = enemy
        self.battle_manager = BattleManager(self.hero, self.enemy)

        self.buttons = []
        self.message_log = ["Batalha iniciada!"]
        self.message_timer = 0

        self._create_ui()

    def _create_ui(self):
        """Cria botões de comando"""
        self.buttons.clear()

        screen_width = 1920
        screen_height = 1080

        btn_width = 200
        btn_height = 60
        spacing = 20
        start_x = 100
        start_y = screen_height - 150

        # Botões de Ação
        actions = [
            ("ATACAR", self._on_attack),
            ("MAGIA", self._on_magic),
            ("ITEM", self._on_item),
            ("FUGIR", self._on_run),
        ]

        for i, (text, action) in enumerate(actions):
            btn = Button(
                start_x + i * (btn_width + spacing),
                start_y,
                btn_width,
                btn_height,
                text,
                action,
                24,
            )
            self.buttons.append(btn)

    def _on_attack(self):
        msg = self.battle_manager.player_attack()
        self._add_log(msg)

    def _on_magic(self):
        self._add_log("Magia ainda não implementada!")

    def _on_item(self):
        self._add_log("Itens ainda não implementados!")

    def _on_run(self):
        msg = self.battle_manager.try_run()
        self._add_log(msg)

    def _add_log(self, message):
        self.message_log.append(message)
        if len(self.message_log) > 3:
            self.message_log.pop(0)
        self.message_timer = pygame.time.get_ticks()

    def update(self):
        # Verifica fim de batalha
        if self.battle_manager.state == BattleState.VICTORY:
            # TODO: Dar XP e Loot
            self.game.state_manager.pop_state()
        elif self.battle_manager.state == BattleState.RUN_AWAY:
            self.game.state_manager.pop_state()
        elif self.battle_manager.state == BattleState.DEFEAT:
            # TODO: Game Over
            self.game.state_manager.pop_state()

        # Turno do inimigo (automático com delay)
        if self.battle_manager.state == BattleState.ENEMY_TURN:
            current_time = pygame.time.get_ticks()
            if current_time - self.message_timer > 1000:  # 1s delay
                msg = self.battle_manager.next_turn()
                if msg:
                    self._add_log(msg)

        ButtonManager.update_buttons(self.buttons, self.game)

    def render(self, surface):
        screen_width, screen_height = surface.get_size()

        # Fundo (temporário)
        surface.fill((20, 10, 10))

        # Inimigo (Centro)
        if self.enemy.image:
            # Escala inimigo
            img = pygame.transform.scale(self.enemy.image, (400, 400))
            rect = img.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
            surface.blit(img, rect)
        else:
            # Placeholder
            rect = pygame.Rect(0, 0, 300, 300)
            rect.center = (screen_width // 2, screen_height // 2 - 100)
            pygame.draw.rect(surface, (200, 50, 50), rect)

        # Nome do Inimigo
        name_font = self.game.game_config.get_font("title", 48)
        name_text = name_font.render(self.enemy.name, True, (255, 100, 100))
        name_rect = name_text.get_rect(
            center=(screen_width // 2, screen_height // 2 - 350)
        )
        surface.blit(name_text, name_rect)

        # HP do Inimigo (Barra)
        bar_width = 400
        bar_height = 30
        bar_x = screen_width // 2 - bar_width // 2
        bar_y = name_rect.bottom + 20

        pct = self.enemy.current_hp / self.enemy.max_hp
        pygame.draw.rect(surface, (50, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(
            surface, (255, 0, 0), (bar_x, bar_y, bar_width * pct, bar_height)
        )
        pygame.draw.rect(
            surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2
        )

        # Jogador (Esquerda/Baixo - Imagem Body)
        if self.hero.image_body:
            hero_img = pygame.transform.scale(self.hero.image_body, (300, 600))
            hero_rect = hero_img.get_rect(bottomleft=(50, screen_height - 50))
            surface.blit(hero_img, hero_rect)

        # HUD de Batalha (Inferior)
        hud_rect = pygame.Rect(0, screen_height - 200, screen_width, 200)
        pygame.draw.rect(surface, (0, 0, 0), hud_rect)
        pygame.draw.line(
            surface,
            (255, 255, 255),
            (0, screen_height - 200),
            (screen_width, screen_height - 200),
            2,
        )

        # Log de Mensagens
        log_font = self.game.game_config.get_font("menu", 24)
        for i, msg in enumerate(self.message_log):
            text = log_font.render(msg, True, (255, 255, 255))
            surface.blit(text, (screen_width // 2 + 100, screen_height - 180 + i * 30))

        # Status do Herói (Simples)
        stats_font = self.game.game_config.get_font("menu", 28)
        hp_text = stats_font.render(
            f"HP: {self.hero.current_hp}/{self.hero.stats.hp}", True, (100, 255, 100)
        )
        mp_text = stats_font.render(
            f"MP: {self.hero.stats.mana}/{self.hero.stats.mana}", True, (100, 100, 255)
        )

        surface.blit(hp_text, (screen_width - 300, screen_height - 150))
        surface.blit(mp_text, (screen_width - 300, screen_height - 110))

        # Botões
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)
