import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.responsive_ui import ResponsiveUI
from src.ui.button_manager import ButtonManager

class SettingsState(BaseState):
    """Estado de configurações do jogo com todas as opções"""
    
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self._create_ui()
        
    def _create_ui(self):
        """Cria a interface do menu de configurações"""
        self.buttons.clear()
        
        # Posições base para 1080p
        base_button_width = 500
        base_button_height = 70
        
        # ✅ CORREÇÃO: Removidos emojis dos textos
        button_configs = [
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 250, 
             "Configurações de Vídeo", self._open_video_settings),
            
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 340,
             "Configurações de Áudio", self._open_audio_settings),
            
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 430,
             "Selecionar Tema", self._open_theme_selection),
            
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 520,
             "Configurações de Controles", self._open_control_settings),
            
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 610,
             "Gerenciar Save Games", self._open_save_management),
            
            (ResponsiveUI.BASE_WIDTH // 2 - base_button_width // 2, 720,
             "Voltar ao Menu Principal", self._back_to_menu)
        ]
        
        for base_x, base_y, text, action in button_configs:
            button = Button(
                base_x, base_y, base_button_width, base_button_height,
                text, action, base_font_size=28
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
            # Usar ButtonManager para processar cliques
            ButtonManager.handle_button_click(self.buttons, event)
                    
    def update(self):
        """Atualiza a lógica do estado"""
        ButtonManager.update_buttons(self.buttons, self.game)
            
    def render(self, surface):
        """Renderiza o estado"""
        screen_width, screen_height = surface.get_size()
        
        # Fundo
        surface.fill(self.game.game_config.get_color('background'))
        
        # Título principal
        title_font_size = ResponsiveUI.scale_font_size(64, screen_width, screen_height)
        title_font = self.game.game_config.get_font('title', title_font_size)
        title_text = title_font.render("Configurações", True, self.game.game_config.get_color('text'))
        title_y = ResponsiveUI.scale_value(120, screen_width, screen_height)
        title_rect = title_text.get_rect(center=(screen_width//2, title_y))
        surface.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_font_size = ResponsiveUI.scale_font_size(24, screen_width, screen_height)
        subtitle_font = self.game.game_config.get_font('menu', subtitle_font_size)
        subtitle_text = subtitle_font.render(
            "Configure o jogo ao seu gosto", 
            True, self.game.game_config.get_color('text_secondary')
        )
        subtitle_y = ResponsiveUI.scale_value(170, screen_width, screen_height)
        subtitle_rect = subtitle_text.get_rect(center=(screen_width//2, subtitle_y))
        surface.blit(subtitle_text, subtitle_rect)
        
        # Atalhos de teclado (dica)
        hint_font_size = ResponsiveUI.scale_font_size(18, screen_width, screen_height)
        hint_font = self.game.game_config.get_font('menu', hint_font_size)
        hint_text = hint_font.render(
            "Atalhos: V (Vídeo) • A (Áudio) • T (Temas) • ESC (Voltar)", 
            True, self.game.game_config.get_color('text_secondary')
        )
        hint_y = ResponsiveUI.scale_value(780, screen_width, screen_height)
        hint_rect = hint_text.get_rect(center=(screen_width//2, hint_y))
        surface.blit(hint_text, hint_rect)
        
        # Botões usando ButtonManager
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)
            
    def on_resize(self, old_size, new_size):
        """Recria a UI quando a resolução muda"""
        self._create_ui()
        
    def enter(self):
        """Chamado quando o estado entra em foco"""
        print("Entrando no menu de configurações")
        
    def exit(self):
        """Chamado quando o estado sai de foco"""
        print("Saindo do menu de configurações")