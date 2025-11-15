import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.responsive_ui import ResponsiveUI
from src.ui.button_manager import ButtonManager

class ThemeSelectionState(BaseState):
    """Estado para seleção de temas com destaque visual"""
    
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.theme_buttons = []
        self._create_ui()
        
    def _create_ui(self):
        """Cria a interface de seleção de temas"""
        # Botão voltar
        back_button = Button(
            ResponsiveUI.BASE_WIDTH // 2 - 200, 700, 400, 60,
            "Voltar", self._back, 32
        )
        self.buttons.append(back_button)
        
        # Botões para cada tema disponível
        available_themes = self.game.game_config.theme_manager.get_available_themes()
        theme_button_width = 350
        theme_button_height = 50
        
        start_y = 200
        for i, theme_name in enumerate(available_themes):
            y_pos = start_y + i * (theme_button_height + 15)
            
            # ✅ ALTERNATIVA: Botão especial para tema atual com cor diferente
            is_current = theme_name == self.game.game_config.theme_manager.current_theme
            
            # Usar cor diferente para o tema atual
            if is_current:
                theme_button = Button(
                    ResponsiveUI.BASE_WIDTH // 2 - theme_button_width // 2,
                    y_pos,
                    theme_button_width,
                    theme_button_height,
                    f"--> {theme_name}",
                    lambda t=theme_name: self._select_theme(t),
                    28
                )
                # Você pode customizar ainda mais a aparência do botão atual se desejar
            else:
                theme_button = Button(
                    ResponsiveUI.BASE_WIDTH // 2 - theme_button_width // 2,
                    y_pos,
                    theme_button_width,
                    theme_button_height,
                    theme_name,
                    lambda t=theme_name: self._select_theme(t),
                    28
                )
            
            self.theme_buttons.append(theme_button)
    
    def _select_theme(self, theme_name: str):
        """Seleciona um tema e SALVA no banco de dados"""
        if self.game.game_config.theme_manager.set_theme(theme_name):
            self.game.game_config.settings_manager.set_current_theme(theme_name)
            self.game.game_config.clear_cache()
            print(f"🎨 Tema alterado para: {theme_name} (salvo no banco de dados)")
            self._create_ui()
    
    def _back(self):
        """Volta para o menu de configurações"""
        self.game.state_manager.pop_state()
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back()
        else:
            all_buttons = self.buttons + self.theme_buttons
            ButtonManager.handle_button_click(all_buttons, event)
                    
    def update(self):
        all_buttons = self.buttons + self.theme_buttons
        ButtonManager.update_buttons(all_buttons, self.game)
            
    def render(self, surface):
        screen_width, screen_height = surface.get_size()
        
        surface.fill(self.game.game_config.get_color('background'))
        
        title_font_size = ResponsiveUI.scale_font_size(48, screen_width, screen_height)
        title_font = self.game.game_config.get_font('title', title_font_size)
        title_text = title_font.render("Selecionar Tema", True, self.game.game_config.get_color('text'))
        title_rect = title_text.get_rect(center=(screen_width//2, 100))
        surface.blit(title_text, title_rect)
        
        current_theme = self.game.game_config.theme_manager.current_theme
        theme_font_size = ResponsiveUI.scale_font_size(24, screen_width, screen_height)
        theme_font = self.game.game_config.get_font('menu', theme_font_size)
        theme_text = theme_font.render(f"Tema atual: {current_theme}", True, self.game.game_config.get_color('text_secondary'))
        theme_rect = theme_text.get_rect(center=(screen_width//2, 150))
        surface.blit(theme_text, theme_rect)
        
        instruction_font_size = ResponsiveUI.scale_font_size(18, screen_width, screen_height)
        instruction_font = self.game.game_config.get_font('menu', instruction_font_size)
        instruction_text = instruction_font.render(
            "--> indica o tema selecionado • Clique para mudar", 
            True, self.game.game_config.get_color('text_secondary')
        )
        instruction_rect = instruction_text.get_rect(center=(screen_width//2, 650))
        surface.blit(instruction_text, instruction_rect)
        
        all_buttons = self.buttons + self.theme_buttons
        ButtonManager.render_buttons(all_buttons, surface, self.game.game_config)