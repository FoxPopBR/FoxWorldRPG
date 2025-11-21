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
        self.game = game
        self.buttons = []
        self._create_ui()

    def _create_ui(self):
        """Cria a interface do mapa"""
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
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F3:
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
        title_text = title_font.render("MAPA DO MUNDO", True, (255, 255, 255))
        surface.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 40))

        # Área do mapa (placeholder)
        map_rect = pygame.Rect(200, 150, 1520, 750)
        pygame.draw.rect(surface, (30, 30, 40), map_rect, border_radius=20)
        pygame.draw.rect(surface, (60, 60, 80), map_rect, 2, border_radius=20)

        # Grade simulando mapa
        grid_size = 50
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
        pygame.draw.circle(surface, (255, 100, 100), (player_x, player_y), 15)
        pygame.draw.circle(surface, (255, 200, 200), (player_x, player_y), 10)

        # Texto placeholder
        placeholder_font = self.game.game_config.get_font("menu", 28)
        placeholder_text = placeholder_font.render(
            "🗺️ Sistema de Mapa em Desenvolvimento", True, (180, 180, 180)
        )
        surface.blit(placeholder_text, (map_rect.left + 50, map_rect.bottom - 100))

        # Legenda
        legend_font = self.game.game_config.get_font("menu", 20)
        legend_text = legend_font.render("🔴 Você está aqui", True, (220, 220, 220))
        surface.blit(legend_text, (map_rect.left + 50, map_rect.bottom - 60))

        # Info de atalho
        info_font = self.game.game_config.get_font("menu", 20)
        info_text = info_font.render(
            "Pressione ESC ou F3 para voltar ao jogo", True, (150, 150, 150)
        )
        surface.blit(
            info_text,
            (screen_width // 2 - info_text.get_width() // 2, screen_height - 60),
        )

        # Renderiza botões
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)
