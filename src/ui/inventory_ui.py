# src/ui/inventory_ui.py
import pygame
from typing import Tuple, Optional


class InventoryUI:
    """Interface de usuário para o inventário - REFATORADO UIScaler"""

    def __init__(self, game):
        self.game = game
        self.scroll_offset = 0

        # Acesso rápido aos sistemas
        self.theme = game.game_config.theme
        self.ui_scaler = game.ui_scaler

        # Dimensões base (escaladas depois)
        self.item_base_height = 50
        self.padding_base = 10

    def render(self, surface: pygame.Surface, rect: pygame.Rect):
        """Renderiza a lista de inventário dentro do rect fornecido"""
        hero = self.game.game_config.hero_manager.get_active_hero()
        if not hero:
            return

        # Desenha fundo com transparência
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_color = (*self.theme.COLOR_BG_CARD, 200)  # RGB + Alpha
        s.fill(bg_color)
        surface.blit(s, rect)
        pygame.draw.rect(surface, self.theme.COLOR_BORDER_EMPTY, rect, 2)

        # Título
        font_title = self.ui_scaler.get_themed_font("menu")
        title = font_title.render(
            f"Inventário ({len(hero.inventory)} itens)",
            True,
            self.theme.COLOR_TEXT_PRIMARY,
        )
        title_padding = self.ui_scaler.scale(10, "x")
        surface.blit(title, (rect.x + title_padding, rect.y + title_padding))

        # Área da lista
        list_y_offset = self.ui_scaler.scale(40, "y")
        list_padding = self.ui_scaler.scale(5, "x")
        list_rect = pygame.Rect(
            rect.x + list_padding,
            rect.y + list_y_offset,
            rect.width - list_padding * 2,
            rect.height - list_y_offset - self.ui_scaler.scale(10, "y"),
        )

        # Clip para rolagem
        old_clip = surface.get_clip()
        surface.set_clip(list_rect)

        y = list_rect.y - self.scroll_offset
        item_height = self.ui_scaler.scale(self.item_base_height, "y")
        item_spacing = self.ui_scaler.scale(5, "y")

        font_item = self.ui_scaler.get_themed_font("menu_small")
        font_desc = self.ui_scaler.get_themed_font("menu_tiny")

        for item in hero.inventory:
            # Item Row Background
            item_rect = pygame.Rect(list_rect.x, y, list_rect.width, item_height)

            # Verifica visibilidade
            if y + item_height < list_rect.y or y > list_rect.bottom:
                y += item_height + item_spacing
                continue

            # Ícone (se disponível)
            icon = self.game.game_config.resource_manager.get_item_icon(
                item.get("name", "Item")
            )
            icon_size = self.ui_scaler.scale(32, "x")
            icon_padding = self.ui_scaler.scale(5, "x")

            if icon:
                icon = pygame.transform.scale(icon, (icon_size, icon_size))
                icon_y = item_rect.y + (item_height - icon_size) // 2
                surface.blit(icon, (item_rect.x + icon_padding, icon_y))

            # Nome e Quantidade
            text_x_offset = icon_padding + icon_size + self.ui_scaler.scale(8, "x")

            name_text = font_item.render(
                f"{item.get('name', 'Unknown')}", True, self.theme.COLOR_TEXT_PRIMARY
            )
            qty_text = font_item.render(
                f"x{item.get('quantity', 1)}", True, self.theme.COLOR_ACCENT
            )

            name_y = item_rect.y + self.ui_scaler.scale(5, "y")
            surface.blit(name_text, (item_rect.x + text_x_offset, name_y))

            qty_padding = self.ui_scaler.scale(10, "x")
            surface.blit(
                qty_text, (item_rect.right - qty_text.get_width() - qty_padding, name_y)
            )

            # Descrição (curta)
            desc = item.get("description", "")
            max_desc_len = 40
            if len(desc) > max_desc_len:
                desc = desc[: max_desc_len - 3] + "..."

            desc_text = font_desc.render(desc, True, self.theme.COLOR_TEXT_SECONDARY)
            desc_y = name_y + self.ui_scaler.scale(23, "y")
            surface.blit(desc_text, (item_rect.x + text_x_offset, desc_y))

            # Divisor
            pygame.draw.line(
                surface,
                self.theme.COLOR_BORDER_EMPTY,
                (item_rect.x, item_rect.bottom - 1),
                (item_rect.right, item_rect.bottom - 1),
                1,
            )

            y += item_height + item_spacing

        surface.set_clip(old_clip)

    def handle_event(self, event):
        """Gerencia rolagem"""
        if event.type == pygame.MOUSEWHEEL:
            scroll_speed = self.ui_scaler.scale(20, "y")
            self.scroll_offset -= event.y * scroll_speed
            self.scroll_offset = max(0, self.scroll_offset)
            # TODO: Limitar scroll máximo baseado no número de itens
