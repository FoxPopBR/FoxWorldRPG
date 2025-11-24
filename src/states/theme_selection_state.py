# src/states/theme_selection_state.py
import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.menu_assets import load_menu_visual_assets, render_menu_background


class ThemeSelectionState(BaseState):
    """Estado para seleção de temas - REFATORADO UIScaler"""

    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.theme_buttons = []

        # Carrega assets visuais do menu
        self.menu_assets = load_menu_visual_assets(game)

        self._create_ui()

    def _create_ui(self):
        """Cria a interface de seleção de temas"""
        self.buttons.clear()
        self.theme_buttons.clear()

        # Botão voltar (com textura)
        back_button = Button(
            self.theme.BASE_WIDTH // 2 - 200,
            700,
            400,
            60,
            "Voltar",
            self._back,
            font_size=self.theme.FONT_MENU_LARGE,
            text_color=(255, 255, 255),
            button_image_normal=self.menu_assets["button_normal"],
            button_image_pressed=self.menu_assets["button_pressed"],
        )
        self.buttons.append(back_button)

        # Botões para cada tema disponível
        available_themes = self.game.game_config.theme_manager.get_available_themes()
        theme_button_width = 350
        theme_button_height = 50
        button_spacing = 15

        base_start_y = 200

        for i, theme_name in enumerate(available_themes):
            base_y = base_start_y + i * (theme_button_height + button_spacing)
            is_current = theme_name == self.game.game_config.theme_manager.current_theme

            # Tema atual tem indicador visual
            button_text = f"→ {theme_name}" if is_current else theme_name
            button_bg = (
                self.theme.COLOR_ACCENT
                if is_current
                else self.theme.COLOR_BUTTON_DEFAULT
            )
            button_hover = (
                self.theme.COLOR_WARNING
                if is_current
                else self.theme.COLOR_BUTTON_HOVER
            )

            theme_button = Button(
                self.theme.BASE_WIDTH // 2 - theme_button_width // 2,
                base_y,
                theme_button_width,
                theme_button_height,
                button_text,
                lambda t=theme_name: self._select_theme(t),
                font_size=self.theme.FONT_MENU_MEDIUM,
                text_color=(255, 255, 255),
                button_image_normal=self.menu_assets["button_normal"],
                button_image_pressed=self.menu_assets["button_pressed"],
            )

            self.theme_buttons.append(theme_button)

    def _select_theme(self, theme_name: str):
        """Seleciona um tema e salva no banco de dados"""
        if self.game.game_config.theme_manager.set_theme(theme_name):
            self.game.game_config.settings_manager.set_current_theme(theme_name)
            self.game.game_config.clear_cache()
            print(f"🎨 Tema alterado para: {theme_name} (salvo no banco de dados)")
            self._create_ui()

    def _back(self):
        """Volta para o menu de configurações"""
        current_theme = self.game.game_config.theme_manager.current_theme
        theme_font = self.ui_scaler.get_themed_font("menu")
        theme_text = theme_font.render(
            f"Tema atual: {current_theme}", True, self.theme.COLOR_TEXT_SECONDARY
        )
        theme_y = self.ui_scaler.scale(150, "y")
        theme_rect = theme_text.get_rect(center=(surface.get_width() // 2, theme_y))
        surface.blit(theme_text, theme_rect)

        # Instrução
        instruction_font = self.ui_scaler.get_themed_font("menu_small")
        instruction_text = instruction_font.render(
            "→ indica o tema selecionado • Clique para mudar",
            True,
            self.theme.COLOR_TEXT_HINT,
        )
        instruction_y = self.ui_scaler.scale(650, "y")
        instruction_rect = instruction_text.get_rect(
            center=(surface.get_width() // 2, instruction_y)
        )
        surface.blit(instruction_text, instruction_rect)

        # Botões
        all_buttons = self.buttons + self.theme_buttons
        for button in all_buttons:
            button.render(surface)
