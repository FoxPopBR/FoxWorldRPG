import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager
from src.ui.menu_assets import load_menu_visual_assets, render_menu_background


class VideoSettingsState(BaseState):
    """Configurações de vídeo com UI responsiva"""

    def __init__(self, game):
        super().__init__(game)
        self.buttons = []

        # Carrega assets visuais do menu
        self.menu_assets = load_menu_visual_assets(game)

        # Configurações pendentes (para não aplicar imediatamente)
        self.pending_resolution = self.game.display_config.current_resolution
        self.pending_fullscreen = self.game.display_config.fullscreen
        self.pending_vsync = self.game.display_config.vsync

        self._create_ui()

    def _create_ui(self):
        """Cria a interface de configurações de vídeo"""
        self.buttons.clear()

        # Posições base para 1080p
        base_button_width = 400
        base_button_height = 60

        # Centraliza horizontalmente
        base_x = (self.theme.BASE_WIDTH - base_button_width) // 2

        # Botões com posições base
        button_configs = [
            (
                300,
                f"Resolução: {self.pending_resolution[0]}x{self.pending_resolution[1]}",
                self._next_resolution,
            ),
            (
                380,
                f"Tela Cheia: {'Sim' if self.pending_fullscreen else 'Não'}",
                self._toggle_fullscreen,
            ),
            (
                460,
                f"VSync: {'Sim' if self.pending_vsync else 'Não'}",
                self._toggle_vsync,
            ),
            (580, "Aplicar Configurações", self._apply_settings),
            (660, "Voltar", self._back),
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

    def _next_resolution(self):
        """Avança para a próxima resolução"""
        current = self.pending_resolution
        resolutions = self.game.display_config.SUPPORTED_RESOLUTIONS

        try:
            current_index = resolutions.index(current)
            next_index = (current_index + 1) % len(resolutions)
            self.pending_resolution = resolutions[next_index]
            self._update_resolution_text()
        except ValueError:
            self.pending_resolution = resolutions[0]
            self._update_resolution_text()

    def _previous_resolution(self):
        """Volta para a resolução anterior"""
        current = self.pending_resolution
        resolutions = self.game.display_config.SUPPORTED_RESOLUTIONS

        try:
            current_index = resolutions.index(current)
            prev_index = (current_index - 1) % len(resolutions)
            self.pending_resolution = resolutions[prev_index]
            self._update_resolution_text()
        except ValueError:
            self.pending_resolution = resolutions[-1]
            self._update_resolution_text()

    def _update_resolution_text(self):
        """Atualiza o texto do botão de resolução"""
        new_text = (
            f"Resolução: {self.pending_resolution[0]}x{self.pending_resolution[1]}"
        )
        self.buttons[0].text = new_text

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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Verifica clique direito no botão de resolução (índice 0)
            if event.button == 3:  # Botão direito
                # Verifica colisão manualmente já que Button.handle_event consome o evento
                # Precisamos acessar o rect escalado do botão
                # Como Button não expõe facilmente, vamos usar uma lógica simplificada
                # Se o mouse estiver sobre o botão 0, chama _previous_resolution
                mouse_pos = pygame.mouse.get_pos()
                # Hack: Button não expõe is_hovered publicamente de forma confiável sem update
                # Mas podemos checar se o mouse está no rect base escalado
                # Vamos assumir que o botão 0 é sempre resolução
                res_btn = self.buttons[0]
                # Button usa UIScaler internamente, mas não expõe o rect final facilmente
                # Vamos tentar usar o método handle_event do botão mas interceptar antes?
                # Não, melhor: vamos iterar e ver se colide
                # O botão tem um método _get_scaled_rect mas é privado
                # Vamos usar o rect base e o scaler do jogo
                scaled_rect = self.ui_scaler.rect(
                    res_btn.base_rect.x,
                    res_btn.base_rect.y,
                    res_btn.base_rect.width,
                    res_btn.base_rect.height,
                )
                if scaled_rect.collidepoint(mouse_pos):
                    self._previous_resolution()
                    return

            # Processar eventos de mouse nos botões (clique esquerdo e hover)
            for button in self.buttons:
                if button.handle_event(event):
                    break

    def update(self):
        dt = 1.0 / 60.0
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos, dt=dt)

    def render(self, surface, world_surface=None):
        # Fundo com escurecimento
        render_menu_background(
            surface, self.menu_assets["background"], self.theme, darkness=0.5
        )

        # Título
        title_font = self.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            "Configurações de Vídeo", True, self.theme.COLOR_TEXT_PRIMARY
        )
        title_y = self.ui_scaler.scale(120, "y")
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, title_y))
        surface.blit(title_text, title_rect)

        # Instrução
        instruction_font = self.ui_scaler.get_themed_font("menu")
        instruction_text = instruction_font.render(
            "As configurações serão aplicadas ao clicar em 'Aplicar Configurações'",
            True,
            self.theme.COLOR_TEXT_PRIMARY,
        )
        instruction_y = self.ui_scaler.scale(180, "y")
        instruction_rect = instruction_text.get_rect(
            center=(surface.get_width() // 2, instruction_y)
        )
        surface.blit(instruction_text, instruction_rect)

        # Botões
        for button in self.buttons:
            button.render(surface)

    def on_resize(self, old_size, new_size):
        """Recria a UI quando a resolução muda"""
        self._create_ui()
