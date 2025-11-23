import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager
from src.ui.menu_assets import load_menu_visual_assets, render_menu_background


class SettingsState(BaseState):
    """Estado de configurações do jogo com todas as opções"""

    def __init__(self, game, from_game=False):
        super().__init__(game)
        self.from_game = from_game
        self.buttons = []

        # Carrega assets visuais do menu
        self.menu_assets = load_menu_visual_assets(game)

        self._create_ui()

    def _create_ui(self):
        """Cria a interface do menu de configurações"""
        self.buttons.clear()

        # Posições base para 1920x1080 (virtual)
        base_button_width = 400
        base_button_height = 70

        # Centraliza horizontalmente na resolução base
        base_x = (self.theme.BASE_WIDTH - base_button_width) // 2

        button_configs = [
            (250, "Configurações de Vídeo", self._open_video_settings),
            (340, "Configurações de Áudio", self._open_audio_settings),
            (430, "Selecionar Tema", self._open_theme_selection),
            (520, "Configurações de Controles", self._open_control_settings),
            (610, "Gerenciar Save Games", self._open_save_management),
            (
                720,
                "Voltar ao Jogo" if self.from_game else "Voltar ao Menu Principal",
                self._back_to_menu,
            ),
        ]

        for base_y, text, action in button_configs:
            button = Button(
                base_x,
                base_y,
                base_button_width,
                base_button_height,
                text,
                action,
                font_size=self.theme.FONT_MENU_LARGE,
                text_color=(255, 255, 255),
                button_image_normal=self.menu_assets["button_normal"],
                button_image_pressed=self.menu_assets["button_pressed"],
            )
            self.buttons.append(button)

    def _open_video_settings(self):
        """Abre submenu de configurações de vídeo"""
        from src.states.video_settings_state import VideoSettingsState

        self.game.state_manager.push_state(VideoSettingsState(self.game))

    def _open_audio_settings(self):
        """Abre submenu de configurações de áudio"""
        try:
            from src.states.audio_settings_state import AudioSettingsState

            self.game.state_manager.push_state(AudioSettingsState(self.game))
        except ImportError:
            print("Estado de áudio não implementado ainda")
            self._show_not_implemented("Configurações de Áudio")

    def _open_theme_selection(self):
        """Abre seletor de temas"""
        from src.states.theme_selection_state import ThemeSelectionState

        self.game.state_manager.push_state(ThemeSelectionState(self.game))

    def _open_control_settings(self):
        """Abre configurações de controles"""
        self._show_not_implemented("Configurações de Controles")

    def _open_save_management(self):
        """Abre gerenciador de save games"""
        self._show_not_implemented("Gerenciamento de Save Games")

    def _back_to_menu(self):
        """Volta para o menu principal"""
        self.game.state_manager.pop_state()

    def _show_not_implemented(self, feature_name: str):
        """Mostra mensagem para funcionalidades não implementadas"""
        print(f"{feature_name} - Em desenvolvimento")

    def handle_event(self, event):
        """Processa eventos do jogo"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back_to_menu()
            elif event.key == pygame.K_v:
                self._open_video_settings()
            elif event.key == pygame.K_a:
                self._open_audio_settings()
            elif event.key == pygame.K_t:
                self._open_theme_selection()

        else:
            # Processar eventos de mouse nos botões
            for button in self.buttons:
                if button.handle_event(event):
                    break

    def update(self):
        """Atualiza a lógica do estado"""
        dt = 1.0 / 60.0
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos, dt=dt)

    def render(self, surface):
        """Renderiza o estado"""
        # Fundo com escurecimento
        render_menu_background(
            surface, self.menu_assets["background"], self.theme, darkness=0.5
        )

        # Título principal
        title_font = self.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            "Configurações", True, self.theme.COLOR_TEXT_PRIMARY
        )

        # Centraliza usando coordenadas escaladas
        title_y = self.ui_scaler.scale(120, "y")
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, title_y))
        surface.blit(title_text, title_rect)

        # Subtítulo
        subtitle_font = self.ui_scaler.get_themed_font("menu")
        subtitle_text = subtitle_font.render(
            "Configure o jogo ao seu gosto", True, self.theme.COLOR_TEXT_SECONDARY
        )
        subtitle_y = self.ui_scaler.scale(170, "y")
        subtitle_rect = subtitle_text.get_rect(
            center=(surface.get_width() // 2, subtitle_y)
        )
        surface.blit(subtitle_text, subtitle_rect)

        # Atalhos de teclado (dica)
        hint_font = self.ui_scaler.get_themed_font("menu")
        hint_text = hint_font.render(
            "Atalhos: V (Vídeo) • A (Áudio) • T (Temas) • ESC (Voltar)",
            True,
            self.theme.COLOR_TEXT_SECONDARY,
        )
        hint_y = self.ui_scaler.scale(780, "y")
        hint_rect = hint_text.get_rect(center=(surface.get_width() // 2, hint_y))
        surface.blit(hint_text, hint_rect)

        # Botões
        for button in self.buttons:
            button.render(surface)

    def on_resize(self, old_size, new_size):
        """Recria a UI quando a resolução muda"""
        # Como usamos UIScaler, apenas recriar os botões (que usam coordenadas base) é suficiente
        # O Scaler já foi atualizado pelo Game.change_display_mode
        self._create_ui()

    def enter(self):
        """Chamado quando o estado entra em foco"""
        print("Entrando no menu de configurações")

    def exit(self):
        """Chamado quando o estado sai de foco"""
        print("Saindo do menu de configurações")
