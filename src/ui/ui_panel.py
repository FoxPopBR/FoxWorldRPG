import pygame
from typing import Tuple, Optional


class UIPanel:
    """
    Classe para renderizar painéis de UI com 9-slice scaling.
    Permite redimensionar caixas sem distorcer as bordas.
    """

    def __init__(self, image_path: str, corner_size: int = 16):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.corner_size = corner_size
        self.width = self.original_image.get_width()
        self.height = self.original_image.get_height()

        # Pre-calcula os 9 pedaços (slices)
        w, h = self.width, self.height
        c = corner_size

        # Cantos
        self.top_left = self.original_image.subsurface((0, 0, c, c))
        self.top_right = self.original_image.subsurface((w - c, 0, c, c))
        self.bottom_left = self.original_image.subsurface((0, h - c, c, c))
        self.bottom_right = self.original_image.subsurface((w - c, h - c, c, c))

        # Bordas
        self.top = self.original_image.subsurface((c, 0, w - 2 * c, c))
        self.bottom = self.original_image.subsurface((c, h - c, w - 2 * c, c))
        self.left = self.original_image.subsurface((0, c, c, h - 2 * c))
        self.right = self.original_image.subsurface((w - c, c, c, h - 2 * c))

        # Centro
        self.center = self.original_image.subsurface((c, c, w - 2 * c, h - 2 * c))

    def draw(self, surface: pygame.Surface, rect: pygame.Rect):
        """Desenha o painel redimensionado no rect especificado"""
        x, y, target_w, target_h = rect
        c = self.corner_size

        # Se o tamanho alvo for menor que os cantos, não desenha (ou desenha comprimido)
        if target_w < 2 * c or target_h < 2 * c:
            return

        # 1. Desenha Cantos
        surface.blit(self.top_left, (x, y))
        surface.blit(self.top_right, (x + target_w - c, y))
        surface.blit(self.bottom_left, (x, y + target_h - c))
        surface.blit(self.bottom_right, (x + target_w - c, y + target_h - c))

        # 2. Desenha Bordas (Escaladas)
        # Top & Bottom
        scaled_top = pygame.transform.scale(self.top, (target_w - 2 * c, c))
        scaled_bottom = pygame.transform.scale(self.bottom, (target_w - 2 * c, c))
        surface.blit(scaled_top, (x + c, y))
        surface.blit(scaled_bottom, (x + c, y + target_h - c))

        # Left & Right
        scaled_left = pygame.transform.scale(self.left, (c, target_h - 2 * c))
        scaled_right = pygame.transform.scale(self.right, (c, target_h - 2 * c))
        surface.blit(scaled_left, (x, y + c))
        surface.blit(scaled_right, (x + target_w - c, y + c))

        # 3. Desenha Centro (Escalado)
        scaled_center = pygame.transform.scale(
            self.center, (target_w - 2 * c, target_h - 2 * c)
        )
        surface.blit(scaled_center, (x + c, y + c))
