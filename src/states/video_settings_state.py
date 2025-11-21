import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.responsive_ui import ResponsiveUI
from src.ui.button_manager import ButtonManager


class VideoSettingsState(BaseState):
    """Configurações de vídeo com UI responsiva"""

    def __init__(self, game):
        super().__init__(game)
        self.buttons = []

        # Configurações pendentes (para não aplicar imediatamente)
        self.pending_resolution = self.game.display_config.current_resolution
        self.pending_fullscreen = self.game.display_config.fullscreen
        self.pending_vsync = self.game.display_config.vsync

        self._create_ui()

    def _create_ui(self):
        """Cria a interface de configurações de vídeo"""
        self.buttons.clear()

        # Posições base para 1080p
        base_button_width = 600
        base_button_height = 60

        # Botões com posições base
        button_configs = [
            (
                ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2,
                300,
                f"Resolução: {self.pending_resolution[0]}x{self.pending_resolution[1]}",
                self._cycle_resolution,
                28,
            ),
            (
                ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2,
                380,
                f"Tela Cheia: {'Sim' if self.pending_fullscreen else 'Não'}",
                self._toggle_fullscreen,
                32,
            ),
            (
                ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2,
                460,
                f"VSync: {'Sim' if self.pending_vsync else 'Não'}",
                self._toggle_vsync,
                32,
            ),
            (
                ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2,
                580,
                "Aplicar Configurações",
                self._apply_settings,
                32,
            ),
            (
                ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2,
                660,
                "Voltar",
                self._back,
                32,
            ),
        ]

        for base_x, base_y, text, action, font_size in button_configs:
            button = Button(
                base_x,
                base_y,
                base_button_width,
                base_button_height,
                text,
                action,
                font_size,
            )
            self.buttons.append(button)

    def _cycle_resolution(self):
        """Alterna entre resoluções suportadas (apenas visualmente)"""
        current = self.pending_resolution
        resolutions = self.game.display_config.SUPPORTED_RESOLUTIONS

        try:
            current_index = resolutions.index(current)
            next_index = (current_index + 1) % len(resolutions)
            self.pending_resolution = resolutions[next_index]

            # Atualiza texto do botão
            new_text = (
                f"Resolução: {self.pending_resolution[0]}x{self.pending_resolution[1]}"
            )
            self.buttons[0].text = new_text

        except ValueError:
            self.pending_resolution = resolutions[0]
            self.buttons[0].text = (
                f"Resolução: {self.pending_resolution[0]}x{self.pending_resolution[1]}"
            )

    def _toggle_fullscreen(self):
        """Alterna entre tela cheia e janela (apenas visualmente)"""
        self.pending_fullscreen = not self.pending_fullscreen
        new_text = f"Tela Cheia: {'Sim' if self.pending_fullscreen else 'Não'}"
        self.buttons[1].text = new_text

    def _toggle_vsync(self):
        """Alterna VSync (apenas visualmente)"""
        self.pending_vsync = not self.pending_vsync
        new_text = f"VSync: {'Sim' if self.pending_vsync else 'Não'}"
        self.buttons[2].text = new_text

    def _apply_settings(self):
        """Aplica as configurações de vídeo pendentes"""
        try:
            # Atualiza a configuração real
            self.game.display_config.current_resolution = self.pending_resolution
            self.game.display_config.fullscreen = self.pending_fullscreen
            self.game.display_config.vsync = self.pending_vsync

            # Aplica mudanças
            self.game.change_display_mode()
            self.game.display_config.save_to_file()

            # Recria UI para garantir alinhamento
            self._create_ui()

            self.game.notification_manager.add_notification(
                "Configurações de vídeo aplicadas!", (100, 255, 100)
            )
            print("Configurações de vídeo aplicadas e salvas!")
        except Exception as e:
            print(f"Erro ao aplicar configurações: {e}")
            self.game.notification_manager.add_notification(f"Erro: {e}", (255, 50, 50))

    def _back(self):
        """Volta para o menu de configurações"""
        self.game.state_manager.pop_state()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back()
        else:
            # Processar eventos de mouse nos botões
            for button in self.buttons:
                if hasattr(button, "handle_event"):
                    if button.handle_event(event, self.game):
                        break

    def update(self):
        # Usar ButtonManager para atualizar botões
        ButtonManager.update_buttons(self.buttons, self.game)

    def render(self, surface):
        screen_width, screen_height = surface.get_size()

        # Fundo
        surface.fill(self.game.game_config.get_color("background"))

        # Título
        title_font_size = ResponsiveUI.scale_font_size(48, screen_width, screen_height)
        title_font = self.game.game_config.get_font("title", title_font_size)
        title_text = title_font.render(
            "Configurações de Vídeo", True, self.game.game_config.get_color("text")
        )
        title_y = ResponsiveUI.scale_value(120, screen_width, screen_height)
        title_rect = title_text.get_rect(center=(screen_width // 2, title_y))
        surface.blit(title_text, title_rect)

        # Instrução
        instruction_font_size = ResponsiveUI.scale_font_size(
            24, screen_width, screen_height
        )
        instruction_font = self.game.game_config.get_font("menu", instruction_font_size)
        instruction_text = instruction_font.render(
            "As configurações serão aplicadas ao clicar em 'Aplicar Configurações'",
            True,
            self.game.game_config.get_color("text"),
        )
        instruction_y = ResponsiveUI.scale_value(180, screen_width, screen_height)
        instruction_rect = instruction_text.get_rect(
            center=(screen_width // 2, instruction_y)
        )
        surface.blit(instruction_text, instruction_rect)

        # Botões usando ButtonManager
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)

    def on_resize(self, old_size, new_size):
        """Recria a UI quando a resolução muda"""
        self._create_ui()
