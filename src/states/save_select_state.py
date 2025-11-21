# src/states/save_select_state.py - ATUALIZADO PARA SISTEMA DE SLOTS
import pygame
from datetime import datetime
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager


class SaveSelectState(BaseState):
    """Tela de seleção de slot de save (3 saves por slot de jogo)"""

    def __init__(self, game):
        super().__init__(game)
        self.game_slot_id = getattr(game, "selected_game_slot", 1)
        self.slots = []
        self.buttons = []
        self.slot_action_buttons = {}  # Botões de ação por slot
        self.confirm_delete_slot = None  # Slot aguardando confirmação de exclusão
        self.confirm_button = None  # Botão de confirmação no modal
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

            # Converte para lista de dicts
            for row in slots_data:
                self.slots.append(dict(row))

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

        # Botão Voltar
        back_btn = Button(100, 980, 200, 60, "VOLTAR", self._back_to_slots, 24)
        self.buttons.append(back_btn)

        # Parâmetros dos slots
        slot_width = 500
        slot_height = 240  # Aumentado para acomodar botões
        spacing = 50
        start_x = (1920 - (slot_width * 3 + spacing * 2)) // 2
        start_y = 350

        # Cria botões de ação para cada slot
        for i in range(3):
            save_slot_id = i + 1
            slot = self.slots[i]
            x_pos = start_x + i * (slot_width + spacing)
            is_empty = not slot.get("hero_name")
            is_auto = slot.get("slot_type") == "auto"

            # Armazena botões deste slot
            self.slot_action_buttons[save_slot_id] = []

            if not is_empty:
                # Save ocupado: Botões CARREGAR e DELETAR
                load_btn = Button(
                    x_pos + 20,
                    start_y + slot_height - 50,
                    220,
                    40,
                    "CARREGAR SAVE",
                    lambda sid=save_slot_id: self._load_save(sid),
                    18,
                )
                delete_btn = Button(
                    x_pos + slot_width - 240,
                    start_y + slot_height - 50,
                    220,
                    40,
                    "DELETAR SAVE",
                    lambda sid=save_slot_id: self._confirm_delete_save(sid),
                    18,
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
        if self.confirm_delete_slot == save_slot_id:
            # Já está mostrando o modal, o clique será tratado pelo botão do modal
            pass
        else:
            # Primeira vez - pede confirmação
            self.confirm_delete_slot = save_slot_id

            # Cria botão de confirmação
            box_width = 600
            box_height = 200
            box_x = (1920 - box_width) // 2
            box_y = (1080 - box_height) // 2

            self.confirm_button = Button(
                box_x + box_width // 2 - 100,
                box_y + 130,
                200,
                40,
                "CONFIRMAR",
                lambda: self._delete_save(save_slot_id),
                20,
                text_color=(255, 255, 255),
                bg_color=(200, 50, 50),
                hover_color=(255, 80, 80),
            )

            self.game.notification_manager.add_notification(
                f"Confirme a exclusão", (255, 100, 100)
            )

    def _delete_save(self, save_slot_id):
        """Deleta um save específico (limpa os dados mas mantém o slot)"""
        try:
            cursor = self.game.game_config.database.connection.cursor()

            # Limpa o save (não deleta o registro, apenas reseta os dados)
            cursor.execute(
                """
                UPDATE save_slots 
                SET hero_name = NULL,
                    hero_level = 1,
                    hero_class = NULL,
                    zone_name = 'Início',
                    zone_id = 1,
                    playtime = 0,
                    save_description = '',
                    is_active = 0
                WHERE game_slot_id = ? AND save_slot_id = ?
                """,
                (self.game_slot_id, save_slot_id),
            )

            self.game.game_config.database.connection.commit()
            self.game.notification_manager.add_notification(
                f"Save {save_slot_id} deletado com sucesso", (100, 255, 100)
            )

            self.confirm_button = None

            # Recarrega os slots
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
                self._back_to_slots()
                self.confirm_delete_slot = None  # Cancela confirmação
                self.confirm_button = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Se modal de confirmação estiver aberto, só verifica ele
            if self.confirm_delete_slot and self.confirm_button:
                if self.confirm_button.is_hovered(event.pos, self.game):
                    self.confirm_button.on_click()
                # Se clicar fora, pode fechar o modal se quiser, ou ignorar
                # Por enquanto, vamos permitir clicar fora para cancelar
                elif not pygame.Rect(
                    (1920 - 600) // 2, (1080 - 200) // 2, 600, 200
                ).collidepoint(event.pos):
                    self.confirm_delete_slot = None
                    self.confirm_button = None
                return

            # Verifica clique nos botões principais
            ButtonManager.handle_button_click(self.buttons, event, self.game)

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
        for action_buttons in self.slot_action_buttons.values():
            ButtonManager.update_buttons(action_buttons, self.game)

    def render(self, surface):
        """Renderiza a tela de seleção de saves"""
        screen_width, screen_height = surface.get_size()

        # Fundo
        surface.fill(self.game.game_config.get_color("background"))

        # Título
        title_font = self.game.game_config.get_font("title", 60)
        title_text = title_font.render(
            f"SAVES - SLOT {self.game_slot_id}", True, (255, 255, 255)
        )
        surface.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 100))

        # Subtítulo
        subtitle_font = self.game.game_config.get_font("menu", 24)
        subtitle_text = subtitle_font.render(
            "Selecione um save para carregar", True, (180, 180, 180)
        )
        surface.blit(
            subtitle_text, (screen_width // 2 - subtitle_text.get_width() // 2, 170)
        )

        # Renderiza os 3 slots
        self._render_save_slots(surface)

        # Botões principais
        ButtonManager.render_buttons(self.buttons, surface, self.game.game_config)

        # Renderiza botões de ação dos slots
        for action_buttons in self.slot_action_buttons.values():
            ButtonManager.render_buttons(action_buttons, surface, self.game.game_config)

        # Renderiza mensagem de confirmação se houver
        if self.confirm_delete_slot:
            self._render_confirm_message(surface)
            if self.confirm_button:
                self.confirm_button.render(surface, self.game.game_config)

    def _render_save_slots(self, surface):
        """Renderiza os 3 cards de save"""
        slot_width = 500
        slot_height = 240  # Aumentado
        spacing = 50
        start_x = (1920 - (slot_width * 3 + spacing * 2)) // 2
        start_y = 350

        for i, slot in enumerate(self.slots):
            x_pos = start_x + i * (slot_width + spacing)
            self._render_slot_card(
                surface, slot, x_pos, start_y, slot_width, slot_height
            )

    def _render_slot_card(self, surface, slot, x, y, width, height):
        """Renderiza um card de slot individual"""
        # Fundo do card
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (30, 30, 40), card_rect, border_radius=15)

        # Borda (dourada se auto, azul se manual)
        border_color = (
            (255, 215, 0) if slot.get("slot_type") == "auto" else (100, 150, 255)
        )
        pygame.draw.rect(surface, border_color, card_rect, 3, border_radius=15)

        # Título do slot
        title_font = self.game.game_config.get_font("title", 24)
        slot_title = slot.get("save_title", f"Save {slot.get('save_slot_id', '?')}")
        title_surface = title_font.render(slot_title, True, border_color)
        surface.blit(title_surface, (x + 20, y + 15))

        # Se o slot está vazio
        if not slot.get("hero_name"):
            empty_font = self.game.game_config.get_font("menu", 36)
            empty_text = empty_font.render("[ VAZIO ]", True, (100, 100, 100))
            surface.blit(
                empty_text,
                (x + width // 2 - empty_text.get_width() // 2, y + height // 2 - 30),
            )

            hint_font = self.game.game_config.get_font("menu", 18)
            hint_text = hint_font.render(
                "Nenhum save gravado neste slot", True, (150, 150, 150)
            )
            surface.blit(
                hint_text,
                (x + width // 2 - hint_text.get_width() // 2, y + height // 2 + 10),
            )
            return

        # Informações do save
        info_font = self.game.game_config.get_font("menu", 20)

        # Descrição (se houver)
        description = slot.get("save_description", "")
        if description:
            desc_text = info_font.render(description[:50], True, (180, 180, 180))
            surface.blit(desc_text, (x + 20, y + 50))

        # Nome do herói
        name_text = info_font.render(
            f"Herói: {slot['hero_name']}", True, (255, 255, 255)
        )
        surface.blit(name_text, (x + 20, y + 85))

        # Nível e Classe
        level_class = (
            f"Nv.{slot.get('hero_level', 1)} - {slot.get('hero_class', 'N/A')}"
        )
        level_text = info_font.render(level_class, True, (200, 200, 200))
        surface.blit(level_text, (x + 20, y + 115))

        # Zona
        zone_text = info_font.render(
            f"Zona: {slot.get('zone_name', 'Desconhecida')}", True, (150, 200, 255)
        )
        surface.blit(zone_text, (x + 20, y + 145))

        # Data/Hora do save
        last_saved = slot.get("last_saved", "")
        if last_saved:
            try:
                # Tenta formatar a data
                dt = datetime.fromisoformat(last_saved.replace(" ", "T"))
                date_str = dt.strftime("%d/%m/%Y %H:%M")
            except:
                date_str = last_saved[:16] if len(last_saved) > 16 else last_saved

            date_font = self.game.game_config.get_font("menu", 18)
            date_text = date_font.render(date_str, True, (150, 150, 150))
            surface.blit(
                date_text, (x + width - date_text.get_width() - 20, y + height - 30)
            )

    def _render_confirm_message(self, surface):
        """Renderiza mensagem de confirmação de exclusão de save"""
        # Overlay semi-transparente
        overlay = pygame.Surface((1920, 1080), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

        # Caixa de confirmação
        box_width = 600
        box_height = 200
        box_x = (1920 - box_width) // 2
        box_y = (1080 - box_height) // 2

        pygame.draw.rect(
            surface,
            (40, 40, 50),
            (box_x, box_y, box_width, box_height),
            border_radius=20,
        )
        pygame.draw.rect(
            surface,
            (255, 100, 100),
            (box_x, box_y, box_width, box_height),
            3,
            border_radius=20,
        )

        # Texto de confirmação
        title_font = self.game.game_config.get_font("title", 36)
        title_text = title_font.render("⚠️ CONFIRMAÇÃO", True, (255, 100, 100))
        surface.blit(
            title_text,
            (box_x + box_width // 2 - title_text.get_width() // 2, box_y + 30),
        )

        # Identifica tipo de save
        slot = self.slots[self.confirm_delete_slot - 1]
        save_type = (
            "Auto-Save"
            if slot.get("slot_type") == "auto"
            else f"Save Manual {self.confirm_delete_slot}"
        )

        msg_font = self.game.game_config.get_font("menu", 24)
        msg_text = msg_font.render(f"Deletar {save_type}?", True, (255, 255, 255))
        surface.blit(
            msg_text, (box_x + box_width // 2 - msg_text.get_width() // 2, box_y + 90)
        )

        hint_font = self.game.game_config.get_font("menu", 20)
        # Botão renderizado separadamente

        hint2_text = hint_font.render(
            "Pressione ESC para cancelar", True, (150, 150, 150)
        )
        surface.blit(
            hint2_text,
            (box_x + box_width // 2 - hint2_text.get_width() // 2, box_y + 175),
        )

    def enter(self):
        """Chamado ao entrar no estado"""
        print(f"💾 Entrando na seleção de saves do slot {self.game_slot_id}")

    def exit(self):
        """Chamado ao sair do estado"""
        print("💾 Saindo da seleção de saves")

    def on_resize(self, old_size, new_size):
        """Recria a UI ao redimensionar"""
        self._create_ui()
