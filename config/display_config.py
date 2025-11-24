import pygame
from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class DisplayConfig:
    """Configurações de display e vídeo usando banco de dados"""

    # Internal Resolution (World Rendering)
    INTERNAL_RESOLUTION: Tuple[int, int] = (640, 360)

    # Resoluções suportadas - Baseadas em escala de 640x360
    # Cada resolução é um múltiplo inteiro da resolução interna
    SUPPORTED_RESOLUTIONS: Tuple[Tuple[int, int], ...] = (
        (1280, 720),  # 640×360 × 2 (HD 720p)
        (1920, 1080),  # 640×360 × 3 (Full HD 1080p)
        (2560, 1440),  # 640×360 × 4 (QHD 2K)
    )

    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self._load_settings()

    def _load_settings(self):
        """Carrega configurações do banco de dados"""
        video_settings = self.settings_manager.get_video_settings()

        # CORREÇÃO: Garantir que a resolução seja uma tupla
        resolution = video_settings.get("resolution", (1920, 1080))
        if isinstance(resolution, list):
            resolution = tuple(resolution)

        # VALIDAÇÃO: Migrar para resolução suportada se necessário
        if resolution not in self.SUPPORTED_RESOLUTIONS:
            print(f"⚠️ Resolução {resolution} não é mais suportada")
            # Migra para a resolução mais próxima
            old_width = resolution[0]
            if old_width < 1500:  # Menor que 1920/2
                resolution = (1280, 720)
            elif old_width < 2200:  # Menor que 2560/2
                resolution = (1920, 1080)
            else:
                resolution = (2560, 1440)
            print(f"🔄 Migrando para: {resolution}")
            # Salva a nova resolução
            self.settings_manager.set_video_setting("resolution", resolution)

        self.current_resolution = resolution
        self.fullscreen = video_settings.get("fullscreen", False)
        self.vsync = video_settings.get("vsync", True)
        self.fps = video_settings.get("fps", 60)

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
        self.settings_manager.set_video_setting("resolution", self.current_resolution)
        self.settings_manager.set_video_setting("fullscreen", self.fullscreen)
        self.settings_manager.set_video_setting("vsync", self.vsync)
        self.settings_manager.set_video_setting("fps", self.fps)

    def reset_to_default(self):
        """Reseta para configurações padrão"""
        self.current_resolution = (1920, 1080)
        self.fullscreen = False
        self.vsync = True
        self.fps = 60
        self.save_to_file()

    @property
    def width(self) -> int:
        return self.current_resolution[0]

    @property
    def height(self) -> int:
        return self.current_resolution[1]
