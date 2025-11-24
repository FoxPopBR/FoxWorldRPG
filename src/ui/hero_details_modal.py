import pygame
from typing import Dict, Any, List
from src.ui.ui_panel import UIPanel
from src.ui.ui_list import UIList
from src.ui.ui_item_slot import UIItemSlot
from src.ui.button import Button
from src.ui.icon_atlas import IconAtlas
from src.entities.hero import Hero


class HeroDetailsModal:
    """
    Modal com detalhes do herói (Layout 3 Colunas - Refatorado Rodada 6).
    """

    def __init__(self, game, hero: Hero, on_close_callback):
        self.game = game
        self.hero = hero
        self.on_close = on_close_callback

        # Icon Atlas
        self.icon_atlas = IconAtlas(
            "assets/images/icons/icons_Drop_Shadow.png", icon_size=32
        )

        # Dimensões (Tela cheia com margem)
        self.width = int(game.display_config.width * 0.95)
        self.height = int(game.display_config.height * 0.85)
        self.x = (game.display_config.width - self.width) // 2
        self.y = (game.display_config.height - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Painéis (3 Colunas)
        col1_w = int(self.width * 0.25)
        col2_w = int(self.width * 0.40)
        col3_w = int(self.width * 0.35)

        self.col1_rect = pygame.Rect(self.x, self.y, col1_w, self.height)
        self.col2_rect = pygame.Rect(self.x + col1_w, self.y, col2_w, self.height)
        self.col3_rect = pygame.Rect(
            self.x + col1_w + col2_w, self.y, col3_w, self.height
        )

        # Assets de Painel
        self.panel_bg = UIPanel(
            "assets/images/Box/box_menu_grande_retangulo_horizontal_ferro.png.png",
            corner_size=55,  # Margem para respeitar moldura grossa
        )

        # Botão Fechar
        self.close_btn = Button(
            self.col3_rect.right - 70,
            self.col3_rect.top + 40,
            30,
            30,
            "X",
            action=self.close,
        )

        # === Componentes ===

        # Coluna 2: Equipamento + Inventário
        self.slots: Dict[str, UIItemSlot] = {}
        self._init_slots()

        # Carrega silhueta
        self.body_silhouette = None
        try:
            self.body_silhouette = pygame.image.load(
                "assets/images/classes/barbaro_body.png"
            ).convert_alpha()
            # Escala menor (40% da altura da coluna)
            target_h = int(self.col2_rect.height * 0.40)
            ratio = target_h / self.body_silhouette.get_height()
            target_w = int(self.body_silhouette.get_width() * ratio)
            self.body_silhouette = pygame.transform.scale(
                self.body_silhouette, (target_w, target_h)
            )
        except:
            pass

        # Inventário (Melhorado com fundo e scroll)
        margin_x = 60  # Margem maior para bordas
        inv_h = int(self.col2_rect.height * 0.32)
        inv_y = self.col2_rect.bottom - inv_h - 55
        self.inventory_list = UIList(
            self.col2_rect.x + margin_x,
            inv_y,
            self.col2_rect.width - margin_x * 2,
            inv_h,
        )
        self.inventory_list.render_item_callback = self._render_inventory_item
        self.inventory_list.item_height = 50

        # Coluna 3: Detalhes
        margin_x = 60
        det_h = self.col3_rect.height - 180  # Margem maior (era 140)
        self.details_list = UIList(
            self.col3_rect.x + margin_x,
            self.col3_rect.y + 120,  # Margem maior do topo (era 100)
            self.col3_rect.width - margin_x * 2,
            det_h,
        )
        self.details_list.render_item_callback = self._render_detail_item
        self.details_list.item_height = 45

        # Menu de Contexto
        self.context_menu = None

        # Failsafe: Se stats estiverem zerados (bug de save antigo), cura o herói
        if self.hero.stats.vida_atual <= 0:
            self.hero.stats.vida_atual = self.hero.stats.vida_maxima
        if self.hero.stats.mana_atual <= 0:
            self.hero.stats.mana_atual = self.hero.stats.mana_maxima
        if self.hero.stats.stamina_atual <= 0:
            self.hero.stats.stamina_atual = self.hero.stats.stamina_maxima

        self._refresh_data()

    def _init_slots(self):
        # Layout "Boneco" (Coordenadas relativas ao centro da Coluna 2, parte superior)
        cx = self.col2_rect.centerx
        cy = self.col2_rect.y + int(self.col2_rect.height * 0.28)

        slot_size = 40

        # Ajuste de espaçamento para evitar sobreposição
        # Head (-130) -> Neck (-80) -> Chest (-30) -> Belt (+30) -> Legs (+90) -> Feet (+150)
        # Distância vertical mínima: 50px (slot 40 + 10 margem)

        layout = {
            "head": (cx - slot_size // 2, cy - 140),
            "neck": (cx - slot_size // 2, cy - 90),
            "chest": (cx - slot_size // 2, cy - 40),
            "hands": (cx - 100, cy - 40),  # Alinhado com peito, mais à esquerda
            "belt": (cx - slot_size // 2, cy + 20),
            "legs": (cx - slot_size // 2, cy + 80),
            "feet": (cx - slot_size // 2, cy + 140),
            "ring_l": (cx - 80, cy + 20),  # Alinhado com cinto
            "ring_r": (cx + 80, cy + 20),
            "main_hand": (cx - 150, cy - 10),  # Mais afastado
            "off_hand": (cx + 150, cy - 10),
        }

        for slot_name, (sx, sy) in layout.items():
            slot = UIItemSlot(sx, sy, slot_size, slot_name)
            slot.set_icon_atlas(self.icon_atlas)
            self.slots[slot_name] = slot

    def _refresh_data(self):
        # Atualiza slots
        for slot_name, slot_ui in self.slots.items():
            slot_ui.set_item(self.hero.equipment.get(slot_name))

        # Ordena inventário: equipados primeiro
        # Combina inventário + equipamentos para exibição
        display_items = list(self.hero.inventory)
        for item in self.hero.equipment.values():
            if item:
                display_items.append(item)

        sorted_inv = sorted(
            display_items,
            key=lambda item: (
                0 if self._is_equipped(item) else 1,
                item.get("name", ""),
            ),
        )
        self.inventory_list.set_items(sorted_inv)

        # Garante seleção inicial para navegação via teclado
        if self.inventory_list.items and self.inventory_list.selected_index == -1:
            self.inventory_list.selected_index = 0

        # Atualiza lista de detalhes (TODOS os atributos)
        stats = self.hero.stats

        mapping = [
            ("--- GERAL ---", ""),
            ("Level", str(self.hero.level)),
            ("XP", f"{self.hero.experience}/{self.hero.experience_to_next_level}"),
            ("Ouro", str(self.hero.gold)),
            ("--- OFENSIVO ---", ""),
            ("Dano Físico", f"{stats.dano_fisico_min}-{stats.dano_fisico_max}"),
            ("Dano Mágico", f"{stats.dano_magico_min}-{stats.dano_magico_max}"),
            ("Crítico", f"{stats.chance_critico*100:.1f}%"),
            ("Dano Crítico", f"{stats.dano_critico}%"),
            ("Vel. Ataque", f"{stats.velocidade_ataque:.2f}"),
            ("Precisão", f"{stats.precisao}"),
            ("Penetração Arm.", f"{stats.penetracao_armadura:.1f}"),
            ("Penetração Mág.", f"{stats.penetracao_magica:.1f}"),
            ("--- DEFENSIVO ---", ""),
            ("Defesa Física", f"{stats.defesa_fisica}"),
            ("Defesa Mágica", f"{stats.defesa_magica}"),
            ("Bloqueio", f"{stats.bloqueio*100:.1f}%"),
            ("Esquiva", f"{stats.chance_esquiva*100:.1f}%"),
            ("Res. Fogo", f"{stats.resistencia_fogo}"),
            ("Res. Gelo", f"{stats.resistencia_gelo}"),
            ("Res. Raio", f"{stats.resistencia_eletrico}"),
            ("Res. Veneno", f"{stats.resistencia_veneno}"),
            ("Res. Escuro", f"{stats.resistencia_escuro}"),
            ("Res. Caos", f"{stats.resistencia_caos}"),
            ("--- UTILITÁRIO ---", ""),
            ("Regen. Vida", f"{stats.regeneracao_vida:.1f}/s"),
            ("Regen. Mana", f"{stats.regeneracao_mana:.1f}/s"),
            ("Regen. Stamina", f"{stats.regeneracao_stamina:.1f}/s"),
            ("Vel. Movimento", f"{stats.velocidade_movimento}"),
            ("Sorte", f"{stats.sorte:.1f}"),
            ("Carga", f"{stats.capacidade_carga}"),
        ]
        self.details_list.set_items(mapping)

    def _is_equipped(self, item):
        """Verifica se item está equipado (compara identidade do objeto)"""
        return item in self.hero.equipment.values()

    def _add_point(self, attr):
        if self.hero.attribute_points > 0:
            current = getattr(self.hero.stats, attr)
            setattr(self.hero.stats, attr, current + 1)
            self.hero.attribute_points -= 1
            self.hero._calculate_derived_stats()
            self._refresh_data()

    def _render_inventory_item(self, surface, item, rect, is_hovered, is_selected):
        if is_hovered:
            pygame.draw.rect(surface, (80, 80, 80, 100), rect)

        # Ícone
        icon_rect = pygame.Rect(rect.x + 8, rect.y + 5, 40, 40)

        # Tenta desenhar ícone do atlas
        if "icon_coords" in item:
            row, col = item["icon_coords"]
            try:
                icon = self.icon_atlas.get_scaled_icon(row, col, 40)
                surface.blit(icon, icon_rect)
            except:
                pygame.draw.rect(surface, (100, 100, 100), icon_rect)
        else:
            pygame.draw.rect(surface, (100, 100, 100), icon_rect)

        pygame.draw.rect(surface, (200, 200, 200), icon_rect, 1)

        is_equipped = self._is_equipped(item)

        font = self.game.ui_scaler.get_themed_font("menu_small")
        font_desc = self.game.ui_scaler.get_themed_font("text")

        # Cor DOURADA para itens equipados
        color = (255, 215, 0) if is_equipped else (255, 255, 255)
        prefix = "[E] " if is_equipped else ""

        # Nome
        name_surf = font.render(f"{prefix}{item['name']}", True, color)
        surface.blit(name_surf, (rect.x + 55, rect.y + 5))

        # Descrição (Simples)
        # Descrição (Simples)
        if "description" in item:
            desc_color = (255, 215, 0) if is_equipped else (180, 180, 180)
            desc_surf = font_desc.render(item["description"], True, desc_color)
            surface.blit(desc_surf, (rect.x + 55, rect.y + 25))

        # Qtd
        if item.get("stackable", False):
            qty_surf = font.render(f"x{item.get('quantity', 1)}", True, (200, 200, 200))
            surface.blit(
                qty_surf, (rect.right - 45, rect.centery - qty_surf.get_height() // 2)
            )

        # Linha separadora entre itens
        pygame.draw.line(
            surface,
            (80, 80, 80),
            (rect.x + 5, rect.bottom - 1),
            (rect.right - 5, rect.bottom - 1),
        )

    def _render_detail_item(self, surface, item, rect, is_hovered, is_selected):
        key, val = item

        # Se for separador
        if key.startswith("---"):
            font = self.game.ui_scaler.get_themed_font("menu")
            surf = font.render(key, True, (255, 200, 50))
            surface.blit(surf, (rect.centerx - surf.get_width() // 2, rect.y + 10))
            return

        if is_hovered:
            pygame.draw.rect(surface, (40, 40, 40), rect)

        font = self.game.ui_scaler.get_themed_font("menu")

        key_surf = font.render(str(key), True, (200, 200, 200))
        val_surf = font.render(str(val), True, (255, 255, 255))

        surface.blit(key_surf, (rect.x + 10, rect.y + 5))
        surface.blit(val_surf, (rect.right - 10 - val_surf.get_width(), rect.y + 5))

        pygame.draw.line(
            surface,
            (60, 60, 60),
            (rect.x, rect.bottom - 1),
            (rect.right, rect.bottom - 1),
        )

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.close_btn.update(mouse_pos)
        self.inventory_list.update(mouse_pos)
        self.details_list.update(mouse_pos)

        for slot in self.slots.values():
            slot.update(mouse_pos)

    def draw(self, surface):
        # Desenha 3 Painéis
        self.panel_bg.draw(surface, self.col1_rect)
        self.panel_bg.draw(surface, self.col2_rect)
        self.panel_bg.draw(surface, self.col3_rect)

        self.close_btn.render(surface)

        # Coluna 1: Atributos
        self._draw_col1(surface)

        # Coluna 2: Equipamento
        self._draw_col2(surface)

        # Coluna 3: Detalhes
        self._draw_col3(surface)

    def _draw_col1(self, surface):
        font_title = self.game.ui_scaler.get_themed_font("title")
        font_text = self.game.ui_scaler.get_themed_font("menu")
        font_small = self.game.ui_scaler.get_themed_font("menu_small")

        # Margem interna (respeitando moldura)
        # Centralizando o bloco de atributos
        # Largura estimada do bloco (Texto + Espaço + Botão) ~ 150px
        block_w = 150
        mx = self.col1_rect.centerx - block_w // 2
        my = self.col1_rect.y + 50

        title = font_title.render("ATRIBUTOS", True, (255, 255, 255))
        surface.blit(title, (self.col1_rect.centerx - title.get_width() // 2, my))
        my += 50

        # Pontos Disponíveis
        pts_color = (255, 255, 0) if self.hero.attribute_points > 0 else (150, 150, 150)
        pts_surf = font_text.render(
            f"Pontos: {self.hero.attribute_points}", True, pts_color
        )
        surface.blit(pts_surf, (self.col1_rect.centerx - pts_surf.get_width() // 2, my))
        my += 45

        # Lista de Atributos Base
        attrs = ["forca", "destreza", "vitalidade", "inteligencia", "mana", "stamina"]

        for attr in attrs:
            val = getattr(self.hero.stats, attr)
            txt = f"{attr[:3].upper()}: {val}"
            surf = font_text.render(txt, True, (255, 255, 255))

            # Centralização Perfeita
            # Texto alinhado à direita do centro (-10px)
            # Botão alinhado à esquerda do centro (+10px)
            center_x = self.col1_rect.centerx

            # Texto
            surface.blit(surf, (center_x - surf.get_width() - 15, my + 5))

            # Botão +
            btn_rect = pygame.Rect(center_x + 5, my, 35, 35)

            # Cor do botão baseada em pontos disponíveis
            btn_color = (
                (60, 180, 60) if self.hero.attribute_points > 0 else (60, 60, 60)
            )

            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(surface, (200, 200, 200), btn_rect, 2, border_radius=5)

            plus = font_text.render("+", True, (255, 255, 255))
            surface.blit(
                plus,
                (
                    btn_rect.centerx - plus.get_width() // 2,
                    btn_rect.centery - plus.get_height() // 2,
                ),
            )

            my += 48

        # Barras de Status (HP/MP/ST) - MAIS GROSSAS
        # Reset mx para margem padrão das barras
        mx = self.col1_rect.x + 55
        my += 25
        pygame.draw.line(
            surface, (100, 100, 100), (mx, my), (self.col1_rect.right - 55, my)
        )
        my += 25

        stats = self.hero.stats
        bar_w = self.col1_rect.width - 110
        bar_h = 28  # Barras mais grossas!

        def draw_bar(val, max_val, color, label):
            nonlocal my
            pct = max(0, min(1, val / max(1, max_val)))

            # Fundo da barra
            pygame.draw.rect(surface, (30, 30, 30), (mx, my, bar_w, bar_h))
            # Preenchimento
            pygame.draw.rect(surface, color, (mx, my, int(bar_w * pct), bar_h))
            # Borda
            pygame.draw.rect(surface, (200, 200, 200), (mx, my, bar_w, bar_h), 2)

            # Texto dentro da barra (fonte menor para caber)
            txt = font_small.render(
                f"{label}: {int(val)}/{int(max_val)}", True, (255, 255, 255)
            )
            surface.blit(txt, (mx + 8, my + 5))
            my += 38

        draw_bar(stats.vida_atual, stats.vida_maxima, (220, 50, 50), "HP")
        draw_bar(stats.mana_atual, stats.mana_maxima, (50, 50, 220), "MP")
        draw_bar(stats.stamina_atual, stats.stamina_maxima, (50, 220, 50), "ST")

        # Level Display (Acima da XP Bar)
        my += 10
        level_surf = font_text.render(f"Level: {self.hero.level}", True, (220, 220, 50))
        surface.blit(
            level_surf, (self.col1_rect.centerx - level_surf.get_width() // 2, my)
        )
        my += 30

        # XP Bar (mais fina)
        xp_pct = self.hero.experience / max(1, self.hero.experience_to_next_level)
        pygame.draw.rect(surface, (30, 30, 30), (mx, my, bar_w, 12))
        pygame.draw.rect(surface, (220, 220, 50), (mx, my, int(bar_w * xp_pct), 12))
        pygame.draw.rect(surface, (150, 150, 150), (mx, my, bar_w, 12), 1)

        xp_txt = font_small.render(
            f"XP: {self.hero.experience}/{self.hero.experience_to_next_level}",
            True,
            (200, 200, 200),
        )
        surface.blit(xp_txt, (mx, my + 15))

        # Gold
        my += 32
        gold_txt = font_text.render(f"Ouro: {self.hero.gold}", True, (255, 215, 0))
        surface.blit(gold_txt, (self.col1_rect.right - 55 - gold_txt.get_width(), my))

    def _draw_col2(self, surface):
        font_title = self.game.ui_scaler.get_themed_font("title")
        title = font_title.render("EQUIPAMENTO", True, (255, 255, 255))
        surface.blit(
            title,
            (self.col2_rect.centerx - title.get_width() // 2, self.col2_rect.y + 50),
        )

        # Silhueta
        if self.body_silhouette:
            bx = self.col2_rect.centerx - self.body_silhouette.get_width() // 2
            by = (
                self.col2_rect.y
                + int(self.col2_rect.height * 0.28)
                - self.body_silhouette.get_height() // 2
            )
            surface.blit(self.body_silhouette, (bx, by))

        # Slots
        for slot in self.slots.values():
            slot.draw(surface)

        # Inventário com fundo semi-transparente
        inv_bg = pygame.Surface(
            (self.inventory_list.rect.width, self.inventory_list.rect.height),
            pygame.SRCALPHA,
        )
        inv_bg.fill((255, 255, 255, 25))  # Branco com 10% de transparência
        surface.blit(inv_bg, (self.inventory_list.rect.x, self.inventory_list.rect.y))

        # Título do inventário (MAIOR e melhor posicionado)
        inv_title = self.game.ui_scaler.get_themed_font("menu").render(
            "INVENTÁRIO", True, (255, 215, 0)
        )
        title_x = self.inventory_list.rect.centerx - inv_title.get_width() // 2
        surface.blit(key_surf, (rect.x + 10, rect.y + 5))
        surface.blit(val_surf, (rect.right - 10 - val_surf.get_width(), rect.y + 5))

        pygame.draw.line(
            surface,
            (60, 60, 60),
            (rect.x, rect.bottom - 1),
            (rect.right, rect.bottom - 1),
        )

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.close_btn.update(mouse_pos)
        self.inventory_list.update(mouse_pos)
        self.details_list.update(mouse_pos)

        for slot in self.slots.values():
            slot.update(mouse_pos)

    def draw(self, surface):
        # Desenha 3 Painéis
        self.panel_bg.draw(surface, self.col1_rect)
        self.panel_bg.draw(surface, self.col2_rect)
        self.panel_bg.draw(surface, self.col3_rect)

        self.close_btn.render(surface)

        # Coluna 1: Atributos
        self._draw_col1(surface)

        # Coluna 2: Equipamento
        self._draw_col2(surface)

        # Coluna 3: Detalhes
        self._draw_col3(surface)

        # Menu de Contexto (por cima de tudo)
        if self.context_menu:
            pygame.draw.rect(
                surface, (40, 40, 40), self.context_menu["rect"], border_radius=5
            )
            pygame.draw.rect(
                surface, (200, 200, 200), self.context_menu["rect"], 1, border_radius=5
            )

            font = self.game.ui_scaler.get_themed_font("menu_small")
            my = self.context_menu["rect"].y + 5
            mx = self.context_menu["rect"].x + 10

            for opt in self.context_menu["options"]:
                # Highlight hover
                opt_rect = pygame.Rect(self.context_menu["rect"].x, my, 120, 30)
                if opt_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(surface, (60, 60, 60), opt_rect)

                surf = font.render(opt["label"], True, (255, 255, 255))
                surface.blit(surf, (mx, my + 5))
                my += 30

    def _draw_col1(self, surface):
        font_title = self.game.ui_scaler.get_themed_font("title")
        font_text = self.game.ui_scaler.get_themed_font("menu")
        font_small = self.game.ui_scaler.get_themed_font("menu_small")

        # Margem interna (respeitando moldura)
        # Centralizando o bloco de atributos
        # Largura estimada do bloco (Texto + Espaço + Botão) ~ 150px
        block_w = 150
        mx = self.col1_rect.centerx - block_w // 2
        my = self.col1_rect.y + 50

        title = font_title.render("ATRIBUTOS", True, (255, 255, 255))
        surface.blit(title, (self.col1_rect.centerx - title.get_width() // 2, my))
        my += 50

        # Pontos Disponíveis
        pts_color = (255, 255, 0) if self.hero.attribute_points > 0 else (150, 150, 150)
        pts_surf = font_text.render(
            f"Pontos: {self.hero.attribute_points}", True, pts_color
        )
        surface.blit(pts_surf, (self.col1_rect.centerx - pts_surf.get_width() // 2, my))
        my += 45

        # Lista de Atributos Base
        attrs = ["forca", "destreza", "vitalidade", "inteligencia", "mana", "stamina"]

        for attr in attrs:
            val = getattr(self.hero.stats, attr)
            txt = f"{attr[:3].upper()}: {val}"
            surf = font_text.render(txt, True, (255, 255, 255))

            # Centralização Perfeita
            # Texto alinhado à direita do centro (-10px)
            # Botão alinhado à esquerda do centro (+10px)
            center_x = self.col1_rect.centerx

            # Texto
            surface.blit(surf, (center_x - surf.get_width() - 15, my + 5))

            # Botão +
            btn_rect = pygame.Rect(center_x + 5, my, 35, 35)

            # Cor do botão baseada em pontos disponíveis
            btn_color = (
                (60, 180, 60) if self.hero.attribute_points > 0 else (60, 60, 60)
            )

            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(surface, (200, 200, 200), btn_rect, 2, border_radius=5)

            plus = font_text.render("+", True, (255, 255, 255))
            surface.blit(
                plus,
                (
                    btn_rect.centerx - plus.get_width() // 2,
                    btn_rect.centery - plus.get_height() // 2,
                ),
            )

            my += 48

        # Barras de Status (HP/MP/ST) - MAIS GROSSAS
        # Reset mx para margem padrão das barras
        mx = self.col1_rect.x + 55
        my += 25
        pygame.draw.line(
            surface, (100, 100, 100), (mx, my), (self.col1_rect.right - 55, my)
        )
        my += 25

        stats = self.hero.stats
        bar_w = self.col1_rect.width - 110
        bar_h = 28  # Barras mais grossas!

        def draw_bar(val, max_val, color, label):
            nonlocal my
            pct = max(0, min(1, val / max(1, max_val)))

            # Fundo da barra
            pygame.draw.rect(surface, (30, 30, 30), (mx, my, bar_w, bar_h))
            # Preenchimento
            pygame.draw.rect(surface, color, (mx, my, int(bar_w * pct), bar_h))
            # Borda
            pygame.draw.rect(surface, (200, 200, 200), (mx, my, bar_w, bar_h), 2)

            # Texto dentro da barra (fonte menor para caber)
            txt = font_small.render(
                f"{label}: {int(val)}/{int(max_val)}", True, (255, 255, 255)
            )
            surface.blit(txt, (mx + 8, my + 5))
            my += 38

        draw_bar(stats.vida_atual, stats.vida_maxima, (220, 50, 50), "HP")
        draw_bar(stats.mana_atual, stats.mana_maxima, (50, 50, 220), "MP")
        draw_bar(stats.stamina_atual, stats.stamina_maxima, (50, 220, 50), "ST")

        # Level Display (Acima da XP Bar)
        my += 10
        level_surf = font_text.render(f"Level: {self.hero.level}", True, (220, 220, 50))
        surface.blit(
            level_surf, (self.col1_rect.centerx - level_surf.get_width() // 2, my)
        )
        my += 30

        # XP Bar (mais fina)
        xp_pct = self.hero.experience / max(1, self.hero.experience_to_next_level)
        pygame.draw.rect(surface, (30, 30, 30), (mx, my, bar_w, 12))
        pygame.draw.rect(surface, (220, 220, 50), (mx, my, int(bar_w * xp_pct), 12))
        pygame.draw.rect(surface, (150, 150, 150), (mx, my, bar_w, 12), 1)

        xp_txt = font_small.render(
            f"XP: {self.hero.experience}/{self.hero.experience_to_next_level}",
            True,
            (200, 200, 200),
        )
        surface.blit(xp_txt, (mx, my + 15))

        # Gold
        my += 32
        gold_txt = font_text.render(f"Ouro: {self.hero.gold}", True, (255, 215, 0))
        surface.blit(gold_txt, (self.col1_rect.right - 55 - gold_txt.get_width(), my))

    def _draw_col2(self, surface):
        font_title = self.game.ui_scaler.get_themed_font("title")
        title = font_title.render("EQUIPAMENTO", True, (255, 255, 255))
        surface.blit(
            title,
            (self.col2_rect.centerx - title.get_width() // 2, self.col2_rect.y + 50),
        )

        # Silhueta
        if self.body_silhouette:
            bx = self.col2_rect.centerx - self.body_silhouette.get_width() // 2
            by = (
                self.col2_rect.y
                + int(self.col2_rect.height * 0.28)
                - self.body_silhouette.get_height() // 2
            )
            surface.blit(self.body_silhouette, (bx, by))

        # Slots
        for slot in self.slots.values():
            slot.draw(surface)

        # Inventário com fundo semi-transparente
        inv_bg = pygame.Surface(
            (self.inventory_list.rect.width, self.inventory_list.rect.height),
            pygame.SRCALPHA,
        )
        inv_bg.fill((255, 255, 255, 25))  # Branco com 10% de transparência
        surface.blit(inv_bg, (self.inventory_list.rect.x, self.inventory_list.rect.y))

        # Título do inventário (MAIOR e melhor posicionado)
        inv_title = self.game.ui_scaler.get_themed_font("menu").render(
            "INVENTÁRIO", True, (255, 215, 0)
        )
        title_x = self.inventory_list.rect.centerx - inv_title.get_width() // 2
        title_y = self.inventory_list.rect.y - 35
        surface.blit(inv_title, (title_x, title_y))

        self.inventory_list.draw(surface)

    def _draw_col3(self, surface):
        font_title = self.game.ui_scaler.get_themed_font("title")
        title = font_title.render("DETALHES", True, (255, 255, 255))
        surface.blit(
            title,
            (self.col3_rect.centerx - title.get_width() // 2, self.col3_rect.y + 50),
        )

        self.details_list.draw(surface)

    def handle_event(self, event):
        # 1. Prioridade Absoluta: Menu de Contexto
        if self.context_menu and event.type == pygame.MOUSEBUTTONDOWN:
            if self.context_menu["rect"].collidepoint(event.pos):
                # Clique dentro do menu -> Executa opção
                my = self.context_menu["rect"].y + 5
                for opt in self.context_menu["options"]:
                    opt_rect = pygame.Rect(self.context_menu["rect"].x, my, 120, 30)
                    if opt_rect.collidepoint(event.pos):
                        opt["action"]()
                        self.context_menu = None
                        return True
                    my += 30
            else:
                # Clique fora -> Fecha menu
                self.context_menu = None
            return True

        # 2. Botão Fechar
        if self.close_btn.handle_event(event):
            return True

        # 3. Listas (Só processa se menu não estiver aberto)
        if self.inventory_list.handle_event(event):
            # Verifica se houve clique para abrir menu
            selected_idx = self.inventory_list.selected_index
            if selected_idx != -1 and event.type == pygame.MOUSEBUTTONDOWN:
                # Aceita clique esquerdo (1) ou direito (3)
                if event.button in (1, 3):
                    item = self.inventory_list.items[selected_idx]
                    self._open_context_menu(item, event.pos)
                    return True
            return True

        if self.details_list.handle_event(event):
            return True

        # 4. Botões de Atributos
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hero.attribute_points > 0:
                # Recalcula posições (mesma lógica do draw)
                block_w = 150
                mx = self.col1_rect.centerx - block_w // 2
                my = self.col1_rect.y + 50 + 50 + 45

                attrs = [
                    "forca",
                    "destreza",
                    "vitalidade",
                    "inteligencia",
                    "mana",
                    "stamina",
                ]
                for attr in attrs:
                    center_x = self.col1_rect.centerx
                    btn_rect = pygame.Rect(center_x + 5, my, 35, 35)

                    if btn_rect.collidepoint(event.pos):
                        self._add_point(attr)
                        return True
                    my += 48

        # 5. Teclado
        if event.type == pygame.KEYDOWN:
            if self.context_menu:
                if event.key == pygame.K_ESCAPE:
                    self.context_menu = None
                    return True
            else:
                if event.key == pygame.K_DOWN:
                    if self.inventory_list.items:
                        self.inventory_list.selected_index = min(
                            len(self.inventory_list.items) - 1,
                            self.inventory_list.selected_index + 1,
                        )
                        return True
                elif event.key == pygame.K_UP:
                    if self.inventory_list.items:
                        self.inventory_list.selected_index = max(
                            0, self.inventory_list.selected_index - 1
                        )
                        return True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    idx = self.inventory_list.selected_index
                    if idx != -1 and idx < len(self.inventory_list.items):
                        item = self.inventory_list.items[idx]
                        cx, cy = self.inventory_list.rect.center
                        self._open_context_menu(item, (cx, cy))
                        return True
                elif event.key == pygame.K_ESCAPE:
                    self.close()
                    return True

        return False

    def _open_context_menu(self, item, pos):
        """Abre menu de contexto para o item"""
        options = []

        is_equipped = self._is_equipped(item)

        # Opção Equipar/Desequipar
        if is_equipped:
            options.append(
                {"label": "Desequipar", "action": lambda: self._handle_unequip(item)}
            )
        elif item.get("slot"):  # Só mostra equipar se tiver slot definido
            options.append(
                {"label": "Equipar", "action": lambda: self._handle_equip(item)}
            )

        # Opção Consumir (se for consumível)
        if item.get("type") == "consumable":
            options.append(
                {
                    "label": "Usar",
                    "action": lambda: print(
                        f"Usar {item['name']}"
                    ),  # TODO: Implementar uso
                }
            )

        options.append({"label": "Cancelar", "action": lambda: None})

        self.context_menu = {
            "rect": pygame.Rect(pos[0], pos[1], 120, len(options) * 30 + 10),
            "options": options,
        }

    def _handle_equip(self, item):
        if self.hero.equip_item(item):
            self._refresh_data()

    def _handle_unequip(self, item):
        # Precisa achar o slot onde está equipado
        for slot, equipped_item in self.hero.equipment.items():
            if equipped_item == item:
                if self.hero.unequip_item(slot):
                    self._refresh_data()
                return

    def close(self):
        if self.on_close:
            self.on_close()
