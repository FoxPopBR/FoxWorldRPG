import pygame
from typing import Optional, Callable
from src.ui.responsive_ui import ResponsiveUI

class Button:
    def __init__(self, base_x: int, base_y: int, base_width: int, base_height: int, 
                 text: str, action: Optional[Callable] = None, base_font_size: int = 32,
                 image_key: str = None):
        # Armazena as posições e tamanhos base (para 1080p)
        self.base_x = base_x
        self.base_y = base_y
        self.base_width = base_width
        self.base_height = base_height
        self.base_font_size = base_font_size
        
        self.text = text
        self.action = action
        self.is_hovered_flag = False
        self.rect = None
        self.image_key = image_key
        self.scale_on_hover = 1.0
        
    def update_rect(self, screen_width: int, screen_height: int):
        """Atualiza o retângulo baseado na resolução atual"""
        self.rect = ResponsiveUI.scale_rect(
            self.base_x, self.base_y, 
            self.base_width, self.base_height,
            screen_width, screen_height
        )
        
    def is_hovered(self) -> bool:
        return self.rect and self.rect.collidepoint(pygame.mouse.get_pos())
    
    def update(self, mouse_pos: tuple, screen_width: int, screen_height: int, game_config):
        """Atualiza o estado do botão"""
        self.update_rect(screen_width, screen_height)
        was_hovered = self.is_hovered_flag
        self.is_hovered_flag = self.rect.collidepoint(mouse_pos) if self.rect else False
        
        # Animação de escala no hover
        scale_setting = game_config.get_animation_setting("button_scale_on_hover", 1.05)
        if self.is_hovered_flag and not was_hovered:
            self.scale_on_hover = scale_setting
        elif not self.is_hovered_flag and was_hovered:
            self.scale_on_hover = 1.0
        
    def click(self):
        if self.action:
            self.action()
            
    def render(self, screen: pygame.Surface, game_config):
        if not self.rect:
            self.update_rect(screen.get_width(), screen.get_height())
            
        # Imagem de fundo do botão
        normal_image = game_config.get_image(self.image_key or "button_normal")
        hover_image = game_config.get_image("button_hover") or normal_image
        
        if normal_image:
            # Usar imagem do tema
            current_image = hover_image if self.is_hovered_flag else normal_image
            
            # Aplicar escala se hover
            if self.scale_on_hover != 1.0:
                scaled_width = int(self.rect.width * self.scale_on_hover)
                scaled_height = int(self.rect.height * self.scale_on_hover)
                scaled_image = pygame.transform.scale(current_image, (scaled_width, scaled_height))
                scaled_rect = scaled_image.get_rect(center=self.rect.center)
                screen.blit(scaled_image, scaled_rect)
            else:
                screen.blit(current_image, self.rect)
        else:
            # Fallback para desenho com cores
            color = game_config.get_color('button_hover') if self.is_hovered_flag else game_config.get_color('button_normal')
            border_radius = game_config.get_ui_setting('border_radius', 8)
            border_width = game_config.get_ui_setting('border_width', 2)
            
            # Aplicar escala se hover
            if self.scale_on_hover != 1.0:
                scaled_rect = self.rect.copy()
                scaled_rect.width = int(self.rect.width * self.scale_on_hover)
                scaled_rect.height = int(self.rect.height * self.scale_on_hover)
                scaled_rect.center = self.rect.center
                
                pygame.draw.rect(screen, color, scaled_rect, border_radius=border_radius)
                pygame.draw.rect(screen, game_config.get_color('ui_border'), scaled_rect, border_width, border_radius=border_radius)
            else:
                pygame.draw.rect(screen, color, self.rect, border_radius=border_radius)
                pygame.draw.rect(screen, game_config.get_color('ui_border'), self.rect, border_width, border_radius=border_radius)
        
        # Texto com fonte escalada
        font_size = ResponsiveUI.scale_font_size(
            self.base_font_size, 
            screen.get_width(), 
            screen.get_height()
        )
        font = game_config.get_font('button', font_size)
        text_surface = font.render(self.text, True, game_config.get_color('text'))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)