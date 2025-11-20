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
        
        # Configurações dos botões
        button_width = 300
        button_height = 70
        start_y = 400
        spacing = 20
        
        # Botões do menu
        buttons_config = [
            ("NOVO JOGO", self._new_game),
            ("CONFIGURAÇÕES", self._settings),
            ("SAIR", self._quit)
        ]
        
        # Calcular posição centralizada
        total_height = (button_height * len(buttons_config)) + (spacing * (len(buttons_config) - 1))
        start_y = (1080 - total_height) // 2
        
        for i, (text, action) in enumerate(buttons_config):
            y_pos = start_y + i * (button_height + spacing)
            x_pos = (1920 - button_width) // 2
            
            button = Button(
                x_pos, y_pos, button_width, button_height,
                text, action, font_size=28
            )
            self.buttons.append(button)
    
    def _new_game(self):
        """Inicia um novo jogo"""
        print("🎮 Iniciando novo jogo...")
        from src.states.character_creation_state import CharacterCreationState
        self.game.state_manager.change_state(CharacterCreationState(self.game))
    
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
        """Renderiza o menu"""
        # Fundo
        surface.fill(self.game.game_config.get_color('background'))
        
        # Título
        title_font = self.game.game_config.get_font('title', 72)
        title_text = title_font.render("FOXWORLD RPG", True, (255, 255, 255))
        surface.blit(title_text, (1920//2 - title_text.get_width()//2, 200))
        
        # Subtítulo
        subtitle_font = self.game.game_config.get_font('menu', 24)
        subtitle_text = subtitle_font.render("Uma Aventura Épica", True, (200, 200, 200))
        surface.blit(subtitle_text, (1920//2 - subtitle_text.get_width()//2, 300))
        
        # Renderizar botões
        for button in self.buttons:
            button.render(surface, self.game.game_config)