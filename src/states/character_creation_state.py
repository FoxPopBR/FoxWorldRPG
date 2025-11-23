# src/states/character_creation_state.py
import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager
from src.entities.hero import HeroClass


class CharacterCreationState(BaseState):
    """Tela de criação de personagem - LAYOUT RELATIVO (Porcentagem)"""

    def __init__(self, game, slot_id=1):
        super().__init__(game)
        self.slot_id = slot_id

        # Inicializa serviços
        from src.services.character_creation_service import CharacterCreationService

        self.creation_service = CharacterCreationService(self.game.game_config.database)

        # Dados do personagem
        self.player_name = ""
        self.selected_class = None
        self.available_points = 10
        self.name_input_active = True

        # Atributos base
        self.base_attributes = {
            "forca": 5,
            "destreza": 5,
            "vitalidade": 5,
            "inteligencia": 5,
            "armadura": 5,
            "energia": 5,
            "mana": 5,
            "stamina": 5,
        }

        # Carrega classes do banco de dados
        self.classes = {}
        self._load_classes_from_database()

        # Controle de scroll para estatísticas
        self.stats_scroll_offset = 0
        self.max_stats_scroll = 0

        # Cache de imagens carregadas
        self.class_images = {}
        self._load_class_images()

        # LAYOUT CONFIG (Porcentagens)
        self.base_w = self.theme.BASE_WIDTH
        self.base_h = self.theme.BASE_HEIGHT

        # Colunas (Total ~94% largura + espaçamentos)
        self.col1_pct = 0.22  # Visualização
        self.col2_pct = 0.22  # Atributos
        self.col3_pct = 0.26  # Habilidades
        self.col4_pct = 0.24  # Stats
        self.spacing_pct = 0.015  # 1.5% espaçamento

        # Alturas
        self.panel_top_pct = 0.12  # Começa em 12% do topo
        self.panel_height_pct = 0.60  # 60% da altura da tela

        self.buttons = []
        self.class_buttons = []
        self.attribute_controls = []
        self._create_ui()

    def _load_classes_from_database(self):
        """Carrega as classes do banco de dados"""
        try:
            available_classes = self.creation_service.get_available_classes()

            if not available_classes:
                raise Exception("Nenhuma classe encontrada no banco de dados")

            for class_data in available_classes:
                class_key = class_data["class_key"]
                self.classes[class_key] = self.creation_service.get_class_display_info(
                    class_key
                )

            if self.classes:
                self.selected_class = list(self.classes.keys())[0]

            print(f"✅ Classes carregadas do banco: {len(self.classes)}")

        except Exception as e:
            print(f"❌ Erro crítico ao carregar classes do banco: {e}")
            raise

    def _load_class_images(self):
        """Carrega as imagens das classes"""
        for class_key in self.classes.keys():
            try:
                image = self.game.game_config.resource_manager.get_hero_image(
                    class_key, "class"
                )

                if image:
                    image = pygame.transform.scale(image, (100, 100))
                    self.class_images[class_key] = image
                else:
                    self.class_images[class_key] = (
                        self.game.game_config.resource_manager._create_placeholder(
                            100, 100, (100, 100, 100), text=class_key[:3]
                        )
                    )
            except Exception as e:
                print(f"❌ Erro ao carregar imagem da classe {class_key}: {e}")
                self.class_images[class_key] = pygame.Surface((100, 100))

    def _create_ui(self):
        """Cria interface com layout relativo"""
        self.buttons.clear()
        self.class_buttons.clear()
        self.attribute_controls.clear()

        # Botões de ação (Rodapé - 92% da altura)
        button_y = int(self.base_h * 0.92)
        btn_width = 200
        btn_height = 50

        cancel_btn = Button(
            int(self.base_w * 0.05),  # 5% da esquerda
            button_y,
            btn_width,
            btn_height,
            "CANCELAR",
            self._cancel_creation,
            font_size=self.theme.FONT_MENU_MEDIUM,
        )

        confirm_btn = Button(
            int(self.base_w * 0.95) - btn_width,  # 5% da direita
            button_y,
            btn_width,
            btn_height,
            "CONFIRMAR",
            self._confirm_character,
            font_size=self.theme.FONT_MENU_MEDIUM,
        )
        self.buttons.extend([cancel_btn, confirm_btn])

        self._create_class_buttons()
        self._create_attribute_controls()

    def _create_class_buttons(self):
        """Cria botões de classe centralizados abaixo dos painéis"""
        total_classes = len(self.classes)

        # Área dos botões de classe (entre painéis e botões de ação)
        # Começa logo após o fim dos painéis (12% + 60% = 72%)
        start_y_pct = 0.74

        # Dimensões relativas
        btn_w = 140
        btn_h = 140
        spacing = 20

        total_width = (btn_w * total_classes) + (spacing * (total_classes - 1))
        start_x = (self.base_w - total_width) // 2
        start_y = int(self.base_h * start_y_pct)

        for i, (class_key, class_data) in enumerate(self.classes.items()):
            x_pos = start_x + i * (btn_w + spacing)

            class_btn = Button(
                x_pos,
                start_y,
                btn_w,
                btn_h,
                "",
                lambda c=class_key: self._select_class(c),
                font_size=self.theme.FONT_MENU_SMALL,
            )
            self.class_buttons.append(class_btn)

    def _create_attribute_controls(self):
        """Cria controles de atributos no painel 2"""
        # Calcula posição do painel 2
        spacing = int(self.base_w * self.spacing_pct)
        col1_w = int(self.base_w * self.col1_pct)
        panel_x = (
            int(self.base_w * 0.02) + col1_w + spacing
        )  # 2% margem + col1 + spacing
        panel_y = int(self.base_h * self.panel_top_pct)
        panel_w = int(self.base_w * self.col2_pct)

        # Área interna para controles
        # Começa após título e pontos (aprox 25% da altura do painel)
        start_y = panel_y + int(self.base_h * 0.18)
        spacing_y = int(self.base_h * 0.055)  # 5.5% da altura da tela por linha

        attributes = [
            ("forca", "FORÇA"),
            ("destreza", "DESTREZA"),
            ("vitalidade", "VITALIDADE"),
            ("inteligencia", "INTELIGÊNCIA"),
            ("armadura", "ARMADURA"),
            ("mana", "MANA"),
            ("stamina", "STAMINA"),
        ]

        btn_size = 30

        for i, (attr_key, attr_name) in enumerate(attributes):
            y_pos = start_y + i * spacing_y

            # Botões alinhados à direita do painel
            # Menos
            minus_x = panel_x + panel_w - (btn_size * 2) - 60
            minus_btn = Button(
                minus_x,
                y_pos,
                btn_size,
                btn_size,
                "-",
                lambda a=attr_key: self._adjust_attribute(a, -1),
                font_size=self.theme.FONT_HUD_MEDIUM,
            )

            # Mais
            plus_x = panel_x + panel_w - btn_size - 20
            plus_btn = Button(
                plus_x,
                y_pos,
                btn_size,
                btn_size,
                "+",
                lambda a=attr_key: self._adjust_attribute(a, 1),
                font_size=self.theme.FONT_HUD_MEDIUM,
            )

            self.attribute_controls.append(
                {
                    "key": attr_key,
                    "name": attr_name,
                    "y": y_pos,  # Y absoluto calculado
                    "minus_btn": minus_btn,
                    "plus_btn": plus_btn,
                }
            )

    def _select_class(self, class_key):
        self.selected_class = class_key

    def _adjust_attribute(self, attribute, change):
        current_value = self.base_attributes[attribute]
        if change > 0 and self.available_points > 0 and current_value < 15:
            self.base_attributes[attribute] += change
            self.available_points -= change
        elif change < 0 and current_value > 3:
            self.base_attributes[attribute] += change
            self.available_points -= change

    def _cancel_creation(self):
        from src.states.menu_state import MenuState

        self.game.state_manager.change_state(MenuState(self.game))

    def _confirm_character(self):
        if not self.player_name.strip():
            self.game.notification_manager.add_notification(
                "Digite um nome!", (255, 100, 100)
            )
            self.name_input_active = True
            return

        if not self.selected_class:
            self.game.notification_manager.add_notification(
                "Selecione uma classe!", (255, 100, 100)
            )
            return

        try:
            game_slot_id = self.slot_id
            cursor = self.game.game_config.database.connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM save_slots WHERE game_slot_id = ? AND hero_name = ?",
                (game_slot_id, self.player_name),
            )
            if cursor.fetchone()[0] > 0:
                self.game.notification_manager.add_notification(
                    f"Nome '{self.player_name}' já existe!", (255, 100, 100)
                )
                return

            hero_class = HeroClass(self.selected_class)
            hero = self.game.game_config.hero_manager.create_hero(
                self.player_name, hero_class, self.base_attributes
            )

            if hero:
                self._update_game_slot(game_slot_id, hero)
                self._create_save_slots(game_slot_id, hero)
                from src.states.game_state import GameState

                self.game.state_manager.change_state(GameState(self.game))
            else:
                self.game.notification_manager.add_notification(
                    "Falha ao criar personagem!", (255, 100, 100)
                )

        except Exception as e:
            print(f"❌ Erro ao criar personagem: {e}")
            self.game.notification_manager.add_notification(
                "Erro ao criar personagem!", (255, 100, 100)
            )

    def _update_game_slot(self, slot_id, hero):
        cursor = self.game.game_config.database.connection.cursor()
        cursor.execute(
            """UPDATE game_slots SET player_name = ?, player_class = ?, player_level = ?, 
               zone_name = ?, playtime = 0, is_active = 1 WHERE slot_id = ?""",
            (hero.name, hero.hero_class.value, hero.level, "Início", slot_id),
        )
        self.game.game_config.database.connection.commit()

    def _create_save_slots(self, game_slot_id, hero):
        cursor = self.game.game_config.database.connection.cursor()
        # Cria os 3 slots de save com IDs 1, 2, 3
        # Cria os 3 slots de save com IDs 1, 2, 3
        for save_id in [1, 2, 3]:
            slot_type = "auto" if save_id == 1 else "manual"
            save_title = "Auto Save" if save_id == 1 else f"Save Manual {save_id - 1}"

            # Apenas o slot 1 (Auto Save) recebe dados do herói na criação
            if save_id == 1:
                cursor.execute(
                    """INSERT OR REPLACE INTO save_slots 
                       (game_slot_id, save_slot_id, slot_type, save_type, hero_name, hero_level, hero_class, zone_name, save_title)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        game_slot_id,
                        save_id,
                        slot_type,
                        slot_type,
                        hero.name,
                        hero.level,
                        hero.hero_class.value,
                        "Início",
                        save_title,
                    ),
                )
            else:
                # Slots 2 e 3 são criados vazios
                cursor.execute(
                    """INSERT OR REPLACE INTO save_slots 
                       (game_slot_id, save_slot_id, slot_type, save_type, save_title)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        game_slot_id,
                        save_id,
                        slot_type,
                        slot_type,
                        save_title,
                    ),
                )
        self.game.game_config.database.connection.commit()

    def _calculate_final_attributes(self):
        if not self.selected_class or self.selected_class not in self.classes:
            return self.base_attributes.copy()
        class_data = self.classes[self.selected_class]
        return self.creation_service.calculate_derived_attributes(
            self.base_attributes, class_data
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._cancel_creation()
            elif event.key == pygame.K_RETURN:
                self.name_input_active = False
            elif event.key == pygame.K_UP:
                self._scroll_up()
            elif event.key == pygame.K_DOWN:
                self._scroll_down()
            elif event.key == pygame.K_BACKSPACE:
                if self.name_input_active:
                    self.player_name = self.player_name[:-1]
            else:
                if (
                    self.name_input_active
                    and len(self.player_name) < 20
                    and event.unicode.isprintable()
                ):
                    self.player_name += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Input de nome (Recalcular rect para hit test)
            col1_w = int(self.base_w * self.col1_pct)
            panel_x = int(self.base_w * 0.02)
            panel_y = int(self.base_h * self.panel_top_pct)
            panel_h = int(self.base_h * self.panel_height_pct)

            input_y = panel_y + panel_h - int(self.base_h * 0.08)
            input_rect = self.ui_scaler.rect(panel_x + 20, input_y, col1_w - 40, 40)

            if input_rect.collidepoint(event.pos):
                self.name_input_active = True
            else:
                self.name_input_active = False

            all_buttons = self.buttons + self.class_buttons
            for control in self.attribute_controls:
                all_buttons.append(control["minus_btn"])
                all_buttons.append(control["plus_btn"])

            for btn in all_buttons:
                if btn.handle_event(event):
                    return

            if event.button == 4:
                self._scroll_up()
            elif event.button == 5:
                self._scroll_down()

    def _scroll_up(self):
        self.stats_scroll_offset = max(0, self.stats_scroll_offset - 1)

    def _scroll_down(self):
        self.stats_scroll_offset = min(10, self.stats_scroll_offset + 1)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        all_buttons = self.buttons + self.class_buttons
        for control in self.attribute_controls:
            all_buttons.append(control["minus_btn"])
            all_buttons.append(control["plus_btn"])
        for btn in all_buttons:
            btn.update(mouse_pos)

    def render(self, surface):
        surface.fill(self.theme.COLOR_BACKGROUND)

        # Título
        title_font = self.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            "CRIAÇÃO DE PERSONAGEM", True, self.theme.COLOR_TEXT_PRIMARY
        )
        title_y = self.ui_scaler.scale(40, "y")
        surface.blit(
            title_text,
            (surface.get_width() // 2 - title_text.get_width() // 2, title_y),
        )

        # Cálculos de Layout
        margin_x = int(self.base_w * 0.02)
        spacing = int(self.base_w * self.spacing_pct)
        panel_y = int(self.base_h * self.panel_top_pct)
        panel_h = int(self.base_h * self.panel_height_pct)

        # Coluna 1
        col1_x = margin_x
        col1_w = int(self.base_w * self.col1_pct)
        self._render_panel(surface, col1_x, panel_y, col1_w, panel_h, "VISUALIZAÇÃO")
        self._render_visualization_content(surface, col1_x, panel_y, col1_w, panel_h)

        # Coluna 2
        col2_x = col1_x + col1_w + spacing
        col2_w = int(self.base_w * self.col2_pct)
        self._render_panel(surface, col2_x, panel_y, col2_w, panel_h, "ATRIBUTOS")
        self._render_attributes_content(surface, col2_x, panel_y, col2_w, panel_h)

        # Coluna 3
        col3_x = col2_x + col2_w + spacing
        col3_w = int(self.base_w * self.col3_pct)
        self._render_panel(surface, col3_x, panel_y, col3_w, panel_h, "HABILIDADES")
        self._render_skills_content(surface, col3_x, panel_y, col3_w, panel_h)

        # Coluna 4
        col4_x = col3_x + col3_w + spacing
        col4_w = int(self.base_w * self.col4_pct)
        self._render_panel(surface, col4_x, panel_y, col4_w, panel_h, "ESTATÍSTICAS")
        self._render_stats_content(surface, col4_x, panel_y, col4_w, panel_h)

        # Botões
        for btn in self.buttons:
            btn.render(surface)
        self._render_class_buttons(surface)

        # Controles de atributos
        for control in self.attribute_controls:
            control["minus_btn"].render(surface)
            control["plus_btn"].render(surface)

    def _render_panel(self, surface, x, y, w, h, title):
        """Renderiza o fundo e título de um painel"""
        rect = self.ui_scaler.rect(x, y, w, h)
        pygame.draw.rect(surface, (30, 30, 40), rect, border_radius=20)
        pygame.draw.rect(surface, (60, 60, 80), rect, 2, border_radius=20)

        title_font = self.ui_scaler.get_themed_font("title")
        title_surf = title_font.render(title, True, (200, 200, 220))

        # Título centralizado no topo do painel (offset relativo)
        title_y_offset = self.ui_scaler.scale(20, "y")
        surface.blit(
            title_surf,
            (rect.centerx - title_surf.get_width() // 2, rect.y + title_y_offset),
        )

    def _render_visualization_content(self, surface, x, y, w, h):
        """Conteúdo do painel 1"""
        rect = self.ui_scaler.rect(x, y, w, h)

        if not self.selected_class or self.selected_class not in self.classes:
            return
        class_data = self.classes[self.selected_class]

        # Imagem
        img_size = int(min(rect.width, rect.height) * 0.55)
        img_rect = pygame.Rect(0, 0, img_size, img_size)
        img_rect.centerx = rect.centerx
        img_rect.y = rect.y + int(rect.height * 0.15)

        pygame.draw.rect(surface, (20, 20, 25), img_rect, border_radius=15)
        pygame.draw.rect(surface, class_data["color"], img_rect, 3, border_radius=15)

        if self.selected_class in self.class_images:
            img = pygame.transform.scale(
                self.class_images[self.selected_class], (img_size - 10, img_size - 10)
            )
            surface.blit(img, (img_rect.x + 5, img_rect.y + 5))

        # Nome da Classe
        name_font = self.ui_scaler.get_themed_font("title")
        name_surf = name_font.render(class_data["name"], True, class_data["color"])
        surface.blit(
            name_surf, (rect.centerx - name_surf.get_width() // 2, img_rect.bottom + 15)
        )

        # Input de Nome
        input_h = 40
        input_y = rect.bottom - int(rect.height * 0.15)
        input_rect = pygame.Rect(rect.x + 20, input_y, rect.width - 40, input_h)

        label_font = self.ui_scaler.get_themed_font("menu_small")
        label_surf = label_font.render("NOME DO PERSONAGEM:", True, (200, 200, 200))
        surface.blit(label_surf, (input_rect.x, input_rect.y - 25))

        border_col = (100, 200, 255) if self.name_input_active else (80, 80, 100)
        pygame.draw.rect(surface, (20, 20, 25), input_rect, border_radius=8)
        pygame.draw.rect(surface, border_col, input_rect, 2, border_radius=8)

        txt = self.player_name if self.player_name else "Digite o nome..."
        col = (255, 255, 255) if self.player_name else (100, 100, 100)
        txt_surf = label_font.render(txt, True, col)
        surface.blit(
            txt_surf,
            (input_rect.x + 10, input_rect.centery - txt_surf.get_height() // 2),
        )

    def _render_attributes_content(self, surface, x, y, w, h):
        """Conteúdo do painel 2"""
        rect = self.ui_scaler.rect(x, y, w, h)

        # Pontos Disponíveis
        pts_y = rect.y + int(rect.height * 0.10)
        pts_bg_rect = pygame.Rect(rect.x + 20, pts_y, rect.width - 40, 40)

        pygame.draw.rect(surface, (20, 20, 30), pts_bg_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 60, 80), pts_bg_rect, 2, border_radius=8)

        pts_font = self.ui_scaler.get_themed_font("menu")
        col = (100, 255, 100) if self.available_points > 0 else (150, 150, 150)
        pts_surf = pts_font.render(f"PONTOS: {self.available_points}", True, col)
        surface.blit(
            pts_surf,
            (
                pts_bg_rect.centerx - pts_surf.get_width() // 2,
                pts_bg_rect.centery - pts_surf.get_height() // 2,
            ),
        )

        # Renderiza labels e valores dos controles
        for control in self.attribute_controls:
            # Y já está escalado no create_ui, mas precisamos renderizar relativo ao painel se quisermos ser puristas
            # Mas como calculamos absoluto lá, usamos absoluto aqui
            y_pos = self.ui_scaler.scale(control["y"], "y")

            # Nome
            name_font = self.ui_scaler.get_themed_font("menu_small")
            name_surf = name_font.render(control["name"], True, (220, 220, 220))
            surface.blit(name_surf, (rect.x + 20, y_pos + 8))

            # Valor
            val = self.base_attributes[control["key"]]
            val_bg_rect = pygame.Rect(0, 0, 50, 30)
            # Posiciona entre os botões (calculado visualmente)
            val_bg_rect.centerx = control["minus_btn"].rect.right + 30  # Aproximado
            # Melhor: usar a posição dos botões
            btn_right = control["minus_btn"]._get_scaled_rect().right
            btn_left = control["plus_btn"]._get_scaled_rect().left
            val_bg_rect.centerx = (btn_right + btn_left) // 2
            val_bg_rect.centery = control["minus_btn"]._get_scaled_rect().centery

            pygame.draw.rect(surface, (20, 20, 25), val_bg_rect, border_radius=5)

            val_col = (255, 255, 0) if val > 5 else (255, 255, 255)
            val_surf = name_font.render(str(val), True, val_col)
            surface.blit(
                val_surf,
                (
                    val_bg_rect.centerx - val_surf.get_width() // 2,
                    val_bg_rect.centery - val_surf.get_height() // 2,
                ),
            )

    def _render_skills_content(self, surface, x, y, w, h):
        """Conteúdo do painel 3"""
        rect = self.ui_scaler.rect(x, y, w, h)
        if not self.selected_class:
            return

        class_data = self.classes[self.selected_class]
        content_y = rect.y + int(rect.height * 0.12)

        # Descrição
        desc_font = self.ui_scaler.get_themed_font("menu_small")
        words = class_data["description"].split(" ")
        lines = []
        curr_line = []
        max_w = rect.width - 40

        for word in words:
            if desc_font.size(" ".join(curr_line + [word]))[0] <= max_w:
                curr_line.append(word)
            else:
                lines.append(" ".join(curr_line))
                curr_line = [word]
        lines.append(" ".join(curr_line))

        for line in lines:
            surf = desc_font.render(line, True, (200, 200, 200))
            surface.blit(surf, (rect.x + 20, content_y))
            content_y += desc_font.get_linesize()

        content_y += 20

        # Bônus
        title_font = self.ui_scaler.get_themed_font("menu")
        bonus_title = title_font.render("Bônus de Classe:", True, (100, 200, 255))
        surface.blit(bonus_title, (rect.x + 20, content_y))
        content_y += 30

        hero_class = HeroClass(self.selected_class)
        from src.entities.hero import Hero

        temp = Hero("temp", hero_class, self.base_attributes)
        bonuses = temp._get_class_bonus()

        for k, v in bonuses.items():
            sign = "+" if v > 0 else ""
            txt = f"• {k.upper()}: {sign}{v}"
            col = (100, 255, 100) if v > 0 else (255, 100, 100)
            surf = desc_font.render(txt, True, col)
            surface.blit(surf, (rect.x + 30, content_y))
            content_y += 25

    def _render_stats_content(self, surface, x, y, w, h):
        """Conteúdo do painel 4"""
        rect = self.ui_scaler.rect(x, y, w, h)

        scroll_area = pygame.Rect(
            rect.x + 10,
            rect.y + int(rect.height * 0.12),
            rect.width - 20,
            rect.height - int(rect.height * 0.15),
        )
        pygame.draw.rect(surface, (20, 20, 25), scroll_area, border_radius=10)

        final_attrs = self._calculate_final_attributes()

        # Renderiza lista simplificada para caber
        y_off = scroll_area.y + 10
        font = self.ui_scaler.get_themed_font("menu_small")

        stats_to_show = [
            ("Vida", final_attrs["vida_maxima"]),
            ("Mana", final_attrs["mana_maxima"]),
            (
                "Dano Físico",
                f"{final_attrs['dano_fisico_min']}-{final_attrs['dano_fisico_max']}",
            ),
            (
                "Dano Mágico",
                f"{final_attrs['dano_magico_min']}-{final_attrs['dano_magico_max']}",
            ),
            ("Defesa", final_attrs["defesa_fisica"]),
            ("Def. Mágica", final_attrs["defesa_magica"]),
            ("Crítico", f"{final_attrs['chance_critico']}%"),
            ("Esquiva", f"{final_attrs['chance_esquiva']}%"),
        ]

        for label, val in stats_to_show:
            lbl_surf = font.render(label, True, (180, 180, 180))
            val_surf = font.render(str(val), True, (255, 255, 255))

            surface.blit(lbl_surf, (scroll_area.x + 15, y_off))
            surface.blit(
                val_surf, (scroll_area.right - 15 - val_surf.get_width(), y_off)
            )

            pygame.draw.line(
                surface,
                (40, 40, 50),
                (scroll_area.x + 10, y_off + 20),
                (scroll_area.right - 10, y_off + 20),
            )
            y_off += 28

    def _render_class_buttons(self, surface):
        """Renderiza botões de classe"""
        for btn in self.class_buttons:
            btn.render(surface)

            # Desenha imagem da classe sobre o botão
            rect = btn._get_scaled_rect()

            # Encontra qual classe é esse botão (hacky mas funciona pelo index)
            idx = self.class_buttons.index(btn)
            class_key = list(self.classes.keys())[idx]

            if class_key in self.class_images:
                img = self.class_images[class_key]
                # Escala imagem para caber no botão com margem
                target_size = int(min(rect.width, rect.height) * 0.8)
                scaled_img = pygame.transform.scale(img, (target_size, target_size))

                img_x = rect.centerx - scaled_img.get_width() // 2
                img_y = rect.centery - scaled_img.get_height() // 2
                surface.blit(scaled_img, (img_x, img_y))

            # Borda de seleção
            if self.selected_class == class_key:
                pygame.draw.rect(surface, (255, 255, 0), rect, 3, border_radius=8)
