import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.menu_assets import load_menu_visual_assets, render_menu_background


class GameSlotSelectState(BaseState):
    """Tela de seleção de slot de jogo (5 slots disponíveis)"""

    def __init__(self, game):
        super().__init__(game)
        self.game_slots = []
        self.buttons = []
        self.slot_action_buttons = {}
        self.confirm_delete_slot = None
        self.confirm_button = None

        # Carrega assets visuais do menu
        self.menu_assets = load_menu_visual_assets(game)

        # LAYOUT RELATIVO (Porcentagens da Base 1920x1080)
        # Isso garante que o layout se mantenha proporcional
        self.base_w = self.theme.BASE_WIDTH
        self.base_h = self.theme.BASE_HEIGHT

        self.slot_width_pct = 0.28  # 28% da largura (aprox 540px)
        self.slot_height_pct = 0.24  # 24% da altura (aprox 260px)
        self.spacing_x_pct = 0.03  # 3% de espaçamento
        self.spacing_y_pct = 0.04  # 4% de espaçamento vertical

        self._load_game_slots()
        self._create_ui()

    def _load_game_slots(self):
        """Carrega informações dos 5 slots de jogo"""
        self.game_slots.clear()
        try:
            cursor = self.game.game_config.database.connection.cursor()
            cursor.execute("SELECT * FROM game_slots ORDER BY slot_id")
            slots_data = cursor.fetchall()

            if not slots_data or len(slots_data) == 0:
                self._initialize_empty_slots()
                return

            for row in slots_data:
                self.game_slots.append(dict(row))

        except Exception as e:
            print(f"❌ Erro ao carregar slots de jogo: {e}")
            self._initialize_empty_slots()

    def _initialize_empty_slots(self):
        """Inicializa 5 slots vazios"""
        try:
            cursor = self.game.game_config.database.connection.cursor()
            for i in range(1, 6):
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO game_slots (slot_id, player_name, is_active)
                    VALUES (?, NULL, 0)
                    """,
                    (i,),
                )
            self.game.game_config.database.connection.commit()
            self._load_game_slots()
        except Exception as e:
            print(f"❌ Erro ao inicializar slots: {e}")

    def _create_ui(self):
        """Cria os botões da interface usando layout relativo"""
        self.buttons.clear()
        self.slot_action_buttons.clear()

        # Dimensões calculadas
        slot_w = int(self.base_w * self.slot_width_pct)
        slot_h = int(self.base_h * self.slot_height_pct)
        spacing_x = int(self.base_w * self.spacing_x_pct)
        spacing_y = int(self.base_h * self.spacing_y_pct)

        # Ponto inicial (centralizado horizontalmente para 2 colunas)
        # Largura total de 2 colunas = 2*w + spacing
        total_grid_w = (2 * slot_w) + spacing_x
        start_x = (self.base_w - total_grid_w) // 2
        start_y = int(self.base_h * 0.20)  # Começa em 20% da altura

        # Botão Voltar (Canto inferior esquerdo)
        back_btn = Button(
            int(self.base_w * 0.05),  # 5% da esquerda
            int(self.base_h * 0.90),  # 90% do topo
            200,
            60,
            "VOLTAR",
            self._back_to_menu,
            font_size=self.theme.FONT_MENU_MEDIUM,
            text_color=(255, 255, 255),
            button_image_normal=self.menu_assets["button_normal"],
            button_image_pressed=self.menu_assets["button_pressed"],
        )
        self.buttons.append(back_btn)

        # Criar botões de ação para cada slot
        for i, slot in enumerate(self.game_slots):
            slot_id = slot["slot_id"]
            is_empty = not slot["player_name"]

            # Grid 2 colunas
            col = i % 2
            row = i // 2

            base_x = start_x + col * (slot_w + spacing_x)
            base_y = start_y + row * (slot_h + spacing_y)

            # Botões posicionados RELATIVAMENTE ao fundo do card
            # 15% da altura do card a partir do fundo
            btn_margin_bottom = int(slot_h * 0.25)
            btn_y = base_y + slot_h - btn_margin_bottom

            if is_empty:
                # Botão CRIAR JOGO (Centralizado no botão area)
                btn_w = 200
                btn_x = base_x + (slot_w - btn_w) // 2

                create_btn = Button(
                    btn_x,
                    btn_y,
                    btn_w,
                    40,
                    "CRIAR JOGO",
                    lambda sid=slot_id: self._create_new_game(sid),
                    font_size=self.theme.FONT_MENU_SMALL,
                    text_color=(255, 255, 255),
                    button_image_normal=self.menu_assets["button_normal"],
                    button_image_pressed=self.menu_assets["button_pressed"],
                )
                self.slot_action_buttons[slot_id] = {"create": create_btn}
            else:
                # Botões CARREGAR e DELETAR (Espalhados)
                btn_w = 140
                # Margem lateral interna de 10%
                margin_side = int(slot_w * 0.05)

                load_btn = Button(
                    base_x + margin_side,
                    btn_y,
                    btn_w,
                    40,
                    "CARREGAR",
                    lambda sid=slot_id: self._load_game_slot(sid),
                    font_size=self.theme.FONT_MENU_SMALL,
                    text_color=(255, 255, 255),
                    button_image_normal=self.menu_assets["button_normal"],
                    button_image_pressed=self.menu_assets["button_pressed"],
                )

                delete_btn = Button(
                    base_x + slot_w - btn_w - margin_side,
                    btn_y,
                    btn_w,
                    40,
                    "DELETAR",
                    lambda sid=slot_id: self._delete_game(sid),
                    font_size=self.theme.FONT_MENU_SMALL,
                    text_color=(255, 255, 255),
                    button_image_normal=self.menu_assets["button_normal"],
                    button_image_pressed=self.menu_assets["button_pressed"],
                )
                self.slot_action_buttons[slot_id] = {
                    "load": load_btn,
                    "delete": delete_btn,
                }

    # ==================== ACTION METHODS ====================

    def _back_to_menu(self):
        """Volta para o menu principal"""
        from src.states.menu_state import MenuState

        self.game.state_manager.change_state(MenuState(self.game))

    def _create_new_game(self, slot_id):
        """Inicia criação de novo jogo no slot especificado"""
        print(f"🎮 Criando novo jogo no slot {slot_id}")
        from src.states.character_creation_state import CharacterCreationState

        self.game.state_manager.change_state(CharacterCreationState(self.game, slot_id))

    def _load_game_slot(self, slot_id):
        """Carrega jogo do slot especificado"""
        print(f"🎮 Carregando jogo do slot {slot_id}")

        # Busca dados do herói
        hero_data = self.game.hero_manager.get_hero_by_slot(slot_id)

        if hero_data:
            # Define como herói atual
            self.game.hero_manager.set_current_hero(hero_data)

            # Inicia o jogo
            from src.states.game_state import GameState

            self.game.state_manager.change_state(GameState(self.game, hero_data))
        else:
            print(f"❌ Erro: Dados do herói não encontrados para o slot {slot_id}")

    def _delete_game(self, slot_id):
        """Inicia processo de deletar jogo"""
        print(f"🗑️ Solicitando deleção do slot {slot_id}")
        self.confirm_delete_slot = slot_id

        # Cria botão de confirmação
        btn_w = 200
        btn_h = 50
        center_x = self.theme.BASE_WIDTH // 2
        center_y = self.theme.BASE_HEIGHT // 2 + 100

        self.confirm_button = Button(
            center_x - btn_w // 2,
            center_y,
            btn_w,
            btn_h,
            "CONFIRMAR",
            self._confirm_delete_action,
            font_size=self.theme.FONT_MENU_SMALL,
            text_color=self.theme.COLOR_TEXT_WARNING,
            button_image_normal=self.menu_assets["button_normal"],
            button_image_pressed=self.menu_assets["button_pressed"],
        )

    def _confirm_delete_action(self):
        """Executa a deleção após confirmação"""
        if self.confirm_delete_slot:
            slot_id = self.confirm_delete_slot
            print(f"🗑️ Confirmado: Deletando slot {slot_id}")

            try:
                cursor = self.game.game_config.database.connection.cursor()

                # Limpa dados do slot
                cursor.execute(
                    """
                    UPDATE game_slots 
                    SET player_name = NULL, 
                        player_class = NULL, 
                        player_level = 1, 
                        is_active = 0,
                        playtime = 0,
                        last_played = NULL
                    WHERE slot_id = ?
                """,
                    (slot_id,),
                )

                # Remove herói associado (se houver tabela separada, mas parece que é tudo no game_slots por enquanto ou gerenciado pelo hero_manager)
                # Se houver tabela de herois separada, deveria ser limpa aqui também.
                # Assumindo que game_slots é a principal por enquanto ou que o reset basta.

                self.game.game_config.database.connection.commit()
                print("✅ Slot resetado com sucesso")

                # Recarrega UI
                self.confirm_delete_slot = None
                self.confirm_button = None
                self._load_game_slots()
                self._create_ui()

            except Exception as e:
                print(f"❌ Erro ao deletar slot: {e}")

    def enter(self):
        """Chamado ao entrar no estado"""
        print("🎮 Entrando na seleção de slots de jogo")

    def exit(self):
        """Chamado ao sair do estado"""
        print("🎮 Saindo da seleção de slots de jogo")

    def on_resize(self, old_size, new_size):
        """Recria a UI ao redimensionar"""
        self._create_ui()

    def update(self):
        """Atualiza o estado (required by BaseState)"""
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos, dt=1.0 / 60.0)

        # Update slot action buttons
        for slot_id, buttons_dict in self.slot_action_buttons.items():
            for btn in buttons_dict.values():
                if btn:
                    btn.update(mouse_pos, dt=1.0 / 60.0)

        # Update confirm button if exists
        if self.confirm_button:
            self.confirm_button.update(mouse_pos, dt=1.0 / 60.0)

    def handle_event(self, event):
        """Processa eventos (required by BaseState)"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.state_manager.pop_state()
                return

        # Handle button events
        for button in self.buttons:
            button.handle_event(event)

        # Handle slot action button events
        for slot_id, buttons_dict in self.slot_action_buttons.items():
            for btn in buttons_dict.values():
                if btn:
                    btn.handle_event(event)

        # Handle confirm button event
        if self.confirm_button:
            self.confirm_button.handle_event(event)

    def render(self, surface, world_surface=None):
        """Renderiza o estado"""
        # Desenha fundo
        render_menu_background(surface, self.menu_assets["background"], self.theme)

        # Título
        title_font = self.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            "SELECIONE SEU JOGO", True, self.theme.COLOR_TEXT_PRIMARY
        )
        title_y = self.ui_scaler.scale(80, "y")
        surface.blit(
            title_text,
            (surface.get_width() // 2 - title_text.get_width() // 2, title_y),
        )

        # Renderiza slots
        self._render_slots(surface)

        # Renderiza botões principais
        for btn in self.buttons:
            btn.render(surface)

        # Renderiza botões dos slots
        for buttons in self.slot_action_buttons.values():
            for btn in buttons.values():
                if btn:
                    btn.render(surface)

        # Renderiza modal de confirmação
        if self.confirm_button:
            self._render_confirm_modal(surface)

    def _render_slots(self, surface):
        """Renderiza os cards dos slots"""
        slot_w = int(self.base_w * self.slot_width_pct)
        slot_h = int(self.base_h * self.slot_height_pct)
        spacing_x = int(self.base_w * self.spacing_x_pct)
        spacing_y = int(self.base_h * self.spacing_y_pct)

        total_grid_w = (2 * slot_w) + spacing_x
        start_x = (self.base_w - total_grid_w) // 2
        start_y = int(self.base_h * 0.20)

        for i, slot in enumerate(self.game_slots):
            col = i % 2
            row = i // 2

            base_x = start_x + col * (slot_w + spacing_x)
            base_y = start_y + row * (slot_h + spacing_y)

            slot_rect = self.ui_scaler.rect(base_x, base_y, slot_w, slot_h)

            # Fundo do slot
            is_empty = not slot["player_name"]
            color = (40, 40, 50) if is_empty else (60, 70, 80)
            border_color = (
                self.theme.COLOR_BORDER_DEFAULT
                if is_empty
                else self.theme.COLOR_BORDER_ACTIVE
            )

            pygame.draw.rect(surface, color, slot_rect, border_radius=15)
            pygame.draw.rect(surface, border_color, slot_rect, 2, border_radius=15)

            # Info do slot
            if not is_empty:
                info_font = self.ui_scaler.get_themed_font("menu")
                name_text = info_font.render(
                    f"{slot['player_name']}", True, self.theme.COLOR_TEXT_PRIMARY
                )
                surface.blit(name_text, (slot_rect.x + 20, slot_rect.y + 20))

                details_font = self.ui_scaler.get_themed_font("menu_small")
                level_text = details_font.render(
                    f"Nível {slot.get('player_level', 1)} - {slot.get('player_class', 'Aventureiro')}",
                    True,
                    self.theme.COLOR_TEXT_SECONDARY,
                )
                surface.blit(level_text, (slot_rect.x + 20, slot_rect.y + 60))
            else:
                empty_font = self.ui_scaler.get_themed_font("menu")
                empty_text = empty_font.render(
                    "Vazio", True, self.theme.COLOR_TEXT_HINT
                )
                surface.blit(
                    empty_text,
                    (
                        slot_rect.centerx - empty_text.get_width() // 2,
                        slot_rect.centery - empty_text.get_height() // 2 - 20,
                    ),
                )

            # Número do slot
            slot_num_font = self.ui_scaler.get_themed_font("menu_small")
            slot_num_text = slot_num_font.render(
                f"Slot {slot['slot_id']}", True, self.theme.COLOR_TEXT_HINT
            )
            surface.blit(
                slot_num_text,
                (slot_rect.right - slot_num_text.get_width() - 15, slot_rect.top + 10),
            )

    def _render_confirm_modal(self, surface):
        """Renderiza o modal de confirmação"""
        # Overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Box
        box_w = 600
        box_h = 300
        box_x = (self.theme.BASE_WIDTH - box_w) // 2
        box_y = (self.theme.BASE_HEIGHT - box_h) // 2

        box_rect = self.ui_scaler.rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(surface, self.theme.COLOR_BG_MODAL, box_rect, border_radius=20)
        pygame.draw.rect(
            surface, self.theme.COLOR_BORDER_WARNING, box_rect, 3, border_radius=20
        )

        # Texto
        title_font = self.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            "CONFIRMAR EXCLUSÃO", True, self.theme.COLOR_TEXT_WARNING
        )
        surface.blit(
            title_text,
            (box_rect.centerx - title_text.get_width() // 2, box_rect.y + 30),
        )

        msg_font = self.ui_scaler.get_themed_font("menu")
        msg_text = msg_font.render(
            "Tem certeza que deseja deletar este save?",
            True,
            self.theme.COLOR_TEXT_PRIMARY,
        )
        surface.blit(
            msg_text, (box_rect.centerx - msg_text.get_width() // 2, box_rect.y + 100)
        )

        warn_font = self.ui_scaler.get_themed_font("menu_small")
        warn_text = warn_font.render(
            "Esta ação não pode ser desfeita.", True, self.theme.COLOR_BUTTON_DANGER
        )
        surface.blit(
            warn_text, (box_rect.centerx - warn_text.get_width() // 2, box_rect.y + 150)
        )

        if self.confirm_button:
            self.confirm_button.render(surface)
