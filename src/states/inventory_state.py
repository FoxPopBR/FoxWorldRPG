"""
Estado do Inventário - Gerencia a tela de itens do jogador
"""

import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager


class InventoryState(BaseState):
    """Estado que exibe o inventário do jogador"""

    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self._create_ui()

    def _create_ui(self):
        """Cria a interface do inventário"""
        self.buttons.clear()

        # Botão voltar
        # Posição relativa: x=100, y=980 (em 1080p)
        back_btn = Button(
            100,
            980,
            200,
            60,
            "VOLTAR (ESC)",
            self._back_to_game,
            font_size=self.theme.FONT_MENU_MEDIUM,
        )
        self.buttons.append(back_btn)

    def _back_to_game(self):
        """Volta para o GameState"""
        from src.states.game_state import GameState

        self.game.state_manager.change_state(GameState(self.game))

    def handle_event(self, event):
        """Processa eventos"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F1:
                self._back_to_game()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            ButtonManager.handle_button_click(self.buttons, event, self.game)

    def update(self):
        """Atualiza o estado"""
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, surface, world_surface=None):
        """Renderiza a tela"""
        surface.fill(self.theme.COLOR_BACKGROUND)

        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Título
        title_font = self.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            "INVENTÁRIO", True, self.theme.COLOR_TEXT_PRIMARY
        )

        title_y = self.ui_scaler.scale(40, "y")
        surface.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, title_y)
        )

        # Área do inventário
        # Base: 200, 150, 1520, 750
        inv_x = self.ui_scaler.scale(200, "x")
        inv_y = self.ui_scaler.scale(150, "y")
        inv_w = self.ui_scaler.scale(1520, "x")
        inv_h = self.ui_scaler.scale(750, "y")

        inventory_rect = pygame.Rect(inv_x, inv_y, inv_w, inv_h)
        pygame.draw.rect(
            surface, self.theme.COLOR_BG_CARD, inventory_rect, border_radius=20
        )
        pygame.draw.rect(
            surface,
            self.theme.COLOR_BORDER_DEFAULT,
            inventory_rect,
            2,
            border_radius=20,
        )

        # Texto placeholder
        placeholder_font = self.ui_scaler.get_themed_font("menu")
        placeholder_text = placeholder_font.render(
            "🎒 Sistema de Inventário em Desenvolvimento",
            True,
            self.theme.COLOR_TEXT_HINT,
        )

        center_x = inventory_rect.centerx
        center_y = inventory_rect.centery

        surface.blit(
            placeholder_text,
            (
                center_x - placeholder_text.get_width() // 2,
                center_y - 50,
            ),
        )

        info_font = self.ui_scaler.get_themed_font("menu_small")
        info_text = info_font.render(
            "Pressione ESC ou F1 para voltar ao jogo",
            True,
            self.theme.COLOR_TEXT_SECONDARY,
        )
        surface.blit(
            info_text,
            (
                center_x - info_text.get_width() // 2,
                center_y + 20,
            ),
        )

        # Renderiza botões
        for btn in self.buttons:
            btn.render(surface)

    def on_resize(self, old_size, new_size):
        """Recria UI ao redimensionar"""
        self._create_ui()
