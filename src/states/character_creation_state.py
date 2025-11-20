# src/states/character_creation_state.py - VERSÃO COMPLETA E CORRETA
import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager
from src.entities.hero import HeroClass

class CharacterCreationState(BaseState):
    """Tela de criação de personagem - USANDO BANCO DE DADOS"""
    
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
            'forca': 5,
            'destreza': 5, 
            'vitalidade': 5,
            'inteligencia': 5,
            'armadura': 5,
            'energia': 5,
            'stamina': 5
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
                class_key = class_data['class_key']
                self.classes[class_key] = self.creation_service.get_class_display_info(class_key)
            
            # Seleciona a primeira classe por padrão
            if self.classes:
                self.selected_class = list(self.classes.keys())[0]
                
            print(f"✅ Classes carregadas do banco: {len(self.classes)}")
            
        except Exception as e:
            print(f"❌ Erro crítico ao carregar classes do banco: {e}")
            raise

    def _load_class_images(self):
        """Carrega as imagens das classes"""
        for class_key, class_data in self.classes.items():
            try:
                import os
                icon_path = class_data.get('icon_path', '')
                if icon_path and os.path.exists(icon_path):
                    image = pygame.image.load(icon_path).convert_alpha()
                    image = pygame.transform.scale(image, (60, 60))
                    self.class_images[class_key] = image
                    print(f"✅ Imagem carregada: {class_key}")
                else:
                    # Cria placeholder apenas se a imagem não existir
                    surface = pygame.Surface((60, 60), pygame.SRCALPHA)
                    color = class_data.get('color', (128, 128, 128))
                    pygame.draw.rect(surface, color, (5, 5, 50, 50), border_radius=8)
                    pygame.draw.rect(surface, (255, 255, 255), (5, 5, 50, 50), 2, border_radius=8)
                    self.class_images[class_key] = surface
                    print(f"⚠️  Placeholder criado para: {class_key}")
            except Exception as e:
                print(f"❌ Erro ao carregar imagem da classe {class_key}: {e}")
                # Cria placeholder em caso de erro
                surface = pygame.Surface((60, 60), pygame.SRCALPHA)
                color = class_data.get('color', (128, 128, 128))
                pygame.draw.rect(surface, color, (5, 5, 50, 50), border_radius=8)
                pygame.draw.rect(surface, (255, 255, 255), (5, 5, 50, 50), 2, border_radius=8)
                self.class_images[class_key] = surface

    def _create_ui(self):
        """Cria interface com layout otimizado"""
        self.buttons.clear()
        self.class_buttons.clear()
        self.attribute_controls.clear()
        
        # Botões de ação
        cancel_btn = Button(100, 950, 200, 60, "CANCELAR", self._cancel_creation, 24)
        confirm_btn = Button(1620, 950, 200, 60, "CONFIRMAR", self._confirm_character, 24)
        self.buttons.extend([cancel_btn, confirm_btn])
        
        # Botões das classes
        self._create_class_buttons()
        
        # Controles de atributos
        self._create_attribute_controls()

    def _create_class_buttons(self):
        """Cria botões de classe com layout compacto"""
        total_classes = len(self.classes)
        button_width = 150
        button_height = 130
        spacing = 10
        total_width = (button_width * total_classes) + (spacing * (total_classes - 1))
        start_x = (1920 - total_width) // 2
        start_y = 750
        
        for i, (class_key, class_data) in enumerate(self.classes.items()):
            x_pos = start_x + i * (button_width + spacing)
            y_pos = start_y
            
            class_btn = Button(
                x_pos, y_pos, button_width, button_height,
                "",
                lambda c=class_key: self._select_class(c),
                20
            )
            self.class_buttons.append(class_btn)

    def _create_attribute_controls(self):
        """Cria controles de atributos com layout organizado"""
        # Coluna 1 - Atributos principais
        col1_attributes = [
            ('forca', 'FORÇA', 500, 200),
            ('destreza', 'DESTREZA', 500, 280),
            ('vitalidade', 'VITALIDADE', 500, 360),
            ('inteligencia', 'INTELIGÊNCIA', 500, 440)
        ]
        
        # Coluna 2 - Atributos secundários
        col2_attributes = [
            ('armadura', 'ARMADURA', 800, 200),
            ('energia', 'ENERGIA', 800, 280),
            ('stamina', 'STAMINA', 800, 360)
        ]
        
        for attr_key, attr_name, x_pos, y_pos in col1_attributes + col2_attributes:
            minus_btn = Button(
                x_pos, y_pos, 35, 35, "-",
                lambda a=attr_key: self._adjust_attribute(a, -1), 20
            )
            
            plus_btn = Button(
                x_pos + 80, y_pos, 35, 35, "+",
                lambda a=attr_key: self._adjust_attribute(a, 1), 20
            )
            
            self.attribute_controls.append({
                'key': attr_key,
                'name': attr_name,
                'x': x_pos,
                'y': y_pos,
                'minus_btn': minus_btn,
                'plus_btn': plus_btn
            })

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
        """Confirma a criação do personagem usando o novo sistema"""
        if not self.player_name.strip():
            print("⚠️ Por favor, digite um nome para o personagem")
            self.name_input_active = True
            return
        
        if not self.selected_class:
            print("⚠️ Por favor, selecione uma classe")
            return
        
        try:
            # Valida o nome usando o serviço
            is_valid, message = self.creation_service.validate_character_name(self.player_name)
            if not is_valid:
                print(f"❌ {message}")
                self.name_input_active = True
                return
            
            # Converte string para enum HeroClass
            hero_class = HeroClass(self.selected_class)
            
            # Usa o Hero Manager para criar e salvar
            hero = self.game.game_config.hero_manager.create_hero(
                self.player_name, 
                hero_class, 
                self.base_attributes
            )
            
            if hero:
                print(f"🎮 Personagem criado e salvo na tabela players: {self.player_name} - {self.selected_class}")
                
                from src.states.menu_state import MenuState
                self.game.state_manager.change_state(MenuState(self.game))
            else:
                print("❌ Falha ao criar personagem")
            
        except Exception as e:
            print(f"❌ Erro ao criar personagem: {e}")

    def _calculate_final_attributes(self):
        """Calcula atributos usando o serviço"""
        if not self.selected_class or self.selected_class not in self.classes:
            return self.base_attributes.copy()
        
        class_data = self.classes[self.selected_class]
        return self.creation_service.calculate_derived_attributes(self.base_attributes, class_data)

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
                if (self.name_input_active and len(self.player_name) < 20 and event.unicode.isprintable()):
                    self.player_name += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            name_input_rect = pygame.Rect(150, 600, 400, 50)
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
        mouse_pos = pygame.mouse.get_pos()
        
        all_buttons = self.buttons + self.class_buttons
        for control in self.attribute_controls:
            all_buttons.append(control['minus_btn'])
            all_buttons.append(control['plus_btn'])
        
        ButtonManager.update_buttons(all_buttons, self.game)

    def render(self, surface):
        """Renderiza a tela"""
        screen_width, screen_height = surface.get_size()
        
        # Fundo
        surface.fill((20, 20, 30))
        
        # Título
        title_font = self.game.game_config.get_font('title', 48)
        title_text = title_font.render("CRIAÇÃO DE PERSONAGEM", True, (255, 255, 255))
        surface.blit(title_text, (screen_width//2 - title_text.get_width()//2, 40))
        
        # Painéis
        self._render_visualization_panel(surface)
        self._render_name_input(surface)
        self._render_attributes_panel(surface)
        self._render_stats_panel(surface)
        self._render_class_buttons(surface)
        
        # Botões
        all_buttons = self.buttons + self.class_buttons
        for control in self.attribute_controls:
            all_buttons.append(control['minus_btn'])
            all_buttons.append(control['plus_btn'])
        
        ButtonManager.render_buttons(all_buttons, surface, self.game.game_config)

    def _render_visualization_panel(self, surface):
        """Renderiza o painel de visualização"""
        if not self.selected_class or self.selected_class not in self.classes:
            return
            
        class_data = self.classes[self.selected_class]
        
        # Painel principal
        panel_rect = pygame.Rect(100, 150, 400, 400)
        pygame.draw.rect(surface, (35, 35, 45), panel_rect, border_radius=15)
        pygame.draw.rect(surface, (70, 70, 90), panel_rect, 3, border_radius=15)
        
        # Título
        title_font = self.game.game_config.get_font('title', 28)
        title_text = title_font.render("VISUALIZAÇÃO", True, (255, 255, 255))
        surface.blit(title_text, (panel_rect.x + 20, panel_rect.y - 35))
        
        # Imagem da classe
        image_rect = pygame.Rect(panel_rect.centerx - 80, panel_rect.y + 50, 160, 160)
        pygame.draw.rect(surface, (25, 25, 35), image_rect, border_radius=12)
        pygame.draw.rect(surface, class_data['color'], image_rect, 3, border_radius=12)
        
        if self.selected_class in self.class_images:
            class_image = self.class_images[self.selected_class]
            image_x = image_rect.centerx - class_image.get_width() // 2
            image_y = image_rect.centery - class_image.get_height() // 2
            surface.blit(class_image, (image_x, image_y))
        
        # Nome da classe
        class_font = self.game.game_config.get_font('title', 32)
        class_text = class_font.render(class_data['name'], True, class_data['color'])
        surface.blit(class_text, (panel_rect.centerx - class_text.get_width()//2, panel_rect.y + 230))
        
        # Descrição
        desc_font = self.game.game_config.get_font('menu', 18)
        desc_lines = self._wrap_text(class_data['description'], desc_font, 360)
        for i, line in enumerate(desc_lines):
            desc_surface = desc_font.render(line, True, (200, 200, 200))
            surface.blit(desc_surface, (panel_rect.x + 20, panel_rect.y + 280 + i * 25))

    def _render_name_input(self, surface):
        """Renderiza o campo de nome"""
        name_font = self.game.game_config.get_font('menu', 28)
        name_title = name_font.render("NOME DO PERSONAGEM:", True, (255, 255, 255))
        surface.blit(name_title, (150, 580))
        
        input_rect = pygame.Rect(150, 620, 400, 50)
        border_color = (100, 200, 255) if self.name_input_active else (80, 80, 100)
        pygame.draw.rect(surface, (40, 40, 50), input_rect, border_radius=8)
        pygame.draw.rect(surface, border_color, input_rect, 2, border_radius=8)
        
        name_text = name_font.render(self.player_name, True, (255, 255, 255))
        surface.blit(name_text, (input_rect.x + 10, input_rect.y + 10))
        
        if not self.player_name and not self.name_input_active:
            placeholder_font = self.game.game_config.get_font('menu', 24)
            placeholder_text = placeholder_font.render("Digite o nome...", True, (120, 120, 120))
            surface.blit(placeholder_text, (input_rect.x + 10, input_rect.y + 10))
        
        if self.name_input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = input_rect.x + 10 + name_text.get_width()
            pygame.draw.line(surface, (255, 255, 255), 
                           (cursor_x, input_rect.y + 10), 
                           (cursor_x, input_rect.y + 40), 2)

    def _render_attributes_panel(self, surface):
        """Renderiza o painel de atributos básicos"""
        panel_rect = pygame.Rect(600, 150, 600, 400)
        pygame.draw.rect(surface, (35, 35, 45), panel_rect, border_radius=15)
        pygame.draw.rect(surface, (70, 70, 90), panel_rect, 3, border_radius=15)
        
        title_font = self.game.game_config.get_font('title', 28)
        title_text = title_font.render("ATRIBUTOS BÁSICOS", True, (255, 255, 255))
        surface.blit(title_text, (panel_rect.x + 20, panel_rect.y - 35))
        
        # Pontos disponíveis
        points_font = self.game.game_config.get_font('menu', 26)
        points_text = points_font.render(f"PONTOS DISPONÍVEIS: {self.available_points}", True, (100, 200, 255))
        surface.blit(points_text, (panel_rect.x + 20, panel_rect.y + 20))
        
        # Divisória
        pygame.draw.line(surface, (60, 60, 80), 
                        (panel_rect.x + 20, panel_rect.y + 60), 
                        (panel_rect.x + panel_rect.width - 20, panel_rect.y + 60), 2)
        
        # Controles de atributos
        for control in self.attribute_controls:
            self._render_attribute_control(surface, control)

    def _render_attribute_control(self, surface, control):
        """Renderiza um controle de atributo individual"""
        attr_value = self.base_attributes[control['key']]
        
        # Nome do atributo
        name_font = self.game.game_config.get_font('menu', 22)
        name_surface = name_font.render(control['name'], True, (255, 255, 255))
        surface.blit(name_surface, (control['x'] + 130, control['y'] + 5))
        
        # Valor do atributo (entre os botões)
        value_font = self.game.game_config.get_font('title', 26)
        value_surface = value_font.render(str(attr_value), True, (255, 255, 0))
        value_x = control['x'] + 40
        value_y = control['y'] + 2
        surface.blit(value_surface, (value_x, value_y))

    def _render_stats_panel(self, surface):
        """Renderiza o painel de estatísticas detalhadas"""
        panel_rect = pygame.Rect(1250, 150, 550, 400)
        pygame.draw.rect(surface, (35, 35, 45), panel_rect, border_radius=15)
        pygame.draw.rect(surface, (70, 70, 90), panel_rect, 3, border_radius=15)
        
        title_font = self.game.game_config.get_font('title', 26)
        title_text = title_font.render("ESTATÍSTICAS DETALHADAS", True, (255, 255, 255))
        surface.blit(title_text, (panel_rect.x + 20, panel_rect.y - 35))
        
        # Área de scroll
        scroll_area = pygame.Rect(panel_rect.x + 20, panel_rect.y + 20, panel_rect.width - 40, panel_rect.height - 40)
        pygame.draw.rect(surface, (25, 25, 35), scroll_area, border_radius=10)
        
        final_attributes = self._calculate_final_attributes()
        self._render_scrollable_stats(surface, scroll_area, final_attributes)

    def _render_scrollable_stats(self, surface, scroll_area, attributes):
        """Renderiza estatísticas com scroll"""
        attribute_groups = {
            'ATRIBUTOS PRIMÁRIOS': [
                'forca', 'destreza', 'vitalidade', 'inteligencia', 
                'armadura', 'energia', 'stamina'
            ],
            'ATRIBUTOS DE COMBATE': [
                'vida_maxima', 'mana_maxima', 'dano_fisico_min', 'dano_fisico_max',
                'dano_magico_min', 'dano_magico_max', 'defesa_fisica', 'defesa_magica'
            ],
            'ATRIBUTOS AVANÇADOS': [
                'bloqueio', 'chance_critico', 'dano_critico', 'chance_esquiva',
                'velocidade_ataque', 'precisao', 'regeneracao_vida', 'regeneracao_mana',
                'resistencia_fogo', 'resistencia_gelo', 'resistencia_eletrico',
                'resistencia_veneno', 'resistencia_escuro', 'sorte',
                'velocidade_movimento', 'capacidade_carga'
            ]
        }
        
        y_offset = scroll_area.y + 10 - self.stats_scroll_offset * 35
        
        group_font = self.game.game_config.get_font('menu', 24)
        attr_font = self.game.game_config.get_font('menu', 22)
        
        for group_name, attrs in attribute_groups.items():
            group_y = y_offset
            if group_y + 30 > scroll_area.top and group_y < scroll_area.bottom:
                group_surface = group_font.render(group_name, True, (100, 200, 255))
                surface.blit(group_surface, (scroll_area.x + 10, group_y))
            
            y_offset += 35
            
            for attr_key in attrs:
                attr_y = y_offset
                if attr_y + 28 > scroll_area.top and attr_y < scroll_area.bottom:
                    display_name = attr_key.replace('_', ' ').upper()
                    name_surface = attr_font.render(display_name, True, (200, 200, 200))
                    surface.blit(name_surface, (scroll_area.x + 20, attr_y))
                    
                    value = attributes.get(attr_key, 0)
                    value_str = str(int(value)) if isinstance(value, (int, float)) else str(value)
                    
                    value_surface = attr_font.render(value_str, True, (255, 255, 255))
                    surface.blit(value_surface, (scroll_area.x + 350, attr_y))
                
                y_offset += 30
            
            y_offset += 10
        
        content_height = y_offset - scroll_area.y
        self.max_stats_scroll = max(0, (content_height - scroll_area.height) // 35)

    def _render_class_buttons(self, surface):
        """Renderiza os botões de seleção de classe"""
        title_font = self.game.game_config.get_font('title', 32)
        title_text = title_font.render("ESCOLHA SUA CLASSE", True, (255, 255, 255))
        surface.blit(title_text, (1920//2 - title_text.get_width()//2, 680))
        
        for i, (class_key, class_data) in enumerate(self.classes.items()):
            if i < len(self.class_buttons):
                button = self.class_buttons[i]
                button_rect = button.base_rect
                
                is_selected = class_key == self.selected_class
                border_color = class_data['color'] if is_selected else (80, 80, 100)
                bg_color = (45, 45, 60) if not is_selected else (60, 45, 50)
                
                # Botão
                pygame.draw.rect(surface, bg_color, button_rect, border_radius=12)
                pygame.draw.rect(surface, border_color, button_rect, 3, border_radius=12)
                
                # Imagem da classe
                if class_key in self.class_images:
                    class_image = self.class_images[class_key]
                    image_x = button_rect.centerx - class_image.get_width() // 2
                    image_y = button_rect.y + 15
                    surface.blit(class_image, (image_x, image_y))
                
                # Nome da classe
                name_font = self.game.game_config.get_font('menu', 18)
                name_text = name_font.render(class_data['name'], True, (255, 255, 255))
                surface.blit(name_text, (button_rect.centerx - name_text.get_width()//2, button_rect.y + 85))
                
                # Indicador de seleção
                if is_selected:
                    indicator_font = self.game.game_config.get_font('menu', 14)
                    indicator_text = indicator_font.render("SELECIONADO", True, class_data['color'])
                    surface.blit(indicator_text, (button_rect.centerx - indicator_text.get_width()//2, button_rect.y + 105))

    def _wrap_text(self, text, font, max_width):
        """Quebra texto em múltiplas linhas"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def _scroll_up(self):
        """Rola para cima"""
        self.stats_scroll_offset = max(0, self.stats_scroll_offset - 1)

    def _scroll_down(self):
        """Rola para baixo"""
        self.stats_scroll_offset = min(self.max_stats_scroll, self.stats_scroll_offset + 1)

    def enter(self):
        """Chamado ao entrar no estado"""
        print("🎭 Entrando na criação de personagem")

    def exit(self):
        """Chamado ao sair do estado"""
        print("🎭 Saindo da création de personagem")

    def on_resize(self, old_size, new_size):
        """Recria a UI ao redimensionar"""
        self._create_ui()