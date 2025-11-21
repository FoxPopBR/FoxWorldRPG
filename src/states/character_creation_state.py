# src/states/character_creation_state.py - VERSÃO REDESENHADA (1920x1080)
import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager
from src.entities.hero import HeroClass


class CharacterCreationState(BaseState):
    """Tela de criação de personagem - LAYOUT OTIMIZADO 1920x1080"""

    def __init__(self, game):
        super().__init__(game)

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
            "energia": 5,  # Mantido para compatibilidade
            "mana": 5,  # Novo nome
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

            # Seleciona a primeira classe por padrão
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
                # Usa o ResourceManager para carregar a imagem da classe (ícone)
                # O tipo "class" refere-se ao ícone da classe (ex: barbaro_class.png)
                image = self.game.game_config.resource_manager.get_hero_image(
                    class_key, "class"
                )

                if image:
                    image = pygame.transform.scale(image, (100, 100))
                    self.class_images[class_key] = image
                    print(f"✅ Imagem carregada: {class_key}")
                else:
                    # Placeholder gerado pelo ResourceManager
                    self.class_images[class_key] = (
                        self.game.game_config.resource_manager._create_placeholder(
                            100, 100, (100, 100, 100), text=class_key[:3]
                        )
                    )
            except Exception as e:
                print(f"❌ Erro ao carregar imagem da classe {class_key}: {e}")
                self.class_images[class_key] = pygame.Surface((100, 100))

    def _create_ui(self):
        """Cria interface com layout otimizado para 1920x1080"""
        self.buttons.clear()
        self.class_buttons.clear()
        self.attribute_controls.clear()

        # Botões de ação (Rodapé)
        cancel_btn = Button(100, 980, 200, 60, "CANCELAR", self._cancel_creation, 24)
        confirm_btn = Button(
            1620, 980, 200, 60, "CONFIRMAR", self._confirm_character, 24
        )
        self.buttons.extend([cancel_btn, confirm_btn])

        # Botões das classes (Centralizado abaixo dos painéis)
        self._create_class_buttons()

        # Controles de atributos
        self._create_attribute_controls()

    def _create_class_buttons(self):
        """Cria botões de classe centralizados"""
        total_classes = len(self.classes)
        button_width = 180
        button_height = 160
        spacing = 20
        total_width = (button_width * total_classes) + (spacing * (total_classes - 1))
        start_x = (1920 - total_width) // 2
        start_y = 820  # Posicionado mais abaixo

        for i, (class_key, class_data) in enumerate(self.classes.items()):
            x_pos = start_x + i * (button_width + spacing)
            y_pos = start_y

            class_btn = Button(
                x_pos,
                y_pos,
                button_width,
                button_height,
                "",
                lambda c=class_key: self._select_class(c),
                20,
            )
            self.class_buttons.append(class_btn)

    def _create_attribute_controls(self):
        """Cria controles de atributos no painel central"""
        # Novo layout: 4 painéis sem margem
        # Painel Atributos começa em X=440
        panel_x = 440
        panel_y = 120

        # Coluna única centralizada no painel (abaixo da caixa de pontos)
        start_y = panel_y + 160
        spacing_y = 70  # Reduzido de 75 para 70

        attributes = [
            ("forca", "FORÇA"),
            ("destreza", "DESTREZA"),
            ("vitalidade", "VITALIDADE"),
            ("inteligencia", "INTELIGÊNCIA"),
            ("armadura", "ARMADURA"),
            ("mana", "MANA"),  # Renomeado de energia
            ("stamina", "STAMINA"),
        ]

        for i, (attr_key, attr_name) in enumerate(attributes):
            y_pos = start_y + i * spacing_y

            # Botão Menos (menor: 35x35)
            minus_btn = Button(
                panel_x + 230,
                y_pos,
                35,  # Reduzido de 45
                35,  # Reduzido de 40
                "-",
                lambda a=attr_key: self._adjust_attribute(a, -1),
                22,  # Fonte menor
            )

            # Botão Mais (menor: 35x35)
            plus_btn = Button(
                panel_x + 315,  # Ajustado para botões menores
                y_pos,
                35,
                35,
                "+",
                lambda a=attr_key: self._adjust_attribute(a, 1),
                22,
            )

            self.attribute_controls.append(
                {
                    "key": attr_key,
                    "name": attr_name,
                    "y": y_pos,
                    "minus_btn": minus_btn,
                    "plus_btn": plus_btn,
                }
            )

    def _select_class(self, class_key):
        """Seleciona uma classe"""
        self.selected_class = class_key

    def _adjust_attribute(self, attribute, change):
        """Ajusta atributo se houver pontos disponíveis"""
        current_value = self.base_attributes[attribute]

        if change > 0 and self.available_points > 0 and current_value < 15:
            self.base_attributes[attribute] += change
            self.available_points -= change
        elif change < 0 and current_value > 3:
            self.base_attributes[attribute] += change
            self.available_points -= change

    def _cancel_creation(self):
        """Cancela a criação e volta ao menu"""
        from src.states.menu_state import MenuState

        self.game.state_manager.change_state(MenuState(self.game))

    def _confirm_character(self):
        """Confirma a criação do personagem"""
        if not self.player_name.strip():
            self.game.notification_manager.add_notification(
                "Digite um nome para o personagem!", (255, 100, 100)
            )
            self.name_input_active = True
            return

        if not self.selected_class:
            self.game.notification_manager.add_notification(
                "Selecione uma classe!", (255, 100, 100)
            )
            return

        # Verifica se nome já existe no slot atual
        try:
            game_slot_id = getattr(self.game, "selected_game_slot", 1)
            cursor = self.game.game_config.database.connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM save_slots WHERE game_slot_id = ? AND hero_name = ?",
                (game_slot_id, self.player_name),
            )
            if cursor.fetchone()[0] > 0:
                self.game.notification_manager.add_notification(
                    f"O nome '{self.player_name}' já existe neste slot!",
                    (255, 100, 100),
                )
                return

            # Converte string para enum HeroClass
            hero_class = HeroClass(self.selected_class)

            # Usa o Hero Manager para criar e salvar
            hero = self.game.game_config.hero_manager.create_hero(
                self.player_name, hero_class, self.base_attributes
            )

            if hero:
                print(
                    f"🎮 Personagem criado e salvo na tabela players: {self.player_name} - {self.selected_class}"
                )

                # Atualiza o slot de jogo com as informações do personagem
                self._update_game_slot(game_slot_id, hero)

                # Cria os 3 slots de save para este slot de jogo
                self._create_save_slots(game_slot_id, hero)

                # Cria o primeiro auto-save
                self._create_auto_save(game_slot_id, hero)

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

    def _calculate_final_attributes(self):
        """Calcula atributos usando o serviço"""
        if not self.selected_class or self.selected_class not in self.classes:
            return self.base_attributes.copy()

        class_data = self.classes[self.selected_class]
        return self.creation_service.calculate_derived_attributes(
            self.base_attributes, class_data
        )

    def handle_event(self, event):
        """Processa eventos"""
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
            # Input de nome posicionado no painel da esquerda
            # Coordenadas devem bater com _render_name_input:
            # panel_rect.x = 20, input_y = panel_rect.bottom - 90 = 120 + 650 - 90 = 680
            # input_rect = (20 + 30, 680, 340, 50) -> (50, 680, 340, 50)
            name_input_rect = pygame.Rect(50, 680, 340, 50)

            if name_input_rect.collidepoint(event.pos):
                self.name_input_active = True
            else:
                self.name_input_active = False

            all_buttons = []
            all_buttons.extend(self.buttons)
            all_buttons.extend(self.class_buttons)

            for control in self.attribute_controls:
                all_buttons.append(control["minus_btn"])
                all_buttons.append(control["plus_btn"])

            ButtonManager.handle_button_click(all_buttons, event, self.game)

            if event.button == 4:
                self._scroll_up()
            elif event.button == 5:
                self._scroll_down()

    def update(self):
        """Atualiza o estado"""
        all_buttons = self.buttons + self.class_buttons
        for control in self.attribute_controls:
            all_buttons.append(control["minus_btn"])
            all_buttons.append(control["plus_btn"])

        ButtonManager.update_buttons(all_buttons, self.game)

    def render(self, surface):
        """Renderiza a tela"""
        screen_width, screen_height = surface.get_size()

        # Fundo
        surface.fill(self.game.game_config.get_color("background"))

        # Título Principal
        title_font = self.game.game_config.get_font("title", 60)
        title_text = title_font.render("CRIAÇÃO DE PERSONAGEM", True, (255, 255, 255))
        # Sombra do título
        title_shadow = title_font.render("CRIAÇÃO DE PERSONAGEM", True, (0, 0, 0))
        surface.blit(
            title_shadow, (screen_width // 2 - title_text.get_width() // 2 + 2, 42)
        )
        surface.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 40))

        # Renderiza os 4 painéis principais
        self._render_visualization_panel(surface)
        self._render_attributes_panel(surface)
        self._render_class_description_panel(surface)  # Novo painel
        self._render_stats_panel(surface)

        # Renderiza seleção de classe
        self._render_class_selection_label(surface)

        # Botões (renderiza ANTES das imagens para ficarem por baixo)
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)

        # Renderiza botões de classe com imagens (POR CIMA dos botões renderizados)
        self._render_class_buttons(surface)

        # Renderiza botões de atributos
        for control in self.attribute_controls:
            control["minus_btn"].render(surface, self.game.game_config)
            control["plus_btn"].render(surface, self.game.game_config)

    def _render_visualization_panel(self, surface):
        """Renderiza o painel de visualização (Esquerda)"""
        # Novo layout: 4 painéis sem margens
        panel_rect = pygame.Rect(20, 120, 400, 650)  # Reduzido e without margin

        # Fundo do painel
        pygame.draw.rect(surface, (30, 30, 40), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (60, 60, 80), panel_rect, 2, border_radius=20)

        # Título do Painel
        title_font = self.game.game_config.get_font("title", 32)
        title_text = title_font.render("VISUALIZAÇÃO", True, (200, 200, 220))
        surface.blit(
            title_text,
            (panel_rect.centerx - title_text.get_width() // 2, panel_rect.y + 20),
        )
        if not self.selected_class or self.selected_class not in self.classes:
            return

        class_data = self.classes[self.selected_class]

        # Área da Imagem
        image_bg_rect = pygame.Rect(0, 0, 350, 350)
        image_bg_rect.center = (panel_rect.centerx, panel_rect.y + 200)
        pygame.draw.rect(surface, (20, 20, 25), image_bg_rect, border_radius=15)
        pygame.draw.rect(
            surface, class_data["color"], image_bg_rect, 3, border_radius=15
        )

        # Imagem
        if self.selected_class in self.class_images:
            class_image = self.class_images[self.selected_class]
            # Escala a imagem para preencher melhor o box (330x330)
            scaled_image = pygame.transform.scale(class_image, (330, 330))
            image_x = image_bg_rect.centerx - scaled_image.get_width() // 2
            image_y = image_bg_rect.centery - scaled_image.get_height() // 2
            surface.blit(scaled_image, (image_x, image_y))

        # Nome da Classe (Abaixo da imagem)
        class_font = self.game.game_config.get_font("title", 40)
        class_text = class_font.render(class_data["name"], True, class_data["color"])
        surface.blit(
            class_text,
            (
                panel_rect.centerx - class_text.get_width() // 2,
                image_bg_rect.bottom + 20,
            ),
        )

        # Input de Nome (Integrado ao painel)
        self._render_name_input(surface, panel_rect)

    def _render_name_input(self, surface, panel_rect):
        """Renderiza o campo de nome dentro do painel de visualização"""
        input_y = panel_rect.bottom - 90

        name_font = self.game.game_config.get_font("menu", 24)
        name_title = name_font.render("NOME DO PERSONAGEM:", True, (255, 255, 255))
        surface.blit(name_title, (panel_rect.x + 30, input_y - 35))

        input_rect = pygame.Rect(
            panel_rect.x + 30, input_y, 340, 50
        )  # Reduzido para caber
        border_color = (100, 200, 255) if self.name_input_active else (80, 80, 100)
        bg_color = (20, 20, 25)

        pygame.draw.rect(surface, bg_color, input_rect, border_radius=10)
        pygame.draw.rect(surface, border_color, input_rect, 2, border_radius=10)

        display_text = self.player_name
        text_color = (255, 255, 255)

        if not self.player_name and not self.name_input_active:
            display_text = "Digite o nome..."
            text_color = (100, 100, 100)

        text_surface = name_font.render(display_text, True, text_color)
        surface.blit(
            text_surface,
            (input_rect.x + 15, input_rect.centery - text_surface.get_height() // 2),
        )

        if self.name_input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = (
                input_rect.x
                + 15
                + (name_font.size(self.player_name)[0] if self.player_name else 0)
            )
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (cursor_x, input_rect.y + 10),
                (cursor_x, input_rect.y + 40),
                2,
            )

    def _render_attributes_panel(self, surface):
        """Renderiza o painel de atributos (2ª coluna)"""
        # Novo layout: X=440, largura=400
        panel_rect = pygame.Rect(440, 120, 400, 650)

        pygame.draw.rect(surface, (30, 30, 40), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (60, 60, 80), panel_rect, 2, border_radius=20)

        title_font = self.game.game_config.get_font("title", 32)
        title_text = title_font.render("ATRIBUTOS", True, (200, 200, 220))
        surface.blit(
            title_text,
            (panel_rect.centerx - title_text.get_width() // 2, panel_rect.y + 20),
        )

        # Pontos disponíveis (Destaque MELHORADO)
        points_bg_rect = pygame.Rect(
            panel_rect.x + 40, panel_rect.y + 70, panel_rect.width - 80, 55
        )
        pygame.draw.rect(surface, (20, 20, 25), points_bg_rect, border_radius=10)
        # Borda destacada quando há pontos
        border_color = (100, 255, 100) if self.available_points > 0 else (60, 60, 80)
        pygame.draw.rect(surface, border_color, points_bg_rect, 2, border_radius=10)

        points_font = self.game.game_config.get_font(
            "title", 32
        )  # Aumentado de 28 para 32
        points_color = (100, 255, 100) if self.available_points > 0 else (150, 150, 150)
        points_text = points_font.render(
            f"PONTOS DISPONÍVEIS: {self.available_points}", True, points_color
        )
        surface.blit(
            points_text,
            (
                points_bg_rect.centerx - points_text.get_width() // 2,
                points_bg_rect.centery - points_text.get_height() // 2,
            ),
        )

        # Renderiza os controles
        for control in self.attribute_controls:
            self._render_attribute_control(surface, control, panel_rect.x)

    def _render_attribute_control(self, surface, control, panel_x):
        """Renderiza uma linha de controle de atributo"""
        attr_value = self.base_attributes[control["key"]]
        y_pos = control["y"]

        # Nome do atributo (melhor centralizado)
        name_font = self.game.game_config.get_font("menu", 22)
        name_surface = name_font.render(control["name"], True, (220, 220, 220))
        # Centralizado melhor
        surface.blit(name_surface, (panel_x + 55, y_pos + 5))

        # Valor (Centralizado entre botões)
        # Botões estão em x+230 (fim ~265) e x+315 (início). Centro aprox x+272
        value_bg_rect = pygame.Rect(panel_x + 270, y_pos, 55, 35)  # Menor
        pygame.draw.rect(surface, (20, 20, 25), value_bg_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 60, 80), value_bg_rect, 1, border_radius=8)

        value_font = self.game.game_config.get_font("title", 24)  # Menor
        value_color = (
            (255, 255, 0) if attr_value > 5 else (255, 255, 255)
        )  # Destaque se modificado
        value_surface = value_font.render(str(attr_value), True, value_color)
        surface.blit(
            value_surface,
            (
                value_bg_rect.centerx - value_surface.get_width() // 2,
                value_bg_rect.centery - value_surface.get_height() // 2,
            ),
        )

    def _render_class_description_panel(self, surface):
        """Renderiza o painel de descrição da classe (3ª coluna)"""
        # Novo layout: X=860, largura=400
        panel_rect = pygame.Rect(860, 120, 460, 650)

        pygame.draw.rect(surface, (30, 30, 40), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (60, 60, 80), panel_rect, 2, border_radius=20)

        title_font = self.game.game_config.get_font("title", 32)
        title_text = title_font.render("HABILIDADES", True, (200, 200, 220))
        surface.blit(
            title_text,
            (panel_rect.centerx - title_text.get_width() // 2, panel_rect.y + 20),
        )

        if not self.selected_class or self.selected_class not in self.classes:
            # Mensagem placeholder
            placeholder_font = self.game.game_config.get_font("menu", 22)
            placeholder_text = placeholder_font.render(
                "Selecione uma classe para ver detalhes", True, (150, 150, 150)
            )
            surface.blit(
                placeholder_text,
                (
                    panel_rect.centerx - placeholder_text.get_width() // 2,
                    panel_rect.centery,
                ),
            )
            return

        # Área de conteúdo
        content_y = panel_rect.y + 70
        content_font = self.game.game_config.get_font("menu", 22)  # Fonte maior

        # Pega dados da classe selecionada
        class_data = self.classes[self.selected_class]

        # Descrição dinâmica da classe
        desc_font = self.game.game_config.get_font("menu", 24)
        desc_lines = self._wrap_text(class_data["description"], desc_font, 400)

        for i, line in enumerate(desc_lines):
            desc_surface = desc_font.render(line, True, (220, 220, 200))
            surface.blit(desc_surface, (panel_rect.x + 30, content_y + i * 32))

        content_y += len(desc_lines) * 32 + 40

        # Bônus da classe
        bonus_title_font = self.game.game_config.get_font("title", 26)
        bonus_title = bonus_title_font.render(
            "⚔️ Bônus de Atributos:", True, (100, 200, 255)
        )
        surface.blit(bonus_title, (panel_rect.x + 30, content_y))
        content_y += 40

        # Atributos base da classe (do hero.py)
        from src.entities.hero import Hero, HeroClass  # Import correto

        hero_class_enum = HeroClass(self.selected_class)
        temp_hero = Hero("temp", hero_class_enum, self.base_attributes)
        class_bonuses = temp_hero._get_class_bonus()

        bonus_font = self.game.game_config.get_font("menu", 22)
        for attr, value in class_bonuses.items():
            sign = "+" if value > 0 else ""
            attr_name = attr.upper().replace("_", " ")
            bonus_text = bonus_font.render(
                f"• {attr_name}: {sign}{value}",
                True,
                (100, 255, 100) if value > 0 else (255, 100, 100),
            )
            surface.blit(bonus_text, (panel_rect.x + 50, content_y))
            content_y += 30

    def _render_stats_panel(self, surface):
        """Renderiza o painel de estatísticas (Direita)"""
        # Mais estreito e reposicionado
        panel_rect = pygame.Rect(1350, 120, 420, 650)

        pygame.draw.rect(surface, (30, 30, 40), panel_rect, border_radius=20)
        pygame.draw.rect(surface, (60, 60, 80), panel_rect, 2, border_radius=20)

        title_font = self.game.game_config.get_font("title", 28)
        title_text = title_font.render("ATRIBUTOS DETALHADOS", True, (200, 200, 220))
        surface.blit(
            title_text,
            (panel_rect.centerx - title_text.get_width() // 2, panel_rect.y + 20),
        )

        # Área de scroll
        scroll_area = pygame.Rect(
            panel_rect.x + 20,
            panel_rect.y + 70,
            panel_rect.width - 40,
            panel_rect.height - 90,
        )
        # Fundo da área de scroll
        pygame.draw.rect(surface, (20, 20, 25), scroll_area, border_radius=15)

        final_attributes = self._calculate_final_attributes()
        self._render_scrollable_stats(surface, scroll_area, final_attributes)

    def _render_scrollable_stats(self, surface, scroll_area, attributes):
        """Renderiza estatísticas com scroll"""
        # Grupos organizados
        attribute_groups = {
            "COMBATE": [
                "vida_maxima",
                "mana_maxima",
                "dano_fisico_min",
                "dano_fisico_max",
                "dano_magico_min",
                "dano_magico_max",
                "defesa_fisica",
                "defesa_magica",
            ],
            "AVANÇADO": [
                "bloqueio",
                "chance_critico",
                "dano_critico",
                "chance_esquiva",
                "velocidade_ataque",
                "precisao",
            ],
            "RESISTÊNCIAS": [
                "resistencia_fogo",
                "resistencia_gelo",
                "resistencia_eletrico",
                "resistencia_veneno",
                "resistencia_escuro",
            ],
            "OUTROS": [
                "regeneracao_vida",
                "regeneracao_mana",
                "sorte",
                "velocidade_movimento",
                "capacidade_carga",
            ],
        }

        y_offset = scroll_area.y + 15 - self.stats_scroll_offset * 40

        group_font = self.game.game_config.get_font("title", 30)
        attr_font = self.game.game_config.get_font("menu", 26)

        for group_name, attrs in attribute_groups.items():
            # Renderiza Título do Grupo
            if y_offset + 30 > scroll_area.top and y_offset < scroll_area.bottom:
                pygame.draw.line(
                    surface,
                    (60, 60, 80),
                    (scroll_area.x + 20, y_offset + 15),
                    (scroll_area.right - 20, y_offset + 15),
                    1,
                )
                group_surface = group_font.render(group_name, True, (100, 200, 255))
                surface.blit(group_surface, (scroll_area.x + 20, y_offset))

            y_offset += 35

            # Renderiza Atributos do Grupo
            for attr_key in attrs:
                if y_offset + 25 > scroll_area.top and y_offset < scroll_area.bottom:
                    # Nome
                    display_name = attr_key.replace("_", " ").upper()
                    name_surface = attr_font.render(display_name, True, (180, 180, 180))
                    surface.blit(name_surface, (scroll_area.x + 30, y_offset))

                    # Valor
                    value = attributes.get(attr_key, 0)
                    value_str = (
                        str(int(value))
                        if isinstance(value, (int, float))
                        else str(value)
                    )

                    # Formatação especial para porcentagens
                    if (
                        "chance" in attr_key
                        or "resistencia" in attr_key
                        or "bloqueio" in attr_key
                    ):
                        value_str += "%"

                    value_surface = attr_font.render(value_str, True, (255, 255, 255))
                    surface.blit(
                        value_surface,
                        (
                            scroll_area.right - 50 - value_surface.get_width(),
                            y_offset,
                        ),  # Margem extra para scrollbar
                    )

                y_offset += 35

                # Linha separadora entre atributos
                if y_offset > scroll_area.top and y_offset < scroll_area.bottom:
                    pygame.draw.line(
                        surface,
                        (40, 40, 50),
                        (scroll_area.x + 30, y_offset - 5),
                        (scroll_area.right - 30, y_offset - 5),
                        1,
                    )

            y_offset += 20  # Espaço entre grupos

        content_height = y_offset - scroll_area.y
        self.max_stats_scroll = max(0, (content_height - scroll_area.height) // 40)

        # Desenha barra de scroll visual
        if self.max_stats_scroll > 0:
            scrollbar_height = max(
                30, scroll_area.height * scroll_area.height // content_height
            )
            scrollbar_y = scroll_area.y + (
                self.stats_scroll_offset / self.max_stats_scroll
            ) * (scroll_area.height - scrollbar_height)
            scrollbar_rect = pygame.Rect(
                scroll_area.right - 8, scrollbar_y, 6, scrollbar_height
            )
            pygame.draw.rect(surface, (100, 100, 150), scrollbar_rect, border_radius=3)

    def _render_class_buttons(self, surface):
        """Renderiza os botões de classe com imagens"""
        for i, btn in enumerate(self.class_buttons):
            # Renderiza o botão base (fundo e borda)
            btn.render(surface, self.game.game_config)

            # Identifica a classe deste botão
            class_keys = list(self.classes.keys())
            if i < len(class_keys):
                class_key = class_keys[i]

                # Desenha a imagem da classe preenchendo o botão
                if class_key in self.class_images:
                    img = self.class_images[class_key]
                    # Escala para o tamanho do botão (com margem maior para não vazar)
                    icon_size = btn.rect.width - 20  # Margem de 10px de cada lado
                    scaled_img = pygame.transform.scale(img, (icon_size, icon_size))

                    # Centraliza no botão
                    img_x = btn.rect.centerx - scaled_img.get_width() // 2
                    img_y = btn.rect.centery - scaled_img.get_height() // 2

                    # Efeito de "pressionado" se selecionado
                    if self.selected_class == class_key:
                        img_y += 4  # Desloca para baixo

                    surface.blit(scaled_img, (img_x, img_y))

                # Nome da classe ABAIXO do botão
                name_font = self.game.game_config.get_font("menu", 18)
                color = self.classes[class_key]["color"]
                # Se selecionado, destaca
                if self.selected_class == class_key:
                    color = (255, 255, 255)

                name_text = name_font.render(
                    self.classes[class_key]["name"], True, color
                )
                surface.blit(
                    name_text,
                    (
                        btn.rect.centerx - name_text.get_width() // 2,
                        btn.rect.bottom + 10,
                    ),
                )

    def _render_class_selection_label(self, surface):
        """Renderiza o label 'ESCOLHA SUA CLASSE'"""
        # Não é mais necessário pois os botões são auto-explicativos e têm destaque,
        # mas podemos manter um título sutil se desejado.
        pass

    def _wrap_text(self, text, font, max_width):
        """Quebra texto em múltiplas linhas"""
        words = text.split(" ")
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            test_width = font.size(test_line)[0]

            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _scroll_up(self):
        """Rola para cima"""
        self.stats_scroll_offset = max(0, self.stats_scroll_offset - 1)

    def _scroll_down(self):
        """Rola para baixo"""
        self.stats_scroll_offset = min(
            self.max_stats_scroll, self.stats_scroll_offset + 1
        )

    def _update_game_slot(self, game_slot_id, hero):
        """Atualiza o slot de jogo com as informações do personagem criado"""
        try:
            cursor = self.game.game_config.database.connection.cursor()

            # Obtém a classe do herói
            class_data = self.game.game_config.database.get_hero_class_by_key(
                hero.hero_class.value
            )

            cursor.execute(
                """
                UPDATE game_slots 
                SET player_name = ?, 
                    player_class = ?, 
                    player_level = ?,
                    zone_name = 'Início',
                    playtime = 0,
                    last_played = CURRENT_TIMESTAMP,
                    is_active = 1
                WHERE slot_id = ?
                """,
                (
                    hero.name,
                    class_data["name"] if class_data else hero.hero_class.value,
                    hero.level,
                    game_slot_id,
                ),
            )
            self.game.game_config.database.connection.commit()
            print(f"✅ Slot de jogo {game_slot_id} atualizado com {hero.name}")
        except Exception as e:
            print(f"❌ Erro ao atualizar slot de jogo: {e}")

    def _create_save_slots(self, game_slot_id, hero):
        """Cria os 3 slots de save para o slot de jogo (1 auto + 2 manuais)"""
        try:
            cursor = self.game.game_config.database.connection.cursor()

            # Obtém a classe do herói
            class_data = self.game.game_config.database.get_hero_class_by_key(
                hero.hero_class.value
            )
            class_name = class_data["name"] if class_data else hero.hero_class.value

            # Cria os 3 slots de save
            save_slots = [
                (game_slot_id, 1, "auto", "Auto Save", "Save automático inicial"),
                (game_slot_id, 2, "manual", "Save Manual 1", ""),
                (game_slot_id, 3, "manual", "Save Manual 2", ""),
            ]

            for slot_data in save_slots:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO save_slots 
                    (game_slot_id, save_slot_id, slot_type, save_title, save_description,
                     hero_name, hero_level, hero_class, zone_name, zone_id, playtime, is_active)
                    VALUES (?, ?, ?, ?, ?, NULL, 1, NULL, 'Início', 1, 0, 0)
                    """,
                    slot_data,
                )

            self.game.game_config.database.connection.commit()
            print(f"✅ Slots de save criados para o slot de jogo {game_slot_id}")
        except Exception as e:
            print(f"❌ Erro ao criar slots de save: {e}")

    def _create_auto_save(self, game_slot_id, hero):
        """Cria o primeiro auto-save para o personagem"""
        try:
            cursor = self.game.game_config.database.connection.cursor()

            # Obtém a classe do herói
            class_data = self.game.game_config.database.get_hero_class_by_key(
                hero.hero_class.value
            )
            class_name = class_data["name"] if class_data else hero.hero_class.value

            # Atualiza o slot de auto-save (save_slot_id = 1)
            cursor.execute(
                """
                UPDATE save_slots 
                SET hero_name = ?,
                    hero_level = ?,
                    hero_class = ?,
                    zone_name = 'Início',
                    zone_id = 1,
                    playtime = 0,
                    save_title = 'Auto Save - Início da Jornada',
                    save_description = ?,
                    last_saved = CURRENT_TIMESTAMP,
                    is_active = 1
                WHERE game_slot_id = ? AND save_slot_id = 1
                """,
                (
                    hero.name,
                    hero.level,
                    class_name,
                    f"{hero.name} iniciou sua jornada como {class_name}",
                    game_slot_id,
                ),
            )

            self.game.game_config.database.connection.commit()
            print(f"💾 Auto-save criado para {hero.name} no slot {game_slot_id}")
        except Exception as e:
            print(f"❌ Erro ao criar auto-save: {e}")

    def enter(self):
        """Chamado ao entrar no estado"""
        print("🎭 Entrando na criação de personagem")

    def exit(self):
        """Chamado ao sair do estado"""
        print("🎭 Saindo da criação de personagem")

    def on_resize(self, old_size, new_size):
        """Recria a UI ao redimensionar"""
        self._create_ui()
