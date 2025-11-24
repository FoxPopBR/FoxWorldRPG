"""
Estado do Mapa - Exibe o mapa do mundo/zona
"""

import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager


class MapState(BaseState):
    """Estado que exibe o mapa do mundo"""

    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self._create_ui()

    def _create_ui(self):
        """Cria a interface do mapa"""
        self.buttons.clear()

        # Botão voltar
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
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F3:
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
            "MAPA DO MUNDO", True, self.theme.COLOR_TEXT_PRIMARY
        )

        title_y = self.ui_scaler.scale(40, "y")
        surface.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, title_y)
        )

        # Área do mapa
        map_x = self.ui_scaler.scale(200, "x")
        map_y = self.ui_scaler.scale(150, "y")
        map_w = self.ui_scaler.scale(1520, "x")
        map_h = self.ui_scaler.scale(750, "y")

        map_rect = pygame.Rect(map_x, map_y, map_w, map_h)
        pygame.draw.rect(surface, self.theme.COLOR_BG_CARD, map_rect, border_radius=20)
        pygame.draw.rect(
            surface, self.theme.COLOR_BORDER_DEFAULT, map_rect, 2, border_radius=20
        )

        # Grade simulando mapa
        grid_size = self.ui_scaler.scale(50, "x")
        for x in range(map_rect.left, map_rect.right, grid_size):
            pygame.draw.line(
                surface, (40, 40, 50), (x, map_rect.top), (x, map_rect.bottom), 1
            )
        for y in range(map_rect.top, map_rect.bottom, grid_size):
            pygame.draw.line(
                surface, (40, 40, 50), (map_rect.left, y), (map_rect.right, y), 1
            )

        # Indicador de posição do jogador (centro do mapa)
        player_x = map_rect.centerx
        player_y = map_rect.centery

        radius_outer = self.ui_scaler.scale(15, "x")
        radius_inner = self.ui_scaler.scale(10, "x")

        pygame.draw.circle(surface, (255, 100, 100), (player_x, player_y), radius_outer)
        pygame.draw.circle(surface, (255, 200, 200), (player_x, player_y), radius_inner)

        # Texto placeholder
        placeholder_font = self.ui_scaler.get_themed_font("menu")
        placeholder_text = placeholder_font.render(
            "🗺️ Sistema de Mapa em Desenvolvimento", True, self.theme.COLOR_TEXT_HINT
        )

        text_x = map_rect.left + self.ui_scaler.scale(50, "x")
        text_y = map_rect.bottom - self.ui_scaler.scale(100, "y")
        surface.blit(placeholder_text, (text_x, text_y))

        # Legenda
        legend_font = self.ui_scaler.get_themed_font("menu_small")
        legend_text = legend_font.render(
            "🔴 Você está aqui", True, self.theme.COLOR_TEXT_SECONDARY
        )

        legend_y = map_rect.bottom - self.ui_scaler.scale(60, "y")
        surface.blit(legend_text, (text_x, legend_y))

        # Info de atalho
        info_font = self.ui_scaler.get_themed_font("menu_small")
        info_text = info_font.render(
            "Pressione ESC ou F3 para voltar ao jogo",
            True,
            self.theme.COLOR_TEXT_SECONDARY,
        )
        info_y = screen_height - self.ui_scaler.scale(60, "y")
        surface.blit(
            info_text,
            (screen_width // 2 - info_text.get_width() // 2, info_y),
        )

        # Renderiza botões
        for btn in self.buttons:
            btn.render(surface)

    def on_resize(self, old_size, new_size):
        """Recria UI ao redimensionar"""
        self._create_ui()
