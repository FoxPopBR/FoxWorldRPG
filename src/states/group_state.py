"""
Estado do Grupo - Exibe informações de todos os heróis do grupo
"""

import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager
from src.ui.ui_panel import UIPanel
from src.ui.hero_details_modal import HeroDetailsModal


class GroupState(BaseState):
    """Estado que exibe todos os heróis do grupo - LAYOUT RELATIVO"""

    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.hero = self.game.game_config.hero_manager.get_active_hero()

        # UI Assets
        self.card_panel = UIPanel(
            "assets/images/Box/box_menu_medio_retangulo_vertical_ferro.png",
            corner_size=16,
        )

        # Modal
        self.details_modal = None

        self._create_ui()

    def _create_ui(self):
        """Cria a interface do grupo"""
        self.buttons.clear()

        # Botão voltar
        back_btn = Button(
            100,
            980,
            200,
            60,
            "VOLTAR (ESC)",
            self._back_to_game,
            font_size=self.theme.FONT_MENU_MEDIUM,
        )
        self.buttons.append(back_btn)

    def _back_to_game(self):
        """Volta para o GameState"""
        from src.states.game_state import GameState

        self.game.state_manager.change_state(GameState(self.game))

    def _open_details(self, hero):
        """Abre modal de detalhes"""
        self.details_modal = HeroDetailsModal(self.game, hero, self._close_details)

    def _close_details(self):
        """Fecha modal"""
        self.details_modal = None

    def handle_event(self, event):
        """Processa eventos"""
        # Se modal estiver aberto, ele consome eventos
        if self.details_modal:
            if self.details_modal.handle_event(event):
                return
            # Se modal não consumiu, mas está aberto, bloqueia outros inputs?
            # Geralmente sim. Mas vamos permitir ESC fechar o modal
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._close_details()
                return
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F4:
                self._back_to_game()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ButtonManager.handle_button_click(self.buttons, event, self.game):
                return

            # Verifica clique nos cards de herói
            # Recalcula rects (poderia cachear, mas layout é dinâmico)
            self._check_card_click(event.pos)

    def _check_card_click(self, mouse_pos):
        # Lógica de layout duplicada do render... idealmente extrair
        # Mas para simplificar, vamos recalcular aqui
        screen_width = self.game.display_config.width
        screen_height = self.game.display_config.height

        container_x = self.ui_scaler.scale(96, "x")
        container_y = self.ui_scaler.scale(162, "y")
        container_w = self.ui_scaler.scale(1728, "x")
        container_h = self.ui_scaler.scale(756, "y")

        group_rect = pygame.Rect(container_x, container_y, container_w, container_h)

        margin_x = int(container_w * 0.02)
        margin_y = int(container_h * 0.05)
        available_w = container_w - (margin_x * 2)
        available_h = container_h - (margin_y * 2)
        spacing = int(available_w * 0.02)
        slot_w = (available_w - (spacing * 3)) // 4
        slot_h = available_h
        start_x = group_rect.left + margin_x
        start_y = group_rect.top + margin_y

        for i in range(4):
            box_x = start_x + i * (slot_w + spacing)
            box_rect = pygame.Rect(box_x, start_y, slot_w, slot_h)

            if box_rect.collidepoint(mouse_pos):
                if i == 0 and self.hero:  # Por enquanto só herói 1
                    self._open_details(self.hero)

    def update(self):
        """Atualiza o estado"""
        if self.details_modal:
            self.details_modal.update()
            return

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, surface, world_surface=None):
        """Renderiza a tela"""
        surface.fill(self.theme.COLOR_BACKGROUND)

        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Título
        title_font = self.ui_scaler.get_themed_font("title_large")
        title_text = title_font.render(
            "GRUPO DE HERÓIS", True, self.theme.COLOR_TEXT_PRIMARY
        )

        title_y = self.ui_scaler.scale(50, "y")
        surface.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, title_y)
        )

        # Container Principal
        container_x = self.ui_scaler.scale(96, "x")
        container_y = self.ui_scaler.scale(162, "y")
        container_w = self.ui_scaler.scale(1728, "x")
        container_h = self.ui_scaler.scale(756, "y")

        group_rect = pygame.Rect(container_x, container_y, container_w, container_h)

        # Fundo do container (opcional, já que teremos os cards)
        # pygame.draw.rect(surface, self.theme.COLOR_BG_CARD, group_rect, border_radius=20)

        # Renderiza boxes dos heróis
        margin_x = int(container_w * 0.02)
        margin_y = int(container_h * 0.05)
        available_w = container_w - (margin_x * 2)
        available_h = container_h - (margin_y * 2)
        spacing = int(available_w * 0.02)
        slot_w = (available_w - (spacing * 3)) // 4
        slot_h = available_h

        start_x = group_rect.left + margin_x
        start_y = group_rect.top + margin_y

        for i in range(4):  # 4 slots de heróis
            box_x = start_x + i * (slot_w + spacing)
            box_rect = pygame.Rect(box_x, start_y, slot_w, slot_h)

            # Desenha Painel (Card)
            self.card_panel.draw(surface, box_rect)

            # Conteúdo do box
            if i == 0 and self.hero:
                self._render_hero_box(surface, box_rect, self.hero)
            else:
                # Slot vazio
                empty_font = self.ui_scaler.get_themed_font("menu")
                empty_text = empty_font.render(
                    "VAZIO", True, self.theme.COLOR_TEXT_HINT
                )
                surface.blit(
                    empty_text,
                    (
                        box_rect.centerx - empty_text.get_width() // 2,
                        box_rect.centery - empty_text.get_height() // 2,
                    ),
                )

        # Info de atalho (Rodapé)
        info_font = self.ui_scaler.get_themed_font("menu_small")
        info_text = info_font.render(
            "Clique no herói para detalhes | ESC voltar",
            True,
            self.theme.COLOR_TEXT_SECONDARY,
        )
        info_y = screen_height - self.ui_scaler.scale(60, "y")
        surface.blit(
            info_text,
            (screen_width // 2 - info_text.get_width() // 2, info_y),
        )

        # Renderiza botões
        for btn in self.buttons:
            btn.render(surface)

        # Renderiza Modal (se aberto)
        if self.details_modal:
            # Overlay escuro
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            self.details_modal.draw(surface)

    def _render_hero_box(self, surface, box_rect, hero):
        """Renderiza informações de um herói no box (Relativo ao box)"""
        scaler = self.game.ui_scaler

        # Margem superior interna
        y_offset = box_rect.top + int(box_rect.height * 0.05)

        # 1. Nome (Fonte Maior)
        name_font = scaler.get_themed_font("title_large")  # Aumentado
        name_text = name_font.render(
            hero.name.upper(), True, self.theme.COLOR_TEXT_PRIMARY
        )
        # Se nome muito grande, reduz fonte
        if name_text.get_width() > box_rect.width - 20:
            name_font = scaler.get_themed_font("title")
            name_text = name_font.render(
                hero.name.upper(), True, self.theme.COLOR_TEXT_PRIMARY
            )

        surface.blit(
            name_text, (box_rect.centerx - name_text.get_width() // 2, y_offset)
        )
        y_offset += name_text.get_height() + 15

        # 2. Imagem do Rosto (Face)
        face_size = int(box_rect.width * 0.6)  # Aumentado um pouco
        face_x = box_rect.centerx - face_size // 2

        # Moldura Face
        pygame.draw.rect(
            surface,
            (20, 20, 20),
            (face_x - 4, y_offset - 4, face_size + 8, face_size + 8),
        )
        pygame.draw.rect(
            surface,
            (100, 100, 100),
            (face_x - 2, y_offset - 2, face_size + 4, face_size + 4),
            2,
        )

        if hero.image_face:
            face_img = pygame.transform.scale(hero.image_face, (face_size, face_size))
            surface.blit(face_img, (face_x, y_offset))
        else:
            pygame.draw.rect(
                surface, (50, 50, 60), (face_x, y_offset, face_size, face_size)
            )

        y_offset += face_size + 20

        # 3. Classe e Nível (Fonte Média)
        info_font = scaler.get_themed_font("menu")  # Aumentado de menu_small
        class_text = info_font.render(
            f"{hero.hero_class.value.upper()}", True, (200, 200, 255)
        )
        surface.blit(
            class_text, (box_rect.centerx - class_text.get_width() // 2, y_offset)
        )
        y_offset += class_text.get_height() + 5

        lvl_text = info_font.render(
            f"Lvl {hero.level} - XP {hero.experience}/{hero.experience_to_next_level}",
            True,
            (255, 255, 200),
        )
        surface.blit(lvl_text, (box_rect.centerx - lvl_text.get_width() // 2, y_offset))
        y_offset += lvl_text.get_height() + 20

        # 4. Barras de Status (HP, MP, Stamina)
        bar_w = int(box_rect.width * 0.8)
        bar_h = 24  # Barra mais grossa para caber texto
        bar_x = box_rect.centerx - bar_w // 2

        # Fonte para texto dentro da barra
        bar_font = scaler.get_themed_font("text_bold")  # Fonte legível

        # Helper para desenhar barra com texto
        def draw_stat_bar(current, maximum, color_fill, color_bg, label):
            nonlocal y_offset
            pct = max(0, min(1, current / max(1, maximum)))

            # Fundo
            pygame.draw.rect(surface, color_bg, (bar_x, y_offset, bar_w, bar_h))
            # Preenchimento
            pygame.draw.rect(
                surface, color_fill, (bar_x, y_offset, int(bar_w * pct), bar_h)
            )
            # Borda
            pygame.draw.rect(
                surface, (200, 200, 200), (bar_x, y_offset, bar_w, bar_h), 2
            )

            # Texto Centralizado (Ex: "HP: 100/100")
            txt = f"{label}: {int(current)}/{int(maximum)}"
            txt_surf = bar_font.render(txt, True, (255, 255, 255))

            # Sombra do texto para legibilidade
            txt_shadow = bar_font.render(txt, True, (0, 0, 0))
            surface.blit(
                txt_shadow,
                (
                    box_rect.centerx - txt_surf.get_width() // 2 + 1,
                    y_offset + bar_h // 2 - txt_surf.get_height() // 2 + 1,
                ),
            )
            surface.blit(
                txt_surf,
                (
                    box_rect.centerx - txt_surf.get_width() // 2,
                    y_offset + bar_h // 2 - txt_surf.get_height() // 2,
                ),
            )

            y_offset += bar_h + 10

        # HP
        draw_stat_bar(
            hero.stats.vida_atual,
            hero.stats.vida_maxima,
            (180, 40, 40),
            (60, 10, 10),
            "HP",
        )

        # MP
        draw_stat_bar(
            hero.stats.mana_atual,
            hero.stats.mana_maxima,
            (40, 40, 180),
            (10, 10, 60),
            "MP",
        )

        # Stamina
        draw_stat_bar(
            hero.stats.stamina_atual,
            hero.stats.stamina_maxima,
            (40, 180, 40),
            (10, 60, 10),
            "ST",
        )

    def on_resize(self, old_size, new_size):
        """Recria UI ao redimensionar"""
        self._create_ui()
