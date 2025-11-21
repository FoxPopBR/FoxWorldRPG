# src/states/game_slot_select_state.py
import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager


class GameSlotSelectState(BaseState):
    """Tela de seleção de slot de jogo (5 slots disponíveis)"""

    def __init__(self, game):
        super().__init__(game)
        self.game_slots = []
        self.buttons = []
        self.slot_action_buttons = (
            {}
        )  # Dicionário para armazenar botões de ação por slot
        self.confirm_delete_slot = None  # Slot aguardando confirmação de exclusão
        self.confirm_button = None  # Botão de confirmação no modal
        self._load_game_slots()
        self._create_ui()

    def _load_game_slots(self):
        """Carrega informações dos 5 slots de jogo"""
        self.game_slots.clear()  # Limpa lista para evitar duplicatas
        try:
            cursor = self.game.game_config.database.connection.cursor()
            cursor.execute("SELECT * FROM game_slots ORDER BY slot_id")
            slots_data = cursor.fetchall()

            if not slots_data or len(slots_data) == 0:
                # Se não existem slots, cria os 5 vazios
                self._initialize_empty_slots()
                return

            # Converte para lista de dicts
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

            # Recarrega os slots
            cursor.execute("SELECT * FROM game_slots ORDER BY slot_id")
            slots_data = cursor.fetchall()
            self.game_slots = [dict(row) for row in slots_data]

        except Exception as e:
            print(f"❌ Erro ao inicializar slots: {e}")
            # Fallback para slots em memória
            self.game_slots = [
                {"slot_id": i, "player_name": None, "is_active": 0} for i in range(1, 6)
            ]

    def _create_ui(self):
        """Cria interface de seleção de slots"""
        self.buttons.clear()
        self.slot_action_buttons.clear()

        # Botão Voltar (usa posições base)
        back_btn = Button(100, 980, 200, 60, "VOLTAR", self._back_to_menu, 24)
        self.buttons.append(back_btn)

        # Parâmetros dos slots (valores base para 1920x1080)
        base_slot_width = 550
        base_slot_height = 260
        base_spacing_x = 60
        base_spacing_y = 60

        # Calcula posições base (ResponsiveUI fará o scaling automaticamente)
        # Primeira linha: 3 slots
        base_start_x_row1 = (1920 - (base_slot_width * 3 + base_spacing_x * 2)) // 2
        base_start_y_row1 = 250

        # Segunda linha: 2 slots (centralizados)
        base_start_x_row2 = (1920 - (base_slot_width * 2 + base_spacing_x)) // 2
        base_start_y_row2 = base_start_y_row1 + base_slot_height + base_spacing_y

        # Armazena as posições base
        self.base_positions = [
            (base_start_x_row1, base_start_y_row1),  # Slot 1
            (
                base_start_x_row1 + base_slot_width + base_spacing_x,
                base_start_y_row1,
            ),  # Slot 2
            (
                base_start_x_row1 + (base_slot_width + base_spacing_x) * 2,
                base_start_y_row1,
            ),  # Slot 3
            (base_start_x_row2, base_start_y_row2),  # Slot 4
            (
                base_start_x_row2 + base_slot_width + base_spacing_x,
                base_start_y_row2,
            ),  # Slot 5
        ]

        self.base_slot_width = base_slot_width
        self.base_slot_height = base_slot_height

        # Cria botões de ação para cada slot
        for i, (base_x, base_y) in enumerate(self.base_positions):
            slot_id = i + 1
            slot = self.game_slots[i]
            is_empty = not slot["player_name"]

            # Armazena botões deste slot
            self.slot_action_buttons[slot_id] = []

            if is_empty:
                # Slot vazio: Botão CRIAR JOGO (centralizado)
                create_btn = Button(
                    base_x + base_slot_width // 2 - 100,
                    base_y + base_slot_height - 50,
                    200,
                    40,
                    "CRIAR JOGO",
                    lambda sid=slot_id: self._create_new_game(sid),
                    20,
                )
                self.slot_action_buttons[slot_id].append(create_btn)
            else:
                # Slot ocupado: Botões CARREGAR e DELETAR
                load_btn = Button(
                    base_x + 20,
                    base_y + base_slot_height - 50,
                    240,
                    40,
                    "CARREGAR SAVE",
                    lambda sid=slot_id: self._load_game_slot(sid),
                    18,
                )
                delete_btn = Button(
                    base_x + base_slot_width - 260,
                    base_y + base_slot_height - 50,
                    240,
                    40,
                    "DELETAR SLOT",
                    lambda sid=slot_id: self._confirm_delete_slot(sid),
                    18,
                )
                self.slot_action_buttons[slot_id].extend([load_btn, delete_btn])

    def _create_new_game(self, slot_id):
        """Inicia criação de novo jogo no slot selecionado"""
        self.game.selected_game_slot = slot_id
        self.game.notification_manager.add_notification(
            f"Criando novo jogo no slot {slot_id}", (100, 255, 100)
        )

        from src.states.character_creation_state import CharacterCreationState

        self.game.state_manager.change_state(CharacterCreationState(self.game))

    def _load_game_slot(self, slot_id):
        """Carrega o último save do slot (vai para tela de saves)"""
        self.game.selected_game_slot = slot_id
        self.game.notification_manager.add_notification(
            f"Carregando saves do slot {slot_id}...", (100, 255, 100)
        )

        from src.states.save_select_state import SaveSelectState

        self.game.state_manager.change_state(SaveSelectState(self.game))

    def _confirm_delete_slot(self, slot_id):
        """Confirma exclusão do slot"""
        if self.confirm_delete_slot == slot_id:
            # Já está mostrando o modal
            pass
        else:
            # Primeira vez - pede confirmação
            self.confirm_delete_slot = slot_id

            # Cria botão de confirmação (posições base - ResponsiveUI escalará)
            base_box_width = 600
            base_box_height = 200
            base_box_x = (1920 - base_box_width) // 2
            base_box_y = (1080 - base_box_height) // 2

            self.confirm_button = Button(
                base_box_x + base_box_width // 2 - 100,
                base_box_y + 130,
                200,
                40,
                "CONFIRMAR",
                lambda: self._delete_game_slot(slot_id),
                20,
                text_color=(255, 255, 255),
                bg_color=(200, 50, 50),
                hover_color=(255, 80, 80),
            )

            self.game.notification_manager.add_notification(
                f"Confirme a exclusão do Slot {slot_id}", (255, 100, 100)
            )

    def _delete_game_slot(self, slot_id):
        """Deleta um slot de jogo e todos os seus saves"""
        try:
            cursor = self.game.game_config.database.connection.cursor()

            # Primeiro, obtém o nome do jogador para deletar saves
            cursor.execute(
                "SELECT player_name FROM game_slots WHERE slot_id = ?", (slot_id,)
            )
            result = cursor.fetchone()

            if result:
                # Deleta saves associados
                cursor.execute(
                    "DELETE FROM save_slots WHERE game_slot_id = ?", (slot_id,)
                )

                # Limpa o slot (não deleta, apenas reseta)
                cursor.execute(
                    """
                    UPDATE game_slots 
                    SET player_name = NULL,
                        player_class = NULL,
                        player_level = 1,
                        zone_name = 'Início',
                        playtime = 0,
                        is_active = 0
                    WHERE slot_id = ?
                    """,
                    (slot_id,),
                )

                self.game.game_config.database.connection.commit()
                self.game.notification_manager.add_notification(
                    f"Slot {slot_id} deletado com sucesso", (100, 255, 100)
                )

        except Exception as e:
            self.game.notification_manager.add_notification(
                f"Erro ao deletar slot: {e}", (255, 50, 50)
            )
            print(f"❌ Erro ao deletar slot {slot_id}: {e}")

    def _back_to_menu(self):
        """Volta ao menu principal"""
        from src.states.menu_state import MenuState

        self.game.state_manager.change_state(MenuState(self.game))

    def handle_event(self, event):
        """Processa eventos"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back_to_menu()
                self.confirm_delete_slot = None  # Cancela confirmação
                self.confirm_button = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Se modal de confirmação estiver aberto, só verifica ele
            if self.confirm_delete_slot and self.confirm_button:
                if self.confirm_button.is_hovered(event.pos, self.game):
                    self.confirm_button.on_click()

            # Verifica clique nos botões de ação dos slots
            for slot_id, action_buttons in self.slot_action_buttons.items():
                for btn in action_buttons:
                    if btn.is_hovered(event.pos, self.game):
                        btn.on_click()
                        return

    def update(self):
        """Atualiza o estado"""
        if self.confirm_delete_slot and self.confirm_button:
            mouse_pos = pygame.mouse.get_pos()
            self.confirm_button.update(mouse_pos, self.game)
            return

        ButtonManager.update_buttons(self.buttons, self.game)

        # Atualiza botões de ação dos slots

        # Overlay semi-transparente (usa tamanho atual da tela)
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

        # Caixa de confirmação (posições base)
        base_box_width = 600
        base_box_height = 200
        base_box_x = (1920 - base_box_width) // 2
        base_box_y = (1080 - base_box_height) // 2

        # Escala a caixa
        box_rect = ResponsiveUI.scale_rect(
            base_box_x,
            base_box_y,
            base_box_width,
            base_box_height,
            screen_width,
            screen_height,
        )

        pygame.draw.rect(
            surface,
            (40, 40, 50),
            box_rect,
            border_radius=20,
        )
        pygame.draw.rect(
            surface,
            (255, 100, 100),
            box_rect,
            3,
            border_radius=20,
        )

        # Texto de confirmação (escalado)
        title_font_size = ResponsiveUI.scale_font_size(36, screen_width, screen_height)
        title_font = self.game.game_config.get_font("title", title_font_size)
        title_text = title_font.render("⚠️ CONFIRMAÇÃO", True, (255, 100, 100))
        title_y = box_rect.y + ResponsiveUI.scale_value(30, screen_width, screen_height)
        surface.blit(
            title_text,
            (box_rect.centerx - title_text.get_width() // 2, title_y),
        )

        msg_font_size = ResponsiveUI.scale_font_size(24, screen_width, screen_height)
        msg_font = self.game.game_config.get_font("menu", msg_font_size)
        msg_text = msg_font.render(
            f"Deletar SLOT {self.confirm_delete_slot}?", True, (255, 255, 255)
        )
        msg_y = box_rect.y + ResponsiveUI.scale_value(90, screen_width, screen_height)
        surface.blit(msg_text, (box_rect.centerx - msg_text.get_width() // 2, msg_y))

        hint_font_size = ResponsiveUI.scale_font_size(20, screen_width, screen_height)
        hint_font = self.game.game_config.get_font("menu", hint_font_size)

        hint2_text = hint_font.render(
            "Pressione ESC para cancelar", True, (150, 150, 150)
        )
        hint2_y = box_rect.y + ResponsiveUI.scale_value(
            175, screen_width, screen_height
        )
        surface.blit(
            hint2_text,
            (box_rect.centerx - hint2_text.get_width() // 2, hint2_y),
        )

    def enter(self):
        """Chamado ao entrar no estado"""
        print("🎮 Entrando na seleção de slots de jogo")

    def exit(self):
        """Chamado ao sair do estado"""
        print("🎮 Saindo da seleção de slots de jogo")

    def on_resize(self, old_size, new_size):
        """Recria a UI ao redimensionar"""
        self._create_ui()
