"""
Estado do Grupo - Exibe informações de todos os heróis do grupo
"""

import pygame

"""
Estado do Grupo - Exibe informações de todos os heróis do grupo
"""

import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager


class GroupState(BaseState):
    """Estado que exibe todos os heróis do grupo - LAYOUT RELATIVO"""

    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.hero = self.game.game_config.hero_manager.get_active_hero()

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

    def handle_event(self, event):
        """Processa eventos"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F4:
                self._back_to_game()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            ButtonManager.handle_button_click(self.buttons, event, self.game)

    def update(self):
        """Atualiza o estado"""
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, surface):
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
        # Base: 1920x1080
        # Margem 5% = 96px
        # Largura 90% = 1728px
        # Altura 70% = 756px
        # Y = 15% = 162px

        container_x = self.ui_scaler.scale(96, "x")
        container_y = self.ui_scaler.scale(162, "y")
        container_w = self.ui_scaler.scale(1728, "x")
        container_h = self.ui_scaler.scale(756, "y")

        group_rect = pygame.Rect(container_x, container_y, container_w, container_h)
        pygame.draw.rect(
            surface, self.theme.COLOR_BG_CARD, group_rect, border_radius=20
        )
        pygame.draw.rect(
            surface, self.theme.COLOR_BORDER_DEFAULT, group_rect, 2, border_radius=20
        )

        # Renderiza boxes dos heróis
        # 4 slots distribuídos igualmente dentro do container
        margin_x = int(container_w * 0.02)
        margin_y = int(container_h * 0.05)

        # Espaço disponível para slots
        available_w = container_w - (margin_x * 2)
        available_h = container_h - (margin_y * 2)

        # Largura de cada slot (4 slots + 3 espaçamentos)
        spacing = int(available_w * 0.02)
        slot_w = (available_w - (spacing * 3)) // 4
        slot_h = available_h

        start_x = group_rect.left + margin_x
        start_y = group_rect.top + margin_y

        for i in range(4):  # 4 slots de heróis
            box_x = start_x + i * (slot_w + spacing)
            box_rect = pygame.Rect(box_x, start_y, slot_w, slot_h)

            # Fundo do box
            if i == 0 and self.hero:
                # Herói ativo - destaque
                pygame.draw.rect(surface, (40, 40, 50), box_rect, border_radius=15)
                pygame.draw.rect(
                    surface, self.theme.COLOR_ACCENT_BLUE, box_rect, 3, border_radius=15
                )
            else:
                # Slot vazio
                pygame.draw.rect(surface, (25, 25, 30), box_rect, border_radius=15)
                pygame.draw.rect(surface, (50, 50, 60), box_rect, 2, border_radius=15)

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
            "Pressione ESC ou F4 para voltar ao jogo",
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

    def _render_hero_box(self, surface, box_rect, hero):
        """Renderiza informações de um herói no box (Relativo ao box)"""
        scaler = self.game.ui_scaler

        y_offset = box_rect.top + int(box_rect.height * 0.05)

        # Nome
        name_font = scaler.get_themed_font("title")
        name_text = name_font.render(
            hero.name.upper(), True, self.theme.COLOR_TEXT_PRIMARY
        )

        # Verifica se cabe
        if name_text.get_width() > box_rect.width - 20:
            name_font = scaler.get_themed_font("menu")  # Reduz fonte
            name_text = name_font.render(
                hero.name.upper(), True, self.theme.COLOR_TEXT_PRIMARY
            )

        surface.blit(
            name_text, (box_rect.centerx - name_text.get_width() // 2, y_offset)
        )
        y_offset += name_text.get_height() + int(box_rect.height * 0.02)

        # Imagem do Rosto (Face)
        # Tamanho relativo: 30% da largura do box
        face_size = int(box_rect.width * 0.4)
        face_x = box_rect.centerx - face_size // 2

        if hero.image_face:
            face_img = pygame.transform.scale(hero.image_face, (face_size, face_size))

            # Moldura
            pygame.draw.rect(
                surface,
                (20, 20, 30),
                (face_x - 2, y_offset - 2, face_size + 4, face_size + 4),
                border_radius=10,
            )
            pygame.draw.rect(
                surface,
                self.theme.COLOR_BORDER_DEFAULT,
                (face_x - 2, y_offset - 2, face_size + 4, face_size + 4),
                2,
                border_radius=10,
            )
            surface.blit(face_img, (face_x, y_offset))
        else:
            pygame.draw.rect(
                surface,
                (50, 50, 60),
                (face_x, y_offset, face_size, face_size),
                border_radius=10,
            )

        y_offset += face_size + int(box_rect.height * 0.03)

        # Classe e Nível
        info_font = scaler.get_themed_font("menu_small")
        class_text = info_font.render(
            hero.hero_class.value.upper(), True, self.theme.COLOR_ACCENT_BLUE
        )
        level_text = info_font.render(
            f"Nível {hero.level}", True, self.theme.COLOR_TEXT_SECONDARY
        )

        surface.blit(
            class_text, (box_rect.centerx - class_text.get_width() // 2, y_offset)
        )
        y_offset += class_text.get_height() + 5
        surface.blit(
            level_text, (box_rect.centerx - level_text.get_width() // 2, y_offset)
        )
        y_offset += level_text.get_height() + int(box_rect.height * 0.03)

        # Barras
        bar_w = int(box_rect.width * 0.8)
        bar_h = int(box_rect.height * 0.03)
        bar_x = box_rect.centerx - bar_w // 2

        # HP
        hp_pct = hero.stats.vida_atual / hero.stats.vida_maxima
        pygame.draw.rect(
            surface, (50, 50, 60), (bar_x, y_offset, bar_w, bar_h), border_radius=4
        )
        pygame.draw.rect(
            surface,
            (200, 50, 50),
            (bar_x, y_offset, int(bar_w * hp_pct), bar_h),
            border_radius=4,
        )

        hp_txt = info_font.render(
            f"HP {hero.stats.vida_atual}/{hero.stats.vida_maxima}",
            True,
            (255, 255, 255),
        )
        surface.blit(
            hp_txt, (box_rect.centerx - hp_txt.get_width() // 2, y_offset - 2)
        )  # Texto sobre a barra

        y_offset += bar_h + 10

        # MP
        mp_pct = hero.stats.mana_atual / hero.stats.mana_maxima
        pygame.draw.rect(
            surface, (50, 50, 60), (bar_x, y_offset, bar_w, bar_h), border_radius=4
        )
        pygame.draw.rect(
            surface,
            (50, 50, 200),
            (bar_x, y_offset, int(bar_w * mp_pct), bar_h),
            border_radius=4,
        )

        mp_txt = info_font.render(
            f"MP {hero.stats.mana_atual}/{hero.stats.mana_maxima}",
            True,
            (255, 255, 255),
        )
        surface.blit(mp_txt, (box_rect.centerx - mp_txt.get_width() // 2, y_offset - 2))

        y_offset += bar_h + int(box_rect.height * 0.05)

        # Atributos
        attr_font = scaler.get_themed_font("menu_small")
        attrs = [
            ("FOR", hero.stats.forca),
            ("DES", hero.stats.destreza),
            ("VIT", hero.stats.vitalidade),
            ("INT", hero.stats.inteligencia),
        ]

        for k, v in attrs:
            txt = attr_font.render(f"{k}: {v}", True, self.theme.COLOR_TEXT_SECONDARY)
            surface.blit(txt, (bar_x, y_offset))
            y_offset += txt.get_height() + 5

    def on_resize(self, old_size, new_size):
        """Recria UI ao redimensionar"""
        self._create_ui()
