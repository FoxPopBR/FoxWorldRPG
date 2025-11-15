import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.responsive_ui import ResponsiveUI
from src.ui.button_manager import ButtonManager

class CharacterCreationState(BaseState):
    """Tela única de criação de personagem com design melhorado"""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Dados do personagem
        self.player_name = "Aragorn"
        self.selected_class = "barbaro"
        self.available_points = 10
        
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
        
        # Classes disponíveis
        self.classes = {
            'barbaro': {
                'name': 'BÁRBARO',
                'description': 'Guerreiro feroz com força bruta e resistência inigualável. Especializado em combate corpo a corpo.',
                'bonus': {'forca': 3, 'vitalidade': 2, 'stamina': 2},
                'color': (180, 60, 60),
                'primary_stat': 'FORÇA',
                'secondary_stat': 'VITALIDADE'
            },
            'paladino': {
                'name': 'PALADINO',
                'description': 'Cavaleiro sagrado abençoado com poderes divinos. Excelente defensor com habilidades de cura.',
                'bonus': {'armadura': 3, 'forca': 2, 'energia': 1},
                'color': (240, 200, 80),
                'primary_stat': 'ARMADURA',
                'secondary_stat': 'FORÇA'
            },
            'druida': {
                'name': 'DRUIDA', 
                'description': 'Mestre da natureza com poderes de transformação e cura. Conectado com os espíritos animais.',
                'bonus': {'inteligencia': 2, 'energia': 2, 'vitalidade': 1},
                'color': (60, 150, 80),
                'primary_stat': 'INTELIGÊNCIA',
                'secondary_stat': 'ENERGIA'
            },
            'feiticeiro': {
                'name': 'FEITICEIRO',
                'description': 'Conjurador de magias arcanas elementais. Poder devastador à distância.',
                'bonus': {'inteligencia': 3, 'energia': 3, 'forca': -2},
                'color': (80, 100, 200),
                'primary_stat': 'INTELIGÊNCIA',
                'secondary_stat': 'ENERGIA'
            },
            'necromante': {
                'name': 'NECROMANTE',
                'description': 'Manipulador das trevas com domínio sobre a vida e morte. Convoca aliados das sombras.',
                'bonus': {'inteligencia': 3, 'energia': 2, 'vitalidade': -1},
                'color': (100, 50, 150),
                'primary_stat': 'INTELIGÊNCIA',
                'secondary_stat': 'ENERGIA'
            }
        }
        
        self.buttons = []
        self.class_buttons = []
        self.attribute_controls = []
        self._create_ui()
        
    def _create_ui(self):
        """Cria toda a interface em uma única tela"""
        self.buttons.clear()
        self.class_buttons.clear()
        self.attribute_controls.clear()
        
        # Botões de ação principais
        cancel_btn = Button(
            ResponsiveUI.BASE_WIDTH // 2 - 320, 650, 300, 70,
            "CANCELAR", self._cancel_creation, 28
        )
        confirm_btn = Button(
            ResponsiveUI.BASE_WIDTH // 2 + 20, 650, 300, 70,
            "CONFIRMAR PERSONAGEM", self._confirm_character, 28
        )
        self.buttons.extend([cancel_btn, confirm_btn])
        
        # Botões das classes (lado esquerdo)
        class_button_width = 350
        class_button_height = 60
        start_y = 180
        
        for i, (class_key, class_data) in enumerate(self.classes.items()):
            y_pos = start_y + i * (class_button_height + 10)
            
            # Destacar classe selecionada
            is_selected = class_key == self.selected_class
            display_text = f"► {class_data['name']}" if is_selected else class_data['name']
            
            class_btn = Button(
                100, y_pos, class_button_width, class_button_height,
                display_text, 
                lambda c=class_key: self._select_class(c),
                26
            )
            self.class_buttons.append(class_btn)
        
        # Controles de atributos (lado direito)
        self._create_attribute_controls()
    
    def _create_attribute_controls(self):
        """Cria controles visuais para os atributos"""
        attribute_configs = [
            ('forca', 'FORÇA', 'Físico bruto e capacidade de carga', 300),
            ('destreza', 'DESTREZA', 'Agilidade, precisão e reflexos', 380),
            ('vitalidade', 'VITALIDADE', 'Saúde máxima e resistência', 460),
            ('inteligencia', 'INTELIGÊNCIA', 'Poder mágico e conhecimento', 540),
            ('armadura', 'ARMADURA', 'Defesa física e redução de dano', 300, 260),  # Segunda coluna
            ('energia', 'ENERGIA', 'Poder para habilidades especiais', 380, 260),
            ('stamina', 'STAMINA', 'Resistência para ações prolongadas', 460, 260)
        ]
        
        for config in attribute_configs:
            if len(config) == 4:
                attr_key, attr_name, attr_desc, y_pos = config
                x_offset = 0
            else:
                attr_key, attr_name, attr_desc, y_pos, x_offset = config
            
            x_pos = 800 + x_offset
            
            # Botão -
            minus_btn = Button(
                x_pos, y_pos, 50, 50,
                "－",  # Símbolo visualmente mais atraente
                lambda a=attr_key: self._adjust_attribute(a, -1),
                32
            )
            
            # Botão +
            plus_btn = Button(
                x_pos + 250, y_pos, 50, 50,
                "＋",  # Símbolo visualmente mais atraente
                lambda a=attr_key: self._adjust_attribute(a, 1),
                32
            )
            
            self.attribute_controls.append({
                'key': attr_key,
                'name': attr_name,
                'description': attr_desc,
                'x': x_pos,
                'y': y_pos,
                'minus_btn': minus_btn,
                'plus_btn': plus_btn
            })
    
    def _select_class(self, class_key):
        """Seleciona uma classe"""
        self.selected_class = class_key
        self._create_ui()  # Recria UI para atualizar seleção
    
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
            return
        
        # Calcula atributos finais com bônus da classe
        final_attributes = self.base_attributes.copy()
        if self.selected_class in self.classes:
            bonus = self.classes[self.selected_class]['bonus']
            for attr, value in bonus.items():
                final_attributes[attr] += value
        
        print(f"🎮 Personagem criado: {self.player_name} - {self.selected_class}")
        print(f"📊 Atributos: {final_attributes}")
        
        # TODO: Salvar personagem e iniciar jogo
        from src.states.menu_state import MenuState
        self.game.state_manager.change_state(MenuState(self.game))
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._cancel_creation()
            elif event.key == pygame.K_RETURN:
                self._confirm_character()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Processar cliques em todos os botões
            all_buttons = self.buttons + self.class_buttons
            for control in self.attribute_controls:
                all_buttons.append(control['minus_btn'])
                all_buttons.append(control['plus_btn'])
            
            ButtonManager.handle_button_click(all_buttons, event)
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        screen_size = self.game.screen.get_size()
        
        all_buttons = self.buttons + self.class_buttons
        for control in self.attribute_controls:
            all_buttons.append(control['minus_btn'])
            all_buttons.append(control['plus_btn'])
        
        ButtonManager.update_buttons(all_buttons, self.game)
    
    def render(self, surface):
        screen_width, screen_height = surface.get_size()
        
        # Fundo escuro elegante
        surface.fill((25, 25, 35))
        
        # Título principal
        self._render_title(surface, screen_width)
        
        # Painéis principais
        self._render_class_panel(surface)
        self._render_character_preview(surface)
        self._render_attributes_panel(surface)
        self._render_class_info(surface)
        
        # Botões
        all_buttons = self.buttons + self.class_buttons
        for control in self.attribute_controls:
            all_buttons.append(control['minus_btn'])
            all_buttons.append(control['plus_btn'])
        
        ButtonManager.render_buttons(all_buttons, surface, self.game.game_config)
    
    def _render_title(self, surface, screen_width):
        """Renderiza o título e informações gerais"""
        # Título principal
        title_font = self.game.game_config.get_font('title', 52)
        title_text = title_font.render("CRIAÇÃO DE PERSONAGEM", True, (255, 255, 255))
        surface.blit(title_text, (screen_width//2 - title_text.get_width()//2, 40))
        
        # Pontos disponíveis
        points_font = self.game.game_config.get_font('menu', 28)
        points_text = points_font.render(f"PONTOS DISPONÍVEIS: {self.available_points}", True, (100, 200, 255))
        surface.blit(points_text, (screen_width//2 - points_text.get_width()//2, 100))
        
        # Linha decorativa
        pygame.draw.line(surface, (80, 80, 100), (50, 130), (screen_width-50, 130), 2)
    
    def _render_class_panel(self, surface):
        """Renderiza o painel de seleção de classe"""
        # Título do painel
        panel_font = self.game.game_config.get_font('menu', 32)
        panel_title = panel_font.render("ESCOLHA SUA CLASSE", True, (255, 255, 255))
        surface.blit(panel_title, (100, 140))
        
        # Background do painel
        panel_rect = pygame.Rect(80, 170, 400, 450)
        pygame.draw.rect(surface, (40, 40, 50), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (80, 80, 100), panel_rect, 2, border_radius=12)
    
    def _render_character_preview(self, surface):
        """Renderiza a visualização do personagem"""
        if self.selected_class in self.classes:
            class_data = self.classes[self.selected_class]
            
            # Área de preview
            preview_rect = pygame.Rect(500, 150, 280, 280)
            pygame.draw.rect(surface, (30, 30, 40), preview_rect, border_radius=15)
            pygame.draw.rect(surface, class_data['color'], preview_rect, 3, border_radius=15)
            
            # Nome do personagem
            name_font = self.game.game_config.get_font('title', 36)
            name_text = name_font.render(self.player_name, True, (255, 255, 255))
            surface.blit(name_text, (500 + 140 - name_text.get_width()//2, 160))
            
            # Ícone da classe (placeholder - seria uma imagem)
            class_font = self.game.game_config.get_font('title', 24)
            class_text = class_font.render(class_data['name'], True, class_data['color'])
            surface.blit(class_text, (500 + 140 - class_text.get_width()//2, 440))
            
            # Desenhar um símbolo representativo da classe
            symbol_rect = pygame.Rect(500 + 90, 200, 100, 100)
            pygame.draw.rect(surface, class_data['color'], symbol_rect, border_radius=20)
            pygame.draw.rect(surface, (255, 255, 255), symbol_rect, 2, border_radius=20)
            
            # Símbolo textual temporário
            symbol_font = self.game.game_config.get_font('title', 48)
            symbols = {
                'barbaro': '⚔️',
                'paladino': '🛡️',
                'druida': '🌿',
                'feiticeiro': '🔮', 
                'necromante': '💀'
            }
            symbol = symbols.get(self.selected_class, '?')
            symbol_surface = symbol_font.render(symbol, True, (255, 255, 255))
            surface.blit(symbol_surface, (500 + 140 - symbol_surface.get_width()//2, 210))
    
    def _render_class_info(self, surface):
        """Renderiza informações detalhadas da classe selecionada"""
        if self.selected_class in self.classes:
            class_data = self.classes[self.selected_class]
            
            # Painel de informações
            info_rect = pygame.Rect(500, 450, 280, 180)
            pygame.draw.rect(surface, (40, 40, 50), info_rect, border_radius=12)
            pygame.draw.rect(surface, class_data['color'], info_rect, 2, border_radius=12)
            
            # Descrição
            desc_font = self.game.game_config.get_font('menu', 18)
            desc_lines = self._wrap_text(class_data['description'], desc_font, 260)
            for i, line in enumerate(desc_lines):
                desc_surface = desc_font.render(line, True, (200, 200, 200))
                surface.blit(desc_surface, (510, 470 + i * 25))
            
            # Estatísticas principais
            stats_font = self.game.game_config.get_font('menu', 20)
            primary_stat = stats_font.render(f"Principal: {class_data['primary_stat']}", True, class_data['color'])
            secondary_stat = stats_font.render(f"Secundária: {class_data['secondary_stat']}", True, (180, 180, 180))
            
            surface.blit(primary_stat, (510, 520))
            surface.blit(secondary_stat, (510, 550))
    
    def _render_attributes_panel(self, surface):
        """Renderiza o painel de atributos com design melhorado"""
        # Título do painel
        panel_font = self.game.game_config.get_font('menu', 32)
        panel_title = panel_font.render("ATRIBUTOS", True, (255, 255, 255))
        surface.blit(panel_title, (800, 140))
        
        # Background do painel
        panel_rect = pygame.Rect(780, 170, 500, 460)
        pygame.draw.rect(surface, (40, 40, 50), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (80, 80, 100), panel_rect, 2, border_radius=12)
        
        # Renderizar cada atributo
        for control in self.attribute_controls:
            self._render_attribute(surface, control)
    
    def _render_attribute(self, surface, control):
        """Renderiza um atributo individual com design aprimorado"""
        attr_value = self.base_attributes[control['key']]
        
        # Nome do atributo
        name_font = self.game.game_config.get_font('menu', 22)
        name_surface = name_font.render(control['name'], True, (255, 255, 255))
        surface.blit(name_surface, (control['x'] + 60, control['y']))
        
        # Descrição do atributo
        desc_font = self.game.game_config.get_font('menu', 16)
        desc_surface = desc_font.render(control['description'], True, (150, 150, 150))
        surface.blit(desc_surface, (control['x'] + 60, control['y'] + 25))
        
        # Display do valor (CAIXA DESTACADA)
        value_rect = pygame.Rect(control['x'] + 120, control['y'], 80, 50)
        pygame.draw.rect(surface, (30, 30, 40), value_rect, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 100), value_rect, 2, border_radius=8)
        
        # Valor numérico (grande e centralizado)
        value_font = self.game.game_config.get_font('title', 28)
        value_surface = value_font.render(str(attr_value), True, (255, 255, 255))
        surface.blit(value_surface, (
            control['x'] + 120 + 40 - value_surface.get_width()//2,
            control['y'] + 25 - value_surface.get_height()//2
        ))
    
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
    
    def enter(self):
        print("🎭 Entrando na criação de personagem")
    
    def exit(self):
        print("🎭 Saindo da criação de personagem")