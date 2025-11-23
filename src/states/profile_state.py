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
        super().__init__(game)
        self.buttons = []
        self.hero = self.game.game_config.hero_manager.get_active_hero()
        self._create_ui()

    def _create_ui(self):
        """Cria a interface do perfil"""
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
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F2:
                self._back_to_game()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            ButtonManager.handle_button_click(self.buttons, event, self.game)

    def update(self):
        """Atualiza o estado"""
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, surface):
        """Renderiza a tela"""
        surface.fill(self.theme.COLOR_BACKGROUND)

        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Título
        title_font = self.ui_scaler.get_themed_font("title")
        if self.hero:
            title_text = title_font.render(
                f"PERFIL - {self.hero.name.upper()}",
                True,
                self.theme.COLOR_TEXT_PRIMARY,
            )
        else:
            title_text = title_font.render(
                "PERFIL", True, self.theme.COLOR_TEXT_PRIMARY
            )

        title_y = self.ui_scaler.scale(40, "y")
        surface.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, title_y)
        )

        if not self.hero:
            # Mensagem de erro
            error_font = self.ui_scaler.get_themed_font("menu")
            error_text = error_font.render(
                "⚠️ Nenhum herói ativo encontrado", True, self.theme.COLOR_BUTTON_DANGER
            )
            surface.blit(
                error_text,
                (
                    screen_width // 2 - error_text.get_width() // 2,
                    screen_height // 2,
                ),
            )
        else:
            # Área do perfil
            prof_x = self.ui_scaler.scale(200, "x")
            prof_y = self.ui_scaler.scale(150, "y")
            prof_w = self.ui_scaler.scale(1520, "x")
            prof_h = self.ui_scaler.scale(750, "y")

            profile_rect = pygame.Rect(prof_x, prof_y, prof_w, prof_h)
            pygame.draw.rect(
                surface, self.theme.COLOR_BG_CARD, profile_rect, border_radius=20
            )
            pygame.draw.rect(
                surface,
                self.theme.COLOR_BORDER_DEFAULT,
                profile_rect,
                2,
                border_radius=20,
            )

            # Exibe informações básicas
            y_offset = self.ui_scaler.scale(200, "y")
            x_offset = self.ui_scaler.scale(250, "x")
            line_height = self.ui_scaler.scale(35, "y")

            info_font = self.ui_scaler.get_themed_font("menu")

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
                    text_surface = info_font.render(
                        text, True, self.theme.COLOR_TEXT_SECONDARY
                    )
                    surface.blit(text_surface, (x_offset, y_offset))
                y_offset += line_height

        # Info de atalho
        info_font = self.ui_scaler.get_themed_font("menu_small")
        info_text = info_font.render(
            "Pressione ESC ou F2 para voltar ao jogo",
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
