import pygame
from .button import Button
from .responsive_ui import ResponsiveUI
from .button_manager import ButtonManager


class MainMenu:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        """Cria os botões do menu principal"""
        self.buttons.clear()
        scaler = self.game.ui_scaler

        # Configurações dos botões (valores base 1920x1080)
        button_width = 300
        button_height = 70
        spacing = 20

        # Botões do menu
        buttons_config = [
            ("NOVO JOGO", self._new_game),
            ("CONTINUAR", self._continue_game),
            ("CONFIGURAÇÕES", self._settings),
            ("SAIR", self._quit),
        ]

        # Calcular posição centralizada (em base)
        total_height = (button_height * len(buttons_config)) + (
            spacing * (len(buttons_config) - 1)
        )
        start_y = (1080 - total_height) // 2

        for i, (text, action) in enumerate(buttons_config):
            y_pos = start_y + i * (button_height + spacing)
            x_pos = (1920 - button_width) // 2

            button = Button(
                x_pos, y_pos, button_width, button_height, text, action, font_size=28
            )
            self.buttons.append(button)

    def _new_game(self):
        """Inicia um novo jogo - vai para seleção de slots"""
        print("🎮 Abrindo seleção de slots de jogo...")
        from src.states.game_slot_select_state import GameSlotSelectState

        self.game.state_manager.change_state(GameSlotSelectState(self.game))

    def _continue_game(self):
        """Continua um jogo - vai para seleção de slots"""
        print("💾 Abrindo seleção de slots de jogo...")
        from src.states.game_slot_select_state import GameSlotSelectState

        self.game.state_manager.change_state(GameSlotSelectState(self.game))

    def _settings(self):
        """Abre as configurações"""
        print("⚙️ Abrindo configurações...")
        from src.states.settings_state import SettingsState

        self.game.state_manager.push_state(SettingsState(self.game))

    def _quit(self):
        """Sai do jogo"""
        print("👋 Saindo do jogo...")
        self.game.running = False

    def handle_event(self, event):
        """Processa eventos do menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_RETURN:
                self._new_game()
            elif event.key == pygame.K_DOWN:
                self._focus_next_button()
            elif event.key == pygame.K_UP:
                self._focus_previous_button()

        # CORREÇÃO: Usar ButtonManager para processar cliques
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ButtonManager.handle_button_click(self.buttons, event, self.game)

    def _focus_next_button(self):
        """Foca no próximo botão (para navegação por teclado)"""
        pass

    def _focus_previous_button(self):
        """Foca no botão anterior (para navegação por teclado)"""
        pass

    def update(self):
        """Atualiza o estado do menu"""
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos, self.game)

    def render(self, surface):
        """Renderiza o menu - USANDO UIScaler"""
        scaler = self.game.ui_scaler

        # Fundo
        surface.fill(self.game.game_config.get_color("background"))

        # Título - usa fonte escalada
        title_font = scaler.get_font(None, 72)
        title_text = title_font.render("FOXWORLD RPG", True, (255, 255, 255))
        title_x = scaler.center_x(title_text.get_width())
        title_y = scaler.scale(200, "y")
        surface.blit(title_text, (title_x, title_y))

        # Subtítulo
        subtitle_font = scaler.get_font(None, 24)
        subtitle_text = subtitle_font.render(
            "Uma Aventura Épica", True, (200, 200, 200)
        )
        subtitle_x = scaler.center_x(subtitle_text.get_width())
        subtitle_y = scaler.scale(300, "y")
        surface.blit(subtitle_text, (subtitle_x, subtitle_y))

        # Renderizar botões (button.render já deve escalar internamente)
        for button in self.buttons:
            button.render(surface, self.game.game_config)
