import pygame
from typing import Tuple, Optional
from src.ui.responsive_ui import ResponsiveUI


class InventoryUI:
    """Interface de usuário para o inventário"""

    def __init__(self, game):
        self.game = game
        self.scroll_offset = 0
        self.item_height = 50
        self.padding = 10

        # Cores
        self.text_color = (255, 255, 255)
        self.bg_color = (30, 30, 30, 200)
        self.border_color = (100, 100, 100)
        self.highlight_color = (60, 60, 80)

    def render(self, surface: pygame.Surface, rect: pygame.Rect):
        """Renderiza a lista de inventário dentro do rect fornecido"""
        hero = self.game.hero_manager.get_active_hero()
        if not hero:
            return

        # Desenha fundo
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill(self.bg_color)
        surface.blit(s, rect)
        pygame.draw.rect(surface, self.border_color, rect, 2)

        # Título
        font_title = self.game.game_config.get_font("menu", 24)
        title = font_title.render(
            f"Inventário ({len(hero.inventory)} itens)", True, self.text_color
        )
        surface.blit(title, (rect.x + 10, rect.y + 10))

        # Área da lista
        list_rect = pygame.Rect(
            rect.x + 5, rect.y + 40, rect.width - 10, rect.height - 50
        )

        # Clip para rolagem
        old_clip = surface.get_clip()
        surface.set_clip(list_rect)

        y = list_rect.y - self.scroll_offset

        font_item = self.game.game_config.get_font("menu", 20)
        font_desc = self.game.game_config.get_font("menu", 16)

        for item in hero.inventory:
            # Item Row Background
            item_rect = pygame.Rect(list_rect.x, y, list_rect.width, self.item_height)

            # Verifica visibilidade
            if y + self.item_height < list_rect.y or y > list_rect.bottom:
                y += self.item_height + 5
                continue

            # Hover effect (simples, baseado na posição do mouse se necessário, mas aqui é estático por enquanto)
            # pygame.draw.rect(surface, self.highlight_color, item_rect)

            # Ícone
            icon = self.game.game_config.resource_manager.get_item_icon(
                item.get("name", "Item")
            )
            if icon:
                icon = pygame.transform.scale(icon, (32, 32))
                surface.blit(icon, (item_rect.x + 5, item_rect.y + 9))

            # Nome e Quantidade
            name_text = font_item.render(
                f"{item.get('name', 'Unknown')}", True, self.text_color
            )
            qty_text = font_item.render(
                f"x{item.get('quantity', 1)}", True, (200, 200, 100)
            )

            surface.blit(name_text, (item_rect.x + 45, item_rect.y + 5))
            surface.blit(
                qty_text, (item_rect.right - qty_text.get_width() - 10, item_rect.y + 5)
            )

            # Descrição (curta)
            desc = item.get("description", "")
            if len(desc) > 40:
                desc = desc[:37] + "..."
            desc_text = font_desc.render(desc, True, (180, 180, 180))
            surface.blit(desc_text, (item_rect.x + 45, item_rect.y + 28))

            # Divisor
            pygame.draw.line(
                surface,
                (60, 60, 60),
                (item_rect.x, item_rect.bottom - 1),
                (item_rect.right, item_rect.bottom - 1),
            )

            y += self.item_height + 5

        surface.set_clip(old_clip)

    def handle_event(self, event):
        """Gerencia rolagem"""
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 20
            self.scroll_offset = max(0, self.scroll_offset)
            # TODO: Limitar scroll máximo baseado no número de itens
