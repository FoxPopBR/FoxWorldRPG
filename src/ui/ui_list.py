import pygame
from typing import List, Any, Callable


class UIList:
    """
    Lista vertical com rolagem.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.items: List[Any] = []
        self.item_height = 30
        self.scroll_y = 0
        self.max_scroll = 0

        # Callback para renderizar cada item: func(surface, item, rect, is_hovered)
        self.render_item_callback: Callable = None

        # Estado
        self.hovered_index = -1
        self.selected_index = -1

        # Cores
        self.bg_color = (30, 30, 30)
        self.scrollbar_color = (100, 100, 100)
        self.scrollbar_bg = (50, 50, 50)

    def set_items(self, items: List[Any]):
        self.items = items
        self._update_scroll_limits()

    def _update_scroll_limits(self):
        total_height = len(self.items) * self.item_height
        self.max_scroll = max(0, total_height - self.rect.height)
        self.scroll_y = min(self.scroll_y, self.max_scroll)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y -= event.y * 20
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos):
                    # Calcula índice do item sob o mouse
                    relative_y = event.pos[1] - self.rect.y + self.scroll_y
                    index = int(relative_y // self.item_height)
                    if 0 <= index < len(self.items):
                        self.selected_index = index
                        return True
        return False

    def update(self, mouse_pos: tuple):
        if self.rect.collidepoint(mouse_pos):
            # Calcula índice do item sob o mouse
            relative_y = mouse_pos[1] - self.rect.y + self.scroll_y
            index = int(relative_y // self.item_height)
            if 0 <= index < len(self.items):
                self.hovered_index = index
            else:
                self.hovered_index = -1
        else:
            self.hovered_index = -1

    def draw(self, surface: pygame.Surface):
        # Clip para não desenhar fora da área
        clip_rect = self.rect
        original_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        # Desenha fundo
        # pygame.draw.rect(surface, self.bg_color, self.rect)

        # Desenha itens
        start_index = int(self.scroll_y // self.item_height)
        end_index = start_index + int(self.rect.height // self.item_height) + 2
        end_index = min(end_index, len(self.items))

        for i in range(start_index, end_index):
            item = self.items[i]
            item_y = self.rect.y + (i * self.item_height) - self.scroll_y
            item_rect = pygame.Rect(
                self.rect.x, item_y, self.rect.width - 12, self.item_height
            )  # -12 para scrollbar

            is_hovered = i == self.hovered_index
            is_selected = i == self.selected_index

            if self.render_item_callback:
                self.render_item_callback(
                    surface, item, item_rect, is_hovered, is_selected
                )
            else:
                # Render padrão (texto simples)
                color = (255, 255, 255) if not is_hovered else (255, 200, 100)
                # Assume que tem fonte carregada ou usa padrão
                # (Simplificação: desenha retangulo)
                if is_hovered:
                    pygame.draw.rect(surface, (60, 60, 60), item_rect)

        # Restaura clip
        surface.set_clip(original_clip)

        # Desenha Scrollbar
        if self.max_scroll > 0:
            scrollbar_x = self.rect.right - 10
            scrollbar_width = 8

            # Fundo da barra
            pygame.draw.rect(
                surface,
                self.scrollbar_bg,
                (scrollbar_x, self.rect.y, scrollbar_width, self.rect.height),
            )

            # Thumb
            view_ratio = self.rect.height / (len(self.items) * self.item_height)
            thumb_height = max(20, self.rect.height * view_ratio)
            scroll_ratio = self.scroll_y / self.max_scroll
            thumb_y = self.rect.y + (self.rect.height - thumb_height) * scroll_ratio

            pygame.draw.rect(
                surface,
                self.scrollbar_color,
                (scrollbar_x, thumb_y, scrollbar_width, thumb_height),
            )
