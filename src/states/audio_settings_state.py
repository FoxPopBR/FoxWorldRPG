import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager
from src.ui.menu_assets import load_menu_visual_assets, render_menu_background


class AudioSettingsState(BaseState):
    """Estado de configurações de áudio com controles +/-"""

    def __init__(self, game):
        super().__init__(game)
        print("✅ AudioSettingsState carregado com sucesso (Versão Padronizada)")
        self.volume_controls = []
        self.action_buttons = []

        # Carrega assets visuais do menu
        self.menu_assets = load_menu_visual_assets(game)

        self._create_ui()

    def _create_ui(self):
        """Cria a interface de configurações de áudio"""
        self.volume_controls.clear()
        self.action_buttons.clear()

        # Obter configurações atuais
        audio_settings = self.game.game_config.settings_manager.get_audio_settings()

        # Configurações de layout
        control_width = 80
        label_width = 340
        control_height = 60
        spacing = 20
        start_y = 200

        # Controles de volume - cada linha tem: [-] [Label] [+]
        volume_types = [
            ("master_volume", "Volume Geral"),
            ("music_volume", "Volume Música"),
            ("sfx_volume", "Volume Efeitos"),
            ("voice_volume", "Volume Voz"),
        ]

        for i, (volume_key, label) in enumerate(volume_types):
            y_pos = start_y + i * (control_height + 20)
            current_volume = audio_settings.get(volume_key, 1.0)

            # Botão -
            minus_btn = Button(
                self.theme.BASE_WIDTH // 2 - control_width - label_width // 2 - spacing,
                y_pos,
                control_width,
                control_height,
                "-",
                lambda k=volume_key: self._adjust_volume(k, -0.1),
                font_size=self.theme.FONT_TITLE_SMALL,
                text_color=(255, 255, 255),
                button_image_normal=self.menu_assets["small_button_normal"],
                button_image_pressed=self.menu_assets["small_button_pressed"],
            )

            # Label com valor atual
            label_btn = Button(
                self.theme.BASE_WIDTH // 2 - label_width // 2,
                y_pos,
                label_width,
                control_height,
                f"{label}: {int(current_volume * 100)}%",
                None,
                font_size=self.theme.FONT_MENU_LARGE,
                text_color=(255, 255, 255),
                button_image_normal=self.menu_assets["button_normal"],
                button_image_pressed=self.menu_assets["button_pressed"],
            )
            label_btn.action = None

            # Botão +
            plus_btn = Button(
                self.theme.BASE_WIDTH // 2 + label_width // 2 + spacing,
                y_pos,
                control_width,
                control_height,
                "+",
                lambda k=volume_key: self._adjust_volume(k, 0.1),
                font_size=self.theme.FONT_TITLE_SMALL,
                text_color=(255, 255, 255),
                button_image_normal=self.menu_assets["small_button_normal"],
                button_image_pressed=self.menu_assets["small_button_pressed"],
            )

            self.volume_controls.append((minus_btn, label_btn, plus_btn))

        # Botões de ação posicionados MAIS ABAIXO
        action_start_y = start_y + len(volume_types) * (control_height + 20) + 80

        # Botões de ação (com texturas)
        base_button_width = 400
        button_x = (self.theme.BASE_WIDTH - base_button_width) // 2

        action_configs = [
            (action_start_y, "Resetar Todos os Volumes", self._reset_volumes),
            (action_start_y + 90, "Voltar", self._back),
        ]

        for y, text, action in action_configs:
            button = Button(
                button_x,
                y,
                base_button_width,
                60,
                text,
                action,
                font_size=self.theme.FONT_MENU_LARGE,
                text_color=(255, 255, 255),
                button_image_normal=self.menu_assets["button_normal"],
                button_image_pressed=self.menu_assets["button_pressed"],
            )
            self.action_buttons.append(button)

    def _adjust_volume(self, volume_key: str, change: float):
        """Ajusta o volume específico"""
        current = self.game.game_config.settings_manager.get_audio_setting(
            volume_key, 1.0
        )
        new_volume = max(0.0, min(1.0, round(current + change, 1)))

        self.game.game_config.settings_manager.set_audio_setting(volume_key, new_volume)
        self._update_volume_labels()
        self._apply_audio_settings()

        print(f"🔊 {volume_key}: {int(new_volume * 100)}%")

    def _reset_volumes(self):
        """Reseta todos os volumes para padrão"""
        self.game.game_config.settings_manager.set_audio_setting("master_volume", 1.0)
        self.game.game_config.settings_manager.set_audio_setting("music_volume", 0.8)
        self.game.game_config.settings_manager.set_audio_setting("sfx_volume", 0.9)
        self.game.game_config.settings_manager.set_audio_setting("voice_volume", 1.0)
        self._update_volume_labels()
        self._apply_audio_settings()
        print("✅ Volumes resetados para padrão")

    def _update_volume_labels(self):
        """Atualiza os textos dos labels de volume"""
        audio_settings = self.game.game_config.settings_manager.get_audio_settings()

        volume_types = ["master_volume", "music_volume", "sfx_volume", "voice_volume"]
        labels = ["Volume Geral", "Volume Música", "Volume Efeitos", "Volume Voz"]

        for i, (volume_key, label_text) in enumerate(zip(volume_types, labels)):
            if i < len(self.volume_controls):
                current_volume = audio_settings.get(volume_key, 1.0)
                _, label_btn, _ = self.volume_controls[i]
                label_btn.text = f"{label_text}: {int(current_volume * 100)}%"

    def _apply_audio_settings(self):
        """Aplica as configurações de áudio no sistema"""
        audio_settings = self.game.game_config.settings_manager.get_audio_settings()

        master_volume = audio_settings.get("master_volume", 1.0)
        music_volume = audio_settings.get("music_volume", 0.8)
        sfx_volume = audio_settings.get("sfx_volume", 0.9)

        print(
            f"🎵 Aplicando volumes: Master={master_volume}, Música={music_volume}, SFX={sfx_volume}"
        )

        # Aplica no jogo
        if hasattr(self.game, "apply_audio_settings"):
            self.game.apply_audio_settings()

    def _back(self):
        """Volta para configurações"""
        self.game.state_manager.pop_state()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back()
        else:
            all_buttons = []
            for minus_btn, label_btn, plus_btn in self.volume_controls:
                all_buttons.extend([minus_btn, plus_btn])
            all_buttons.extend(self.action_buttons)

            # Processar eventos de mouse nos botões
            for button in all_buttons:
                if button.handle_event(event):
                    break

    def update(self):
        dt = 1.0 / 60.0
        mouse_pos = pygame.mouse.get_pos()

        all_buttons = []
        for minus_btn, label_btn, plus_btn in self.volume_controls:
            all_buttons.extend([minus_btn, label_btn, plus_btn])
        all_buttons.extend(self.action_buttons)

        for button in all_buttons:
            button.update(mouse_pos, dt=dt)

    def render(self, surface):
        # Fundo com escurecimento
        render_menu_background(
            surface, self.menu_assets["background"], self.theme, darkness=0.5
        )

        # Título
        title_font = self.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            "Configurações de Áudio", True, self.theme.COLOR_TEXT_PRIMARY
        )
        title_y = self.ui_scaler.scale(100, "y")
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, title_y))
        surface.blit(title_text, title_rect)

        # Instrução
        instruction_font = self.ui_scaler.get_themed_font("menu")
        instruction_text = instruction_font.render(
            "Use os botões + e - para ajustar os volumes (10% por clique)",
            True,
            self.theme.COLOR_TEXT_SECONDARY,
        )
        instruction_y = self.ui_scaler.scale(150, "y")
        instruction_rect = instruction_text.get_rect(
            center=(surface.get_width() // 2, instruction_y)
        )
        surface.blit(instruction_text, instruction_rect)

        for minus_btn, label_btn, plus_btn in self.volume_controls:
            minus_btn.render(surface)
            label_btn.render(surface)
            plus_btn.render(surface)

        for button in self.action_buttons:
            button.render(surface)

    def enter(self):
        print("Entrando nas configurações de áudio")

    def exit(self):
        print("Saindo das configurações de áudio")
