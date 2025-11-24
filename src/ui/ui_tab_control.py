import pygame
from typing import List, Callable


class UITabControl:
    """
    Controle de abas horizontal.
    """

    def __init__(self, x: int, y: int, width: int, height: int, tabs: List[str]):
        self.rect = pygame.Rect(x, y, width, height)
        self.tabs = tabs
        self.active_tab_index = 0
        self.on_tab_change: Callable[[int], None] = None

        # Layout
        self.tab_width = width // len(tabs)
        self.tab_height = height

        # Cores
        self.active_color = (60, 60, 60)
        self.inactive_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.hover_color = (50, 50, 50)

        self.hovered_index = -1

        # Fonte (será setada externamente ou padrão)
        self.font = None

    def set_font(self, font: pygame.font.Font):
        self.font = font

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos):
                    relative_x = mouse_pos[0] - self.rect.x
                    index = int(relative_x // self.tab_width)
                    if 0 <= index < len(self.tabs):
                        self.active_tab_index = index
                        if self.on_tab_change:
                            self.on_tab_change(index)
                        return True
        return False

    def update(self, mouse_pos: tuple):
        if self.rect.collidepoint(mouse_pos):
            relative_x = mouse_pos[0] - self.rect.x
            self.hovered_index = int(relative_x // self.tab_width)
        else:
            self.hovered_index = -1

    def draw(self, surface: pygame.Surface):
        for i, tab_name in enumerate(self.tabs):
            tab_x = self.rect.x + (i * self.tab_width)
            tab_rect = pygame.Rect(tab_x, self.rect.y, self.tab_width, self.tab_height)

            # Cor de fundo
            if i == self.active_tab_index:
                color = self.active_color
            elif i == self.hovered_index:
                color = self.hover_color
            else:
                color = self.inactive_color

            pygame.draw.rect(surface, color, tab_rect)
            pygame.draw.rect(surface, (100, 100, 100), tab_rect, 1)  # Borda

            # Texto
            if self.font:
                text_surf = self.font.render(tab_name, True, self.text_color)
                text_rect = text_surf.get_rect(center=tab_rect.center)
                surface.blit(text_surf, text_rect)
