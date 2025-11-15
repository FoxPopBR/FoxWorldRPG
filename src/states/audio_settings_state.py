import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.responsive_ui import ResponsiveUI
from src.ui.button_manager import ButtonManager

class AudioSettingsState(BaseState):
    """Estado de configurações de áudio com controles +/-"""
    
    def __init__(self, game):
        super().__init__(game)
        self.volume_controls = []
        self.action_buttons = []
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
            ('master_volume', "Volume Geral"),
            ('music_volume', "Volume Música"), 
            ('sfx_volume', "Volume Efeitos"),
            ('voice_volume', "Volume Voz")
        ]
        
        for i, (volume_key, label) in enumerate(volume_types):
            y_pos = start_y + i * (control_height + 20)
            current_volume = audio_settings.get(volume_key, 1.0)
            
            # Botão -
            minus_btn = Button(
                ResponsiveUI.BASE_WIDTH // 2 - control_width - label_width // 2 - spacing,
                y_pos,
                control_width,
                control_height,
                "-",
                lambda k=volume_key: self._adjust_volume(k, -0.1),
                36
            )
            
            # Label com valor atual
            label_btn = Button(
                ResponsiveUI.BASE_WIDTH // 2 - label_width // 2,
                y_pos,
                label_width,
                control_height,
                f"{label}: {int(current_volume * 100)}%",
                None,
                28
            )
            label_btn.action = None
            
            # Botão +
            plus_btn = Button(
                ResponsiveUI.BASE_WIDTH // 2 + label_width // 2 + spacing,
                y_pos,
                control_width,
                control_height,
                "+", 
                lambda k=volume_key: self._adjust_volume(k, 0.1),
                36
            )
            
            self.volume_controls.append((minus_btn, label_btn, plus_btn))
        
        # ✅ CORREÇÃO: Botões de ação posicionados MAIS ABAIXO
        action_start_y = start_y + len(volume_types) * (control_height + 20) + 80
        
        action_configs = [
            (ResponsiveUI.BASE_WIDTH // 2 - 300, action_start_y, 600, 60,
             "Resetar Todos os Volumes", self._reset_volumes, 28),
             
            (ResponsiveUI.BASE_WIDTH // 2 - 300, action_start_y + 90, 600, 60,
             "Voltar", self._back, 32)
        ]
        
        for x, y, width, height, text, action, font_size in action_configs:
            button = Button(x, y, width, height, text, action, font_size)
            self.action_buttons.append(button)
    
    def _adjust_volume(self, volume_key: str, change: float):
        """Ajusta o volume específico"""
        current = self.game.game_config.settings_manager.get_audio_setting(volume_key, 1.0)
        new_volume = max(0.0, min(1.0, round(current + change, 1)))
        
        self.game.game_config.settings_manager.set_audio_setting(volume_key, new_volume)
        self._update_volume_labels()
        self._apply_audio_settings()
        
        print(f"🔊 {volume_key}: {int(new_volume * 100)}%")
    
    def _reset_volumes(self):
        """Reseta todos os volumes para padrão"""
        self.game.game_config.settings_manager.set_audio_setting('master_volume', 1.0)
        self.game.game_config.settings_manager.set_audio_setting('music_volume', 0.8)
        self.game.game_config.settings_manager.set_audio_setting('sfx_volume', 0.9)
        self.game.game_config.settings_manager.set_audio_setting('voice_volume', 1.0)
        self._update_volume_labels()
        self._apply_audio_settings()
        print("✅ Volumes resetados para padrão")
    
    def _update_volume_labels(self):
        """Atualiza os textos dos labels de volume"""
        audio_settings = self.game.game_config.settings_manager.get_audio_settings()
        
        volume_types = ['master_volume', 'music_volume', 'sfx_volume', 'voice_volume']
        labels = ["Volume Geral", "Volume Música", "Volume Efeitos", "Volume Voz"]
        
        for i, (volume_key, label_text) in enumerate(zip(volume_types, labels)):
            if i < len(self.volume_controls):
                current_volume = audio_settings.get(volume_key, 1.0)
                _, label_btn, _ = self.volume_controls[i]
                label_btn.text = f"{label_text}: {int(current_volume * 100)}%"
    
    def _apply_audio_settings(self):
        """Aplica as configurações de áudio no sistema"""
        audio_settings = self.game.game_config.settings_manager.get_audio_settings()
        
        master_volume = audio_settings.get('master_volume', 1.0)
        music_volume = audio_settings.get('music_volume', 0.8)
        sfx_volume = audio_settings.get('sfx_volume', 0.9)
        
        print(f"🎵 Aplicando volumes: Master={master_volume}, Música={music_volume}, SFX={sfx_volume}")
    
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
            
            ButtonManager.handle_button_click(all_buttons, event)
                    
    def update(self):
        all_buttons = []
        for minus_btn, label_btn, plus_btn in self.volume_controls:
            all_buttons.extend([minus_btn, label_btn, plus_btn])
        all_buttons.extend(self.action_buttons)
        
        ButtonManager.update_buttons(all_buttons, self.game)
            
    def render(self, surface):
        screen_width, screen_height = surface.get_size()
        
        surface.fill(self.game.game_config.get_color('background'))
        
        title_font_size = ResponsiveUI.scale_font_size(48, screen_width, screen_height)
        title_font = self.game.game_config.get_font('title', title_font_size)
        title_text = title_font.render("Configurações de Áudio", True, self.game.game_config.get_color('text'))
        title_rect = title_text.get_rect(center=(screen_width//2, 100))
        surface.blit(title_text, title_rect)
        
        instruction_font_size = ResponsiveUI.scale_font_size(20, screen_width, screen_height)
        instruction_font = self.game.game_config.get_font('menu', instruction_font_size)
        instruction_text = instruction_font.render(
            "Use os botões + e - para ajustar os volumes (10% por clique)", 
            True, self.game.game_config.get_color('text_secondary')
        )
        instruction_rect = instruction_text.get_rect(center=(screen_width//2, 150))
        surface.blit(instruction_text, instruction_rect)
        
        for minus_btn, label_btn, plus_btn in self.volume_controls:
            minus_btn.render(surface, self.game.game_config)
            label_btn.render(surface, self.game.game_config)
            plus_btn.render(surface, self.game.game_config)
        
        for button in self.action_buttons:
            button.render(surface, self.game.game_config)
    
    def enter(self):
        print("Entrando nas configurações de áudio")
        
    def exit(self):
        print("Saindo das configurações de áudio")