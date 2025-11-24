import pygame
from typing import Dict, Any, Optional
from src.ui.ui_panel import UIPanel


class UIItemSlot:
    """
    Componente visual para um slot de item.
    Mostra o ícone do item se equipado, ou vazio.
    """

    def __init__(self, x: int, y: int, size: int = 48, slot_type: str = "generic"):
        self.rect = pygame.Rect(x, y, size, size)
        self.slot_type = slot_type
        self.item: Optional[Dict[str, Any]] = None
        self.is_hovered = False
        self.is_selected = False

        # Carrega assets (placeholder por enquanto)
        # Idealmente, teríamos uma imagem de fundo para o slot
        self.bg_color = (40, 40, 40)
        self.border_color = (100, 100, 100)
        self.hover_color = (150, 150, 150)

        # Cache de ícones carregados
        self.icon_cache = {}

    def set_item(self, item: Optional[Dict[str, Any]]):
        self.item = item

    def set_icon_atlas(self, atlas):
        self.icon_atlas = atlas

    def update(self, mouse_pos: tuple):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface):
        # Desenha fundo
        color = self.hover_color if self.is_hovered else self.border_color
        pygame.draw.rect(surface, color, self.rect, 2)  # Borda
        pygame.draw.rect(
            surface, self.bg_color, self.rect.inflate(-4, -4)
        )  # Fundo interno

        # Desenha ícone do item
        if self.item:
            # Tenta usar Atlas primeiro
            if (
                "icon_coords" in self.item
                and hasattr(self, "icon_atlas")
                and self.icon_atlas
            ):
                row, col = self.item["icon_coords"]
                try:
                    icon = self.icon_atlas.get_scaled_icon(
                        row, col, self.rect.width - 8
                    )
                    icon_rect = icon.get_rect(center=self.rect.center)
                    surface.blit(icon, icon_rect)
                    return
                except:
                    pass

            # Fallback para icon_path (legado)
            if "icon_path" in self.item:
                icon_path = self.item["icon_path"]
                if icon_path not in self.icon_cache:
                    try:
                        img = pygame.image.load(icon_path).convert_alpha()
                        # Escala para caber no slot (com margem)
                        icon_size = self.rect.width - 8
                        img = pygame.transform.scale(img, (icon_size, icon_size))
                        self.icon_cache[icon_path] = img
                    except Exception as e:
                        print(f"Erro ao carregar ícone {icon_path}: {e}")
                        self.icon_cache[icon_path] = None

                icon = self.icon_cache.get(icon_path)
                if icon:
                    # Centraliza
                    icon_rect = icon.get_rect(center=self.rect.center)
                    surface.blit(icon, icon_rect)

        # Se não tem item, poderia desenhar um ícone fantasma do tipo de slot (espada, elmo, etc)
        elif not self.item:
            # TODO: Desenhar placeholder baseado em self.slot_type
            pass
