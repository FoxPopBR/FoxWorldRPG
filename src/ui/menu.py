import pygame
from typing import List
from src.ui.button import Button
from src.ui.responsive_ui import ResponsiveUI
from src.ui.button_manager import ButtonManager

class MainMenu:
    """Menu principal do jogo com suporte a temas"""
    
    def __init__(self, game):
        self.game = game
        self.buttons: List[Button] = []
        self.background_image = None
        self._create_buttons()
        self._load_background()
        
    def _load_background(self):
        """Carrega a imagem de fundo do tema"""
        self.background_image = self.game.game_config.get_image("background")
        
    def _create_buttons(self):
        """Cria os botões do menu principal com posições base (1080p)"""
        # Posições base para 1920x1080
        base_button_width = 400
        base_button_height = 80
        
        # Posições Y base (para 1080p)
        base_positions = [400, 500, 600, 700]  # Novo Jogo, Carregar, Configurações, Sair
        
        button_configs = [
            ("Novo Jogo", self._on_new_game),
            ("Carregar Jogo", self._on_load_game),
            ("Configurações", self._on_settings),
            ("Sair", self._on_quit)
        ]
        
        for i, (text, action) in enumerate(button_configs):
            # Botão centralizado horizontalmente, posição Y base
            button = Button(
                ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2,  # X centralizado
                base_positions[i],  # Y base
                base_button_width,
                base_button_height,
                text, action, 
                base_font_size=36,
                image_key="button_normal"  # Usa imagem do tema
            )
            self.buttons.append(button)
            
    def _on_new_game(self):
        """Inicia a criação de um novo personagem"""
        from src.states.character_creation_state import CharacterCreationState
        self.game.state_manager.change_state(CharacterCreationState(self.game))
        
    def _on_load_game(self):
        print("Carregando jogo...")
        # TODO: Implementar carregamento
        
    def _on_settings(self):
        from src.states.settings_state import SettingsState
        self.game.state_manager.push_state(SettingsState(self.game))
        
    def _on_quit(self):
        self.game.running = False
        
    def handle_event(self, event):
        # Usar ButtonManager para processar cliques
        if ButtonManager.handle_button_click(self.buttons, event):
            return  # Um botão foi clicado
        
    def update(self):
        # Usar ButtonManager para atualizar botões
        ButtonManager.update_buttons(self.buttons, self.game)
            
    def render(self, surface):
        screen_width, screen_height = surface.get_size()
        
        # Fundo - imagem ou cor sólida
        if self.background_image:
            # Escalar imagem de fundo para a tela
            scaled_bg = pygame.transform.scale(self.background_image, (screen_width, screen_height))
            surface.blit(scaled_bg, (0, 0))
        else:
            # Fallback para cor sólida
            surface.fill(self.game.game_config.get_color('background'))
        
        # Logo do tema (se existir)
        logo_image = self.game.game_config.get_image("logo")
        if logo_image:
            logo_rect = logo_image.get_rect(center=(screen_width//2, ResponsiveUI.scale_value(150, screen_width, screen_height)))
            surface.blit(logo_image, logo_rect)
        else:
            # Título padrão
            title_font_size = ResponsiveUI.scale_font_size(74, screen_width, screen_height)
            title_font = self.game.game_config.get_font('title', title_font_size)
            title_text = title_font.render("FoxWorld RPG", True, self.game.game_config.get_color('text'))
            title_rect = title_text.get_rect(center=(screen_width//2, 
                                                   ResponsiveUI.scale_value(150, screen_width, screen_height)))
            surface.blit(title_text, title_rect)
        
        # Botões usando ButtonManager
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)