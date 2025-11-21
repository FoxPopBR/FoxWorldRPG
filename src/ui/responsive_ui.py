import pygame
from typing import Tuple, List, Dict, Any


class ResponsiveUI:
    """Sistema de UI responsiva que se adapta a diferentes resoluções"""

    # Resolução base para design (1080p)
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080

    @classmethod
    def scale_value(cls, value: int, current_width: int, current_height: int) -> int:
        """Escala um valor baseado na resolução atual"""
        # Usa a menor escala para manter proporção, mas baseada na dimensão correta
        scale_x = current_width / cls.BASE_WIDTH
        scale_y = current_height / cls.BASE_HEIGHT
        scale = min(scale_x, scale_y)
        return int(value * scale)

    @classmethod
    def scale_rect(
        cls,
        x: int,
        y: int,
        width: int,
        height: int,
        current_width: int,
        current_height: int,
    ) -> pygame.Rect:
        """Escala um retângulo para a resolução atual"""
        # Para X e Width, usa escala horizontal
        # Para Y e Height, usa escala vertical
        # ISSO É CRUCIAL: Se usarmos min(scale_x, scale_y) para tudo,
        # em telas ultrawide ou 4:3 os elementos vão ficar deslocados.

        scale_x = current_width / cls.BASE_WIDTH
        scale_y = current_height / cls.BASE_HEIGHT

        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        scaled_width = int(width * scale_x)
        scaled_height = int(height * scale_y)

        return pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)

    @classmethod
    def scale_font_size(
        cls, base_size: int, current_width: int, current_height: int
    ) -> int:
        """Escala o tamanho da fonte baseado na resolução"""
        scale_x = current_width / cls.BASE_WIDTH
        scale_y = current_height / cls.BASE_HEIGHT
        scale = min(scale_x, scale_y)
        scaled_size = int(base_size * scale)
        return max(scaled_size, 12)  # Tamanho mínimo de fonte

    @classmethod
    def get_centered_x(cls, width: int, current_width: int) -> int:
        """Retorna a posição X centralizada"""
        return (current_width - width) // 2

    @classmethod
    def get_vertical_position(cls, base_y: int, current_height: int) -> int:
        """Calcula posição vertical escalada"""
        scale_y = current_height / cls.BASE_HEIGHT
        return int(base_y * scale_y)
