"""
Estado do Perfil - Exibe informações detalhadas do herói ativo
"""

import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager


class ProfileState(BaseState):
    """Estado que exibe o perfil completo do herói"""

    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.hero = self.game.game_config.hero_manager.get_active_hero()
        self._create_ui()

    def _create_ui(self):
        """Cria a interface do perfil"""
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
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F2:
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
        if self.hero:
            title_text = title_font.render(
                f"PERFIL - {self.hero.name.upper()}", True, (255, 255, 255)
            )
        else:
            title_text = title_font.render("PERFIL", True, (255, 255, 255))
        surface.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 40))

        if not self.hero:
            # Mensagem de erro
            error_font = self.game.game_config.get_font("menu", 28)
            error_text = error_font.render(
                "⚠️ Nenhum herói ativo encontrado", True, (255, 100, 100)
            )
            surface.blit(
                error_text,
                (
                    screen_width // 2 - error_text.get_width() // 2,
                    screen_height // 2,
                ),
            )
        else:
            # Área do perfil (placeholder)
            profile_rect = pygame.Rect(200, 150, 1520, 750)
            pygame.draw.rect(surface, (30, 30, 40), profile_rect, border_radius=20)
            pygame.draw.rect(surface, (60, 60, 80), profile_rect, 2, border_radius=20)

            # Exibe informações básicas
            y_offset = 200
            info_font = self.game.game_config.get_font("menu", 24)

            info_texts = [
                f"Classe: {self.hero.hero_class.value}",
                f"Nível: {self.hero.level}",
                f"HP: {self.hero.stats.vida_maxima}",
                f"MP: {self.hero.stats.mana_maxima}",
                "",
                "📊 Atributos Base:",
                f"Força: {self.hero.stats.forca}",
                f"Destreza: {self.hero.stats.destreza}",
                f"Vitalidade: {self.hero.stats.vitalidade}",
                f"Inteligência: {self.hero.stats.inteligencia}",
                f"Armadura: {self.hero.stats.armadura}",
                f"Mana: {self.hero.stats.mana}",
                f"Stamina: {self.hero.stats.stamina}",
            ]

            for text in info_texts:
                if text:  # Pula linhas vazias
                    text_surface = info_font.render(text, True, (220, 220, 220))
                    surface.blit(text_surface, (250, y_offset))
                y_offset += 35

        # Info de atalho
        info_font = self.game.game_config.get_font("menu", 20)
        info_text = info_font.render(
            "Pressione ESC ou F2 para voltar ao jogo", True, (150, 150, 150)
        )
        surface.blit(
            info_text,
            (screen_width // 2 - info_text.get_width() // 2, screen_height - 60),
        )

        # Renderiza botões
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)
