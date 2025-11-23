# src/states/battle_state.py
import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.core.battle_manager import BattleManager, BattleState


class BattleState(BaseState):
    """Estado de Batalha por Turnos - REFATORADO UIScaler"""

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

        # Dimensões base (1920x1080 virtual)
        btn_width = 200
        btn_height = 60
        spacing = 20
        start_x = 100
        base_start_y = self.theme.BASE_HEIGHT - 150

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
                base_start_y,
                btn_width,
                btn_height,
                text,
                action,
                font_size=self.theme.FONT_MENU_MEDIUM,
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

        # Atualiza botões
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, surface):
        # Fundo
        surface.fill(self.theme.COLOR_BG_DARK)

        # Informações do herói (lado esquerdo)
        self._render_hero_info(surface)

        # Informações do inimigo (lado direito)
        self._render_enemy_info(surface)

        # Log de mensagens (centro inferior)
        self._render_message_log(surface)

        # Botões de ação
        for btn in self.buttons:
            btn.render(surface)

    def _render_hero_info(self, surface):
        """Renderiza informações do herói"""
        base_x = 100
        base_y = 100

        # Título
        title_font = self.ui_scaler.get_themed_font("hud")
        title_text = title_font.render("HERÓI", True, self.theme.COLOR_ACCENT)
        title_pos = self.ui_scaler.pos(base_x, base_y)
        surface.blit(title_text, title_pos)

        # Nome
        name_font = self.ui_scaler.get_themed_font("menu")
        name_text = name_font.render(
            self.hero.name, True, self.theme.COLOR_TEXT_PRIMARY
        )
        name_pos = self.ui_scaler.pos(base_x, base_y + 40)
        surface.blit(name_text, name_pos)

        # HP
        hp_text = name_font.render(
            f"HP: {self.hero.current_hp}/{self.hero.max_hp}",
            True,
            self.theme.COLOR_SUCCESS,
        )
        hp_pos = self.ui_scaler.pos(base_x, base_y + 80)
        surface.blit(hp_text, hp_pos)

        # Barra de HP
        bar_rect = self.ui_scaler.rect(base_x, base_y + 120, 300, 20)
        pygame.draw.rect(surface, self.theme.COLOR_BORDER_EMPTY, bar_rect, 2)

        hp_percent = self.hero.current_hp / self.hero.max_hp
        filled_width = int(bar_rect.width * hp_percent)
        if filled_width > 0:
            fill_rect = pygame.Rect(
                bar_rect.x, bar_rect.y, filled_width, bar_rect.height
            )
            pygame.draw.rect(surface, self.theme.COLOR_SUCCESS, fill_rect)

    def _render_enemy_info(self, surface):
        """Renderiza informações do inimigo"""
        base_x = self.theme.BASE_WIDTH - 400
        base_y = 100

        # Título
        title_font = self.ui_scaler.get_themed_font("hud")
        title_text = title_font.render("INIMIGO", True, self.theme.COLOR_ERROR)
        title_pos = self.ui_scaler.pos(base_x, base_y)
        surface.blit(title_text, title_pos)

        # Nome
        name_font = self.ui_scaler.get_themed_font("menu")
        name_text = name_font.render(
            self.enemy.name, True, self.theme.COLOR_TEXT_PRIMARY
        )
        name_pos = self.ui_scaler.pos(base_x, base_y + 40)
        surface.blit(name_text, name_pos)

        # HP
        hp_text = name_font.render(
            f"HP: {self.enemy.current_hp}/{self.enemy.max_hp}",
            True,
            self.theme.COLOR_ERROR,
        )
        hp_pos = self.ui_scaler.pos(base_x, base_y + 80)
        surface.blit(hp_text, hp_pos)

        # Barra de HP
        bar_rect = self.ui_scaler.rect(base_x, base_y + 120, 300, 20)
        pygame.draw.rect(surface, self.theme.COLOR_BORDER_EMPTY, bar_rect, 2)

        hp_percent = self.enemy.current_hp / self.enemy.max_hp
        filled_width = int(bar_rect.width * hp_percent)
        if filled_width > 0:
            fill_rect = pygame.Rect(
                bar_rect.x, bar_rect.y, filled_width, bar_rect.height
            )
            pygame.draw.rect(surface, self.theme.COLOR_ERROR, fill_rect)

    def _render_message_log(self, surface):
        """Renderiza log de mensagens"""
        base_x = self.theme.BASE_WIDTH // 2
        base_y = self.theme.BASE_HEIGHT - 300

        message_font = self.ui_scaler.get_themed_font("menu_small")

        for i, message in enumerate(self.message_log[-3:]):  # Últimas 3 mensagens
            msg_text = message_font.render(
                message, True, self.theme.COLOR_TEXT_SECONDARY
            )
            msg_y = self.ui_scaler.scale(base_y + i * 30, "y")
            msg_rect = msg_text.get_rect(center=(surface.get_width() // 2, msg_y))
            surface.blit(msg_text, msg_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Volta ao mapa (fuga)
                self._on_run()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Apenas processa botões se for turno do jogador
            if self.battle_manager.state == BattleState.PLAYER_TURN:
                for btn in self.buttons:
                    if btn.handle_event(event):
                        return

    def enter(self):
        print(f"⚔️ Batalha iniciada: {self.hero.name} vs {self.enemy.name}")

    def exit(self):
        print("⚔️ Batalha finalizada")
