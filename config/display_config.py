import pygame
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class DisplayConfig:
    """Configurações de display e vídeo usando banco de dados"""
    
    # Resoluções suportadas
    SUPPORTED_RESOLUTIONS: Tuple[Tuple[int, int], ...] = (
        (800, 600),
        (1024, 768), 
        (1280, 720),
        (1366, 768),
        (1920, 1080)
    )
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self._load_settings()
    
    def _load_settings(self):
        """Carrega configurações do banco de dados"""
        video_settings = self.settings_manager.get_video_settings()
        
        # CORREÇÃO: Garantir que a resolução seja uma tupla
        resolution = video_settings.get('resolution', (1920, 1080))
        if isinstance(resolution, list):
            resolution = tuple(resolution)
        
        self.current_resolution = resolution
        self.fullscreen = video_settings.get('fullscreen', False)
        self.vsync = video_settings.get('vsync', True)
        self.fps = video_settings.get('fps', 60)
    
    def get_display_flags(self) -> int:
        """Retorna as flags do Pygame baseado nas configurações"""
        flags = 0
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        if self.vsync:
            flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
        return flags
    
    def save_to_file(self):
        """Salva configurações no banco de dados"""
        self.settings_manager.set_video_setting('resolution', self.current_resolution)
        self.settings_manager.set_video_setting('fullscreen', self.fullscreen)
        self.settings_manager.set_video_setting('vsync', self.vsync)
        self.settings_manager.set_video_setting('fps', self.fps)
    
    def reset_to_default(self):
        """Reseta para configurações padrão"""
        self.current_resolution = (1920, 1080)
        self.fullscreen = False
        self.vsync = True
        self.fps = 60
        self.save_to_file()