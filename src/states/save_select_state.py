# src/states/save_select_state.py
import pygame
from datetime import datetime
from src.states.base_state import BaseState
from src.ui.button import Button


class SaveSelectState(BaseState):
    """Tela de seleção de slot de save (3 saves por slot de jogo) - REFATORADO UIScaler"""

    def __init__(self, game):
        super().__init__(game)
        self.game_slot_id = getattr(game, "selected_game_slot", 1)
        self.slots = []
        self.buttons = []
        self.slot_action_buttons = {}
        self.confirm_delete_slot = None
        self.confirm_button = None

        # Diagramming base para 1920x1080 (UIScaler escala automaticamente)
        self.base_slot_width = 500
        # Diagramming base para 1920x1080 (UIScaler escala automaticamente)
        self.base_slot_width = 500
        # AJUSTADO para 300 (equilíbrio entre 1080p e 720p)
        self.base_slot_height = 300
        self.base_spacing = 50
        self.base_start_y = 350

        self._load_save_slots()
        self._create_ui()

    def _load_save_slots(self):
        """Carrega informações dos 3 slots de save do slot de jogo selecionado"""
        try:
            cursor = self.game.game_config.database.connection.cursor()
            cursor.execute(
                """
                SELECT * FROM save_slots 
                WHERE game_slot_id = ? 
                ORDER BY save_slot_id
                """,
                (self.game_slot_id,),
            )
            slots_data = cursor.fetchall()

            if not slots_data or len(slots_data) == 0:
                print(
                    f"⚠️ Nenhum save encontrado para o slot de jogo {self.game_slot_id}"
                )
                self._initialize_empty_slots()
                return

            self.slots = [dict(row) for row in slots_data]

        except Exception as e:
            print(f"❌ Erro ao carregar slots de save: {e}")
            self._initialize_empty_slots()

    def _initialize_empty_slots(self):
        """Inicializa 3 slots vazios"""
        self.slots = [
            {
                "save_slot_id": 1,
                "slot_type": "auto",
                "hero_name": None,
                "save_title": "Auto Save",
            },
            {
                "save_slot_id": 2,
                "slot_type": "manual",
                "hero_name": None,
                "save_title": "Save Manual 1",
            },
            {
                "save_slot_id": 3,
                "slot_type": "manual",
                "hero_name": None,
                "save_title": "Save Manual 2",
            },
        ]

    def _create_ui(self):
        """Cria interface de seleção de saves"""
        self.buttons.clear()
        self.slot_action_buttons.clear()

        # Botão Voltar (posição base)
        back_btn = Button(
            100,
            980,
            200,
            60,
            "VOLTAR",
            self._back_to_slots,
            font_size=self.theme.FONT_MENU_MEDIUM,
        )
        self.buttons.append(back_btn)

        # Calcula posição centralizada dos slots
        total_width = self.base_slot_width * 3 + self.base_spacing * 2
        base_start_x = (self.theme.BASE_WIDTH - total_width) // 2

        # Cria botões  de ação para cada slot
        for i in range(3):
            save_slot_id = i + 1
            slot = self.slots[i]
            base_x = base_start_x + i * (self.base_slot_width + self.base_spacing)
            is_empty = not slot.get("hero_name")
            self.slot_action_buttons[save_slot_id] = []

            if not is_empty:
                # Save ocupado: Botões CARREGAR e DELETAR
                # Botões posicionados no fundo do card (offset 70)
                btn_y = self.base_start_y + self.base_slot_height - 70

                load_btn = Button(
                    base_x + 20,
                    btn_y,
                    220,
                    40,
                    "CARREGAR SAVE",
                    lambda sid=save_slot_id: self._load_save(sid),
                    font_size=self.theme.FONT_MENU_SMALL,
                )
                delete_btn = Button(
                    base_x + self.base_slot_width - 240,
                    btn_y,
                    220,
                    40,
                    "DELETAR SAVE",
                    lambda sid=save_slot_id: self._confirm_delete_save(sid),
                    font_size=self.theme.FONT_MENU_SMALL,
                    bg_color=self.theme.COLOR_BUTTON_DANGER,
                    hover_color=self.theme.COLOR_BUTTON_DANGER_HOVER,
                )
                self.slot_action_buttons[save_slot_id].extend([load_btn, delete_btn])

    def _load_save(self, save_slot_id):
        """Carrega um save específico"""
        if save_slot_id > len(self.slots):
            self.game.notification_manager.add_notification(
                f"Slot {save_slot_id} inválido", (255, 50, 50)
            )
            return

        slot = self.slots[save_slot_id - 1]

        if not slot.get("hero_name"):
            self.game.notification_manager.add_notification(
                f"Slot {save_slot_id} vazio", (255, 200, 100)
            )
            return

        # Carrega o herói do slot
        hero = self.game.game_config.hero_manager.get_hero(slot["hero_name"])
        if hero:
            self.game.game_config.hero_manager.set_current_hero(hero)
            self.game.notification_manager.add_notification(
                f"Carregando save: {hero.name}...", (100, 255, 100)
            )

            from src.states.game_state import GameState

            self.game.state_manager.change_state(GameState(self.game))
        else:
            self.game.notification_manager.add_notification(
                f"Herói {slot['hero_name']} não encontrado", (255, 50, 50)
            )

    def _confirm_delete_save(self, save_slot_id):
        """Confirma exclusão do save"""
        if self.confirm_delete_slot != save_slot_id:
            self.confirm_delete_slot = save_slot_id

            # Cria botão de confirmação (posição base)
            base_box_x = (self.theme.BASE_WIDTH - self.theme.MODAL_WIDTH) // 2
            base_box_y = (self.theme.BASE_HEIGHT - 200) // 2

            self.confirm_button = Button(
                base_box_x + self.theme.MODAL_WIDTH // 2 - 100,
                base_box_y + 130,
                200,
                40,
                "CONFIRMAR",
                lambda: self._delete_save(save_slot_id),
                font_size=self.theme.FONT_MENU_SMALL,
                bg_color=self.theme.COLOR_BUTTON_DANGER,
                hover_color=self.theme.COLOR_BUTTON_DANGER_HOVER,
            )

            self.game.notification_manager.add_notification(
                "Confirme a exclusão", (255, 100, 100)
            )

    def _delete_save(self, save_slot_id):
        """Deleta um save específico"""
        try:
            cursor = self.game.game_config.database.connection.cursor()
            cursor.execute(
                """
                UPDATE save_slots 
                SET hero_name = NULL, hero_level = 1, hero_class = NULL,
                    zone_name = 'Início', zone_id = 1, playtime = 0,
                    save_description = '', is_active = 0
                WHERE game_slot_id = ? AND save_slot_id = ?
                """,
                (self.game_slot_id, save_slot_id),
            )

            self.game.game_config.database.connection.commit()
            self.game.notification_manager.add_notification(
                f"Save {save_slot_id} deletado com sucesso", (100, 255, 100)
            )

            self.confirm_delete_slot = None
            self.confirm_button = None
            self._load_save_slots()
            self._create_ui()

        except Exception as e:
            self.game.notification_manager.add_notification(
                f"Erro ao deletar save: {e}", (255, 50, 50)
            )
            print(f"❌ Erro ao deletar save {save_slot_id}: {e}")

    def _back_to_slots(self):
        """Volta para seleção de slots de jogo"""
        from src.states.game_slot_select_state import GameSlotSelectState

        self.game.state_manager.change_state(GameSlotSelectState(self.game))

    def handle_event(self, event):
        """Processa eventos"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.confirm_delete_slot:
                    self.confirm_delete_slot = None
                    self.confirm_button = None
                else:
                    self._back_to_slots()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Modal de confirmação tem prioridade
            if self.confirm_button:
                if self.confirm_button.handle_event(event):
                    return
                # Clicar fora cancela
                modal_rect = self.ui_scaler.rect(
                    (self.theme.BASE_WIDTH - self.theme.MODAL_WIDTH) // 2,
                    (self.theme.BASE_HEIGHT - 200) // 2,
                    self.theme.MODAL_WIDTH,
                    200,
                )
                if not modal_rect.collidepoint(event.pos):
                    self.confirm_delete_slot = None
                    self.confirm_button = None
                return

            # Botões de ação dos slots
            for buttons in self.slot_action_buttons.values():
                for btn in buttons:
                    if btn.handle_event(event):
                        return

            # Botões principais
            for btn in self.buttons:
                if btn.handle_event(event):
                    return

    def update(self):
        """Atualiza o estado"""
        mouse_pos = pygame.mouse.get_pos()

        if self.confirm_button:
            self.confirm_button.update(mouse_pos)
            return

        for btn in self.buttons:
            btn.update(mouse_pos)

        for buttons in self.slot_action_buttons.values():
            for btn in buttons:
                btn.update(mouse_pos)

    def render(self, surface):
        """Renderiza a tela de seleção de saves"""
        surface.fill(self.theme.COLOR_BACKGROUND)

        # Título
        title_font = self.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            f"SAVES - SLOT {self.game_slot_id}", True, self.theme.COLOR_TEXT_PRIMARY
        )
        title_y = self.ui_scaler.scale(100, "y")
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, title_y))
        surface.blit(title_text, title_rect)

        # Subtítulo
        subtitle_font = self.ui_scaler.get_themed_font("menu")
        subtitle_text = subtitle_font.render(
            "Selecione um save para carregar", True, self.theme.COLOR_TEXT_SECONDARY
        )
        subtitle_y = self.ui_scaler.scale(170, "y")
        subtitle_rect = subtitle_text.get_rect(
            center=(surface.get_width() // 2, subtitle_y)
        )
        surface.blit(subtitle_text, subtitle_rect)

        # Renderiza os 3 slots
        self._render_save_slots(surface)

        # Botões
        for btn in self.buttons:
            btn.render(surface)

        for buttons in self.slot_action_buttons.values():
            for btn in buttons:
                btn.render(surface)

        # Modal de confirmação
        if self.confirm_delete_slot:
            self._render_confirm_modal(surface)

    def _render_save_slots(self, surface):
        """Renderiza os 3 cards de save"""
        total_width = self.base_slot_width * 3 + self.base_spacing * 2
        base_start_x = (self.theme.BASE_WIDTH - total_width) // 2

        for i, slot in enumerate(self.slots):
            base_x = base_start_x + i * (self.base_slot_width + self.base_spacing)
            self._render_slot_card(surface, slot, base_x, self.base_start_y)

    def _render_slot_card(self, surface, slot, base_x, base_y):
        """Renderiza um card de slot individual"""
        # Escala o card
        card_rect = self.ui_scaler.rect(
            base_x, base_y, self.base_slot_width, self.base_slot_height
        )

        # Fundo e borda
        border_color = (
            self.theme.COLOR_ACCENT_GOLD
            if slot.get("slot_type") == "auto"
            else self.theme.COLOR_ACCENT_BLUE
        )

        pygame.draw.rect(surface, self.theme.COLOR_BG_CARD, card_rect, border_radius=15)
        pygame.draw.rect(surface, border_color, card_rect, 3, border_radius=15)

        # Título do slot
        title_font = self.ui_scaler.get_themed_font("hud")
        slot_title = slot.get("save_title", f"Save {slot.get('save_slot_id', '?')}")
        title_surface = title_font.render(slot_title, True, border_color)

        padding_x = self.ui_scaler.scale(20, "x")
        padding_y_title = self.ui_scaler.scale(15, "y")
        surface.blit(
            title_surface, (card_rect.x + padding_x, card_rect.y + padding_y_title)
        )

        # Se vazio
        if not slot.get("hero_name"):
            empty_font = self.ui_scaler.get_themed_font("title")
            empty_text = empty_font.render(
                "[ VAZIO ]", True, self.theme.COLOR_TEXT_HINT
            )
            surface.blit(
                empty_text,
                (
                    card_rect.centerx - empty_text.get_width() // 2,
                    card_rect.centery
                    - empty_text.get_height() // 2
                    - self.ui_scaler.scale(15, "y"),
                ),
            )

            hint_font = self.ui_scaler.get_themed_font("menu_small")
            hint_text = hint_font.render(
                "Nenhum save gravado neste slot", True, self.theme.COLOR_TEXT_HINT
            )
            surface.blit(
                hint_text,
                (
                    card_rect.centerx - hint_text.get_width() // 2,
                    card_rect.centery + self.ui_scaler.scale(10, "y"),
                ),
            )
            return

        # Informações do save ocupado
        info_font = self.ui_scaler.get_themed_font("menu")

        # Descrição (se houver)
        description = slot.get("save_description", "")
        if description:
            desc_text = info_font.render(
                description[:50], True, self.theme.COLOR_TEXT_SECONDARY
            )
            desc_y = self.ui_scaler.scale(45, "y")
            surface.blit(desc_text, (card_rect.x + padding_x, card_rect.y + desc_y))

        # Nome do herói
        name_text = info_font.render(
            f"Herói: {slot['hero_name']}", True, self.theme.COLOR_TEXT_PRIMARY
        )
        name_y = self.ui_scaler.scale(75, "y")
        surface.blit(name_text, (card_rect.x + padding_x, card_rect.y + name_y))

        # Nível e Classe
        level_class = (
            f"Nv.{slot.get('hero_level', 1)} - {slot.get('hero_class', 'N/A')}"
        )
        level_text = info_font.render(
            level_class, True, self.theme.COLOR_TEXT_SECONDARY
        )
        # Ajustado para 105
        level_y = self.ui_scaler.scale(105, "y")
        surface.blit(level_text, (card_rect.x + padding_x, card_rect.y + level_y))

        # Zona
        zone_text = info_font.render(
            f"Zona: {slot.get('zone_name', 'Desconhecida')}",
            True,
            self.theme.COLOR_ACCENT_BLUE,
        )
        # Ajustado para 135
        zone_y = self.ui_scaler.scale(135, "y")
        surface.blit(zone_text, (card_rect.x + padding_x, card_rect.y + zone_y))

        # Data/Hora do save
        last_saved = slot.get("last_saved", "")
        if last_saved:
            try:
                dt = datetime.fromisoformat(last_saved.replace(" ", "T"))
                date_str = dt.strftime("%d/%m/%Y %H:%M")
            except:
                date_str = last_saved[:16] if len(last_saved) > 16 else last_saved

            date_font = self.ui_scaler.get_themed_font("menu_small")
            date_text = date_font.render(date_str, True, self.theme.COLOR_TEXT_HINT)
            surface.blit(
                date_text,
                (card_rect.right - date_text.get_width() - 20, card_rect.bottom - 30),
            )

    def _render_confirm_modal(self, surface):
        """Renderiza modal de confirmação de exclusão"""
        # Overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

        # Caixa do modal
        base_box_x = (self.theme.BASE_WIDTH - self.theme.MODAL_WIDTH) // 2
        base_box_y = (self.theme.BASE_HEIGHT - 200) // 2
        modal_rect = self.ui_scaler.rect(
            base_box_x, base_box_y, self.theme.MODAL_WIDTH, 200
        )

        pygame.draw.rect(
            surface, self.theme.COLOR_BG_MODAL, modal_rect, border_radius=20
        )
        pygame.draw.rect(
            surface, self.theme.COLOR_BORDER_WARNING, modal_rect, 3, border_radius=20
        )

        # Texto
        title_font = self.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            "⚠️ CONFIRMAÇÃO", True, self.theme.COLOR_TEXT_WARNING
        )
        surface.blit(
            title_text,
            (
                modal_rect.centerx - title_text.get_width() // 2,
                modal_rect.y + self.ui_scaler.scale(30, "y"),
            ),
        )

        # Tipo de save
        slot = self.slots[self.confirm_delete_slot - 1]
        save_type = (
            "Auto-Save"
            if slot.get("slot_type") == "auto"
            else f"Save Manual {self.confirm_delete_slot}"
        )

        msg_font = self.ui_scaler.get_themed_font("menu")
        msg_text = msg_font.render(
            f"Deletar {save_type}?", True, self.theme.COLOR_TEXT_PRIMARY
        )
        surface.blit(
            msg_text,
            (
                modal_rect.centerx - msg_text.get_width() // 2,
                modal_rect.y + self.ui_scaler.scale(90, "y"),
            ),
        )

        hint_font = self.ui_scaler.get_themed_font("menu_small")
        hint_text = hint_font.render(
            "Pressione ESC para cancelar", True, self.theme.COLOR_TEXT_HINT
        )
        surface.blit(
            hint_text,
            (
                modal_rect.centerx - hint_text.get_width() // 2,
                modal_rect.y + self.ui_scaler.scale(150, "y"),
            ),
        )

        # Botão de confirmação
        if self.confirm_button:
            self.confirm_button.render(surface)

    def enter(self):
        """Chamado ao entrar no estado"""
        print(f"💾 Entrando na seleção de saves do slot {self.game_slot_id}")

    def exit(self):
        """Chamado ao sair do estado"""
        print("💾 Saindo da seleção de saves")

    def on_resize(self, old_size, new_size):
        """Recria a UI ao redimensionar"""
        self._create_ui()
