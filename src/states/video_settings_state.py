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
        self._create_ui()
        
    def _create_ui(self):
        """Cria a interface de configurações de vídeo"""
        self.buttons.clear()
        
        # Posições base para 1080p
        base_button_width = 600
        base_button_height = 60
        
        # Botões com posições base
        button_configs = [
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 300, 
             f"Resolução: {self.game.display_config.current_resolution[0]}x{self.game.display_config.current_resolution[1]}", 
             self._cycle_resolution, 28),
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 380,
             f"Tela Cheia: {'Sim' if self.game.display_config.fullscreen else 'Não'}", 
             self._toggle_fullscreen, 32),
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 460,
             f"VSync: {'Sim' if self.game.display_config.vsync else 'Não'}", 
             self._toggle_vsync, 32),
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 580,
             "Aplicar Configurações", self._apply_settings, 32),
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 660,
             "Voltar", self._back, 32)
        ]
        
        for base_x, base_y, text, action, font_size in button_configs:
            button = Button(base_x, base_y, base_button_width, base_button_height, text, action, font_size)
            self.buttons.append(button)
        
    def _cycle_resolution(self):
        """Alterna entre resoluções suportadas"""
        current = self.game.display_config.current_resolution
        resolutions = self.game.display_config.SUPPORTED_RESOLUTIONS
        
        try:
            current_index = resolutions.index(current)
            next_index = (current_index + 1) % len(resolutions)
            self.game.display_config.current_resolution = resolutions[next_index]
            
            # Atualiza texto do botão
            new_text = f"Resolução: {resolutions[next_index][0]}x{resolutions[next_index][1]}"
            self.buttons[0].text = new_text
            
        except ValueError:
            # Se resolução atual não estiver na lista, usa a primeira
            self.game.display_config.current_resolution = resolutions[0]
    
    def _toggle_fullscreen(self):
        """Alterna entre tela cheia e janela"""
        self.game.display_config.fullscreen = not self.game.display_config.fullscreen
        new_text = f"Tela Cheia: {'Sim' if self.game.display_config.fullscreen else 'Não'}"
        self.buttons[1].text = new_text
    
    def _toggle_vsync(self):
        """Alterna VSync"""
        self.game.display_config.vsync = not self.game.display_config.vsync
        new_text = f"VSync: {'Sim' if self.game.display_config.vsync else 'Não'}"
        self.buttons[2].text = new_text
    
    def _apply_settings(self):
        """Aplica as configurações de vídeo"""
        try:
            self.game.change_display_mode()
            self.game.display_config.save_to_file()
            print("Configurações de vídeo aplicadas e salvas!")
        except Exception as e:
            print(f"Erro ao aplicar configurações: {e}")
    
    def _back(self):
        """Volta para o menu de configurações"""
        self.game.state_manager.pop_state()
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back()
        else:
            # Usar ButtonManager para processar cliques
            ButtonManager.handle_button_click(self.buttons, event)
                    
    def update(self):
        # Usar ButtonManager para atualizar botões
        ButtonManager.update_buttons(self.buttons, self.game)
            
    def render(self, surface):
        screen_width, screen_height = surface.get_size()
        
        # Fundo
        surface.fill(self.game.game_config.get_color('background'))
        
        # Título
        title_font_size = ResponsiveUI.scale_font_size(48, screen_width, screen_height)
        title_font = self.game.game_config.get_font('title', title_font_size)
        title_text = title_font.render("Configurações de Vídeo", True, self.game.game_config.get_color('text'))
        title_y = ResponsiveUI.scale_value(120, screen_width, screen_height)
        title_rect = title_text.get_rect(center=(screen_width//2, title_y))
        surface.blit(title_text, title_rect)
        
        # Instrução
        instruction_font_size = ResponsiveUI.scale_font_size(24, screen_width, screen_height)
        instruction_font = self.game.game_config.get_font('menu', instruction_font_size)
        instruction_text = instruction_font.render(
            "As configurações serão aplicadas ao clicar em 'Aplicar Configurações'", 
            True, self.game.game_config.get_color('text')
        )
        instruction_y = ResponsiveUI.scale_value(180, screen_width, screen_height)
        instruction_rect = instruction_text.get_rect(center=(screen_width//2, instruction_y))
        surface.blit(instruction_text, instruction_rect)
        
        # Botões usando ButtonManager
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)
            
    def on_resize(self, old_size, new_size):
        """Recria a UI quando a resolução muda"""
        self._create_ui()