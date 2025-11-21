"""
Estado do Grupo - Exibe informações de todos os heróis do grupo
"""

import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager


class GroupState(BaseState):
    """Estado que exibe todos os heróis do grupo"""

    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.hero = self.game.game_config.hero_manager.get_active_hero()
        self._create_ui()

    def _create_ui(self):
        """Cria a interface do grupo"""
        self.buttons.clear()

        # Botão voltar
        back_btn = Button(100, 980, 200, 60, "VOLTAR (ESC)", self._back_to_game, 24)
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
        ButtonManager.update_buttons(self.buttons, self.game)

    def render(self, surface):
        """Renderiza a tela"""
        screen_width, screen_height = surface.get_size()

        # Fundo
        surface.fill(self.game.game_config.get_color("background"))

        # Título
        title_font = self.game.game_config.get_font("title", 60)
        title_text = title_font.render("GRUPO DE HERÓIS", True, (255, 255, 255))
        surface.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 40))

        # Área do grupo
        # Aumentado para 1600 de largura para caber 4 slots de 350px + espaçamento
        group_rect = pygame.Rect(160, 150, 1600, 750)
        pygame.draw.rect(surface, (30, 30, 40), group_rect, border_radius=20)
        pygame.draw.rect(surface, (60, 60, 80), group_rect, 2, border_radius=20)

        # Renderiza boxes dos heróis (estilo Phantasy Star 1)
        # Por enquanto, apenas o herói ativo + 3 slots vazios
        box_width = 350
        box_height = 650
        spacing = 30
        start_x = group_rect.left + 50

        for i in range(4):  # 4 slots de heróis
            box_x = start_x + i * (box_width + spacing)
            box_y = group_rect.top + 50
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

            # Fundo do box
            if i == 0 and self.hero:
                # Herói ativo - destaque
                pygame.draw.rect(surface, (40, 40, 50), box_rect, border_radius=15)
                pygame.draw.rect(
                    surface, (100, 200, 255), box_rect, 3, border_radius=15
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
                empty_font = self.game.game_config.get_font("menu", 24)
                empty_text = empty_font.render("VAZIO", True, (80, 80, 80))
                surface.blit(
                    empty_text,
                    (
                        box_rect.centerx - empty_text.get_width() // 2,
                        box_rect.centery,
                    ),
                )

        # Info de atalho
        info_font = self.game.game_config.get_font("menu", 20)
        info_text = info_font.render(
            "Pressione ESC ou F4 para voltar ao jogo", True, (150, 150, 150)
        )
        surface.blit(
            info_text,
            (screen_width // 2 - info_text.get_width() // 2, screen_height - 60),
        )

        # Renderiza botões
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)

    def _render_hero_box(self, surface, box_rect, hero):
        """Renderiza informações de um herói no box"""
        y_offset = box_rect.top + 20

        # Nome
        name_font = self.game.game_config.get_font("title", 32)
        name_text = name_font.render(hero.name.upper(), True, (255, 255, 255))
        surface.blit(
            name_text, (box_rect.centerx - name_text.get_width() // 2, y_offset)
        )
        y_offset += 40

        # Imagem do Rosto (Face)
        if hero.image_face:
            # Centraliza a imagem (Reduzida para 150x150 para não ocupar tudo)
            face_size = 150
            face_img = pygame.transform.scale(hero.image_face, (face_size, face_size))
            face_x = box_rect.centerx - face_size // 2

            # Moldura da imagem
            pygame.draw.rect(
                surface,
                (20, 20, 30),
                (face_x - 5, y_offset - 5, face_size + 10, face_size + 10),
                border_radius=10,
            )
            pygame.draw.rect(
                surface,
                (100, 100, 150),
                (face_x - 5, y_offset - 5, face_size + 10, face_size + 10),
                2,
                border_radius=10,
            )

            surface.blit(face_img, (face_x, y_offset))
            y_offset += face_size + 20
        else:
            # Placeholder se não tiver imagem
            pygame.draw.rect(
                surface,
                (50, 50, 60),
                (box_rect.centerx - 75, y_offset, 150, 150),
                border_radius=10,
            )
            y_offset += 170

        # Classe
        class_font = self.game.game_config.get_font("menu", 22)
        class_text = class_font.render(
            hero.hero_class.value.upper(), True, (180, 200, 255)
        )
        level_font = self.game.game_config.get_font("menu", 24)
        level_text = level_font.render(f"Nível {hero.level}", True, (220, 220, 220))
        surface.blit(
            level_text, (box_rect.centerx - level_text.get_width() // 2, y_offset)
        )
        y_offset += 50

        # Linha divisória
        pygame.draw.line(
            surface,
            (60, 60, 80),
            (box_rect.left + 20, y_offset),
            (box_rect.right - 20, y_offset),
            2,
        )
        y_offset += 30

        # Definições das barras
        bar_width = box_rect.width - 60
        bar_height = 20
        bar_x = box_rect.left + 30

        # --- HP Section ---
        hp_font = self.game.game_config.get_font("menu", 20)
        hp_text = hp_font.render("HP", True, (255, 100, 100))
        surface.blit(hp_text, (box_rect.left + 30, y_offset))

        hp_value = f"{hero.stats.vida_maxima}"
        hp_value_text = hp_font.render(hp_value, True, (220, 220, 220))
        surface.blit(
            hp_value_text, (box_rect.right - 30 - hp_value_text.get_width(), y_offset)
        )

        y_offset += 25

        # Barra HP (Vermelha)
        pygame.draw.rect(
            surface,
            (50, 50, 60),
            (bar_x, y_offset, bar_width, bar_height),
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            (200, 50, 50),
            (bar_x, y_offset, bar_width, bar_height),  # Assumindo 100% para full health
            border_radius=5,
        )

        y_offset += 35

        # --- MP Section ---
        mp_text = hp_font.render("MP", True, (100, 100, 255))
        surface.blit(mp_text, (box_rect.left + 30, y_offset))

        mp_value = f"{hero.stats.mana_maxima}"
        mp_value_text = hp_font.render(mp_value, True, (220, 220, 220))
        surface.blit(
            mp_value_text, (box_rect.right - 30 - mp_value_text.get_width(), y_offset)
        )

        y_offset += 25

        # Barra MP (Azul)
        pygame.draw.rect(
            surface,
            (50, 50, 60),
            (bar_x, y_offset, bar_width, bar_height),
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            (100, 100, 255),
            (bar_x, y_offset, bar_width, bar_height),  # Assumindo 100% para full mana
            border_radius=5,
        )
        y_offset += 50

        # Linha divisória
        pygame.draw.line(
            surface,
            (60, 60, 80),
            (box_rect.left + 20, y_offset),
            (box_rect.right - 20, y_offset),
            2,
        )
        y_offset += 30

        # Atributos principais
        attr_font = self.game.game_config.get_font("menu", 18)
        attributes = [
            ("FOR", hero.stats.forca),
            ("DES", hero.stats.destreza),
            ("VIT", hero.stats.vitalidade),
            ("INT", hero.stats.inteligencia),
        ]

        for attr_name, attr_value in attributes:
            attr_text = attr_font.render(
                f"{attr_name}: {attr_value}", True, (200, 200, 200)
            )
            surface.blit(attr_text, (box_rect.left + 30, y_offset))
            y_offset += 28
