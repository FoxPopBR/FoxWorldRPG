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
        self.game = game
        self.buttons = []
        self._create_ui()

    def _create_ui(self):
        """Cria a interface do inventário"""
        self.buttons.clear()

        # Botão voltar
        back_btn = Button(100, 980, 200, 60, "VOLTAR (ESC)", self._back_to_game, 24)
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
        ButtonManager.update_buttons(self.buttons, self.game)

    def render(self, surface):
        """Renderiza a tela"""
        screen_width, screen_height = surface.get_size()

        # Fundo
        surface.fill(self.game.game_config.get_color("background"))

        # Título
        title_font = self.game.game_config.get_font("title", 60)
        title_text = title_font.render("INVENTÁRIO", True, (255, 255, 255))
        surface.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 40))

        # Área do inventário (placeholder)
        inventory_rect = pygame.Rect(200, 150, 1520, 750)
        pygame.draw.rect(surface, (30, 30, 40), inventory_rect, border_radius=20)
        pygame.draw.rect(surface, (60, 60, 80), inventory_rect, 2, border_radius=20)

        # Texto placeholder
        placeholder_font = self.game.game_config.get_font("menu", 28)
        placeholder_text = placeholder_font.render(
            "🎒 Sistema de Inventário em Desenvolvimento", True, (180, 180, 180)
        )
        surface.blit(
            placeholder_text,
            (
                screen_width // 2 - placeholder_text.get_width() // 2,
                screen_height // 2 - 50,
            ),
        )

        info_font = self.game.game_config.get_font("menu", 20)
        info_text = info_font.render(
            "Pressione ESC ou F1 para voltar ao jogo", True, (150, 150, 150)
        )
        surface.blit(
            info_text,
            (
                screen_width // 2 - info_text.get_width() // 2,
                screen_height // 2 + 20,
            ),
        )

        # Renderiza botões
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)
