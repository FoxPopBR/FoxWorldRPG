# src/states/game_state.py - REDESIGN ESTILO PHANTASY STAR
import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager


class GameState(BaseState):
    """Tela principal do jogo - HUD estilo Phantasy Star 1"""

    def __init__(self, game, hero=None):
        super().__init__(game)

        # Carrega o herói ativo
        self.hero = (
            hero if hero else self.game.game_config.hero_manager.get_active_hero()
        )

        if not self.hero:
            print("⚠️ Nenhum herói ativo encontrado, voltando ao menu")
            from src.states.menu_state import MenuState

            self.game.state_manager.change_state(MenuState(self.game))
            return

        self.buttons = []
        self.sidebar_buttons = []  # Menu lateral
        self.menu_buttons = []
        self.save_buttons = []
        self.load_buttons = []
        self.show_menu = False
        self.show_save_menu = False
        self.show_load_menu = False
        self.show_load_menu = False
        self.last_save_slot = 2  # Padrão para quicksave (Slot Manual 1)

        # Menu principal agora é acessível via ESC ou clicando no botão do sidebar
        # Removido botão "MENU" do canto superior direito

        self._create_sidebar_menu()
        self._create_menu_ui()
        self._create_save_ui()

    def _create_sidebar_menu(self):
        """Cria menu lateral esquerdo fixo"""
        self.sidebar_buttons.clear()

        # Posição alinhada com o sidebar background (x=5, width=90)
        # Vamos centralizar os botões dentro do sidebar de 90px
        # Botões pequenos (ícones) seriam ideais, mas vamos usar texto curto ou ícones se possível
        # Como Button aceita texto, vamos usar letras ou símbolos por enquanto

        start_x = 10
        start_y = 125  # Um pouco abaixo do topo do sidebar (115)
        btn_width = 80
        btn_height = 80
        spacing = 10

        # Ícones/Texto para o menu lateral
        menu_items = [
            ("INV", self._open_inventory),  # Inventário
            ("PER", self._open_profile),  # Perfil
            ("MAP", self._open_map),  # Mapa
            ("GRP", self._open_group),  # Grupo
            ("CFG", self._toggle_menu),  # Menu/Config (abre o menu de pausa)
        ]

        for i, (text, action) in enumerate(menu_items):
            btn = Button(
                start_x,
                start_y + i * (btn_height + spacing),
                btn_width,
                btn_height,
                text,
                action,
                20,
            )
            self.sidebar_buttons.append(btn)

    def _create_save_ui(self):
        """Cria botões do menu de save"""
        self.save_buttons.clear()

        center_x = 1920 // 2
        start_y = 400
        btn_width = 350
        btn_height = 60
        spacing = 30

        # Slot 2 (Manual 1)
        btn_slot2 = Button(
            center_x - btn_width // 2,
            start_y,
            btn_width,
            btn_height,
            "SALVAR NO SLOT 1 (MANUAL)",
            lambda: self._save_to_slot(2),
            20,
        )

        # Slot 3 (Manual 2)
        btn_slot3 = Button(
            center_x - btn_width // 2,
            start_y + btn_height + spacing,
            btn_width,
            btn_height,
            "SALVAR NO SLOT 2 (MANUAL)",
            lambda: self._save_to_slot(3),
            20,
        )

        # Cancelar
        btn_cancel = Button(
            center_x - btn_width // 2,
            start_y + (btn_height + spacing) * 2 + 20,
            btn_width,
            btn_height,
            "CANCELAR",
            lambda: setattr(self, "show_save_menu", False),
            20,
        )

        self.save_buttons.extend([btn_slot2, btn_slot3, btn_cancel])

    def _create_menu_ui(self):
        """Cria botões do menu in-game"""
        self.menu_buttons.clear()

        center_x = 1920 // 2
        # Menu rect: (center_x - 200, 290, 400, 500) -> Topo Y=290
        # Título em Y=320. Botões devem começar abaixo.
        start_y = 380
        btn_width = 300
        btn_height = 50
        spacing = 20

        options = [
            ("VOLTAR AO JOGO", self._toggle_menu),
            ("SALVAR JOGO", self._save_game),
            ("CARREGAR JOGO", self._load_game_menu),
            ("INVENTÁRIO", self._open_inventory),
            ("CONFIGURAÇÕES", self._open_settings),
            ("SAIR PARA MENU", self._exit_to_main_menu),
        ]

        for i, (text, action) in enumerate(options):
            btn = Button(
                center_x - btn_width // 2,
                start_y + i * (btn_height + spacing),
                btn_width,
                btn_height,
                text,
                action,
                20,
            )
            self.menu_buttons.append(btn)

    def _toggle_menu(self):
        """Alterna visibilidade do menu"""
        self.show_menu = not self.show_menu

    def _save_game(self):
        """Abre menu de seleção de slot para salvar"""
        self.show_save_menu = True

    def _load_game_menu(self):
        """Abre menu de seleção de slot para carregar"""
        self.load_buttons.clear()
        center_x = 1920 // 2
        start_y = 350
        btn_width = 400
        btn_height = 60
        spacing = 20

        # Busca slots do banco
        game_slot_id = getattr(self.game, "selected_game_slot", 1)
        cursor = self.game.game_config.database.connection.cursor()
        cursor.execute(
            "SELECT save_slot_id, save_title, hero_level, hero_class, last_saved FROM save_slots WHERE game_slot_id = ? ORDER BY save_slot_id",
            (game_slot_id,),
        )
        slots = cursor.fetchall()

        # Mapeia slots encontrados
        slots_dict = {row[0]: row for row in slots}

        # Cria botões para os 3 slots
        slot_names = {1: "AUTO SAVE", 2: "MANUAL 1", 3: "MANUAL 2"}

        for i in range(1, 4):
            slot_data = slots_dict.get(i)
            y_pos = start_y + (i - 1) * (btn_height + spacing)

            if slot_data and slot_data[1]:  # Se tem título (não vazio)
                title = slot_data[1]
                level = slot_data[2]
                cls = slot_data[3]
                date = slot_data[4]
                # Formata data (pega apenas hora/min se for hoje, ou data completa)
                # Simplificando para mostrar string crua ou formatada simples
                text = f"[{slot_names[i]}] {title} (Lv.{level} {cls})"
                action = lambda s=i: self._load_from_slot(s)
            else:
                text = f"[{slot_names[i]}] VAZIO"
                action = None  # Desabilita clique

            btn = Button(
                center_x - btn_width // 2,
                y_pos,
                btn_width,
                btn_height,
                text,
                action,
                20,
            )
            self.load_buttons.append(btn)

        # Botão Cancelar
        cancel_btn = Button(
            center_x - btn_width // 2,
            start_y + 3 * (btn_height + spacing) + 20,
            btn_width,
            btn_height,
            "CANCELAR",
            lambda: setattr(self, "show_load_menu", False),
            20,
        )
        self.load_buttons.append(cancel_btn)

        self.show_load_menu = True

    def _load_from_slot(self, slot_id):
        """Carrega o jogo do slot especificado"""
        try:
            game_slot_id = getattr(self.game, "selected_game_slot", 1)
            cursor = self.game.game_config.database.connection.cursor()
            cursor.execute(
                "SELECT hero_name FROM save_slots WHERE game_slot_id = ? AND save_slot_id = ?",
                (game_slot_id, slot_id),
            )
            row = cursor.fetchone()

            if row and row[0]:
                hero_name = row[0]
                # Carrega herói usando HeroManager
                hero = self.game.game_config.hero_manager.get_hero(hero_name)
                if hero:
                    self.hero = hero
                    self.game.game_config.hero_manager.set_current_hero(hero)

                    self.game.notification_manager.add_notification(
                        f"Jogo carregado: {hero_name}", (100, 255, 100)
                    )
                    self.show_load_menu = False
                    self.show_menu = False
                    # Recria UI para atualizar HUD com novos dados
                    self._create_ui()
                else:
                    raise Exception("Herói não encontrado no gerenciador")
            else:
                raise Exception("Save vazio ou inválido")

        except Exception as e:
            self.game.notification_manager.add_notification(
                f"Erro ao carregar: {e}", (255, 100, 100)
            )
            print(f"Erro load: {e}")

    def _save_to_slot(self, slot_id):
        """Salva o jogo no slot especificado"""
        try:
            hero = self.hero
            game_slot_id = getattr(self.game, "selected_game_slot", 1)

            cursor = self.game.game_config.database.connection.cursor()

            # Atualiza o save slot
            cursor.execute(
                """
                UPDATE save_slots 
                SET hero_name = ?,
                    hero_level = ?,
                    hero_class = ?,
                    zone_name = ?,
                    zone_id = ?,
                    playtime = ?,
                    last_saved = CURRENT_TIMESTAMP,
                    save_title = ?,
                    save_description = ?,
                    is_active = 1
                WHERE game_slot_id = ? AND save_slot_id = ?
            """,
                (
                    hero.name,
                    hero.level,
                    hero.hero_class.value,
                    f"Zona {hero.zone_id}",
                    hero.zone_id,
                    0,  # TODO: Implementar playtime real
                    f"Save Manual {slot_id - 1}",
                    f"Nível {hero.level} - {hero.hero_class.value}",
                    game_slot_id,
                    slot_id,
                ),
            )

            # Atualiza também o game slot (last_played)
            cursor.execute(
                """
                UPDATE game_slots
                SET last_played = CURRENT_TIMESTAMP
                WHERE slot_id = ?
            """,
                (game_slot_id,),
            )

            self.game.game_config.database.connection.commit()

            self.last_save_slot = slot_id
            self.game.notification_manager.add_notification(
                f"Jogo salvo no Slot {slot_id}!", (100, 255, 100)
            )
            self.show_save_menu = False
            self.show_menu = False  # Fecha menu principal também

        except Exception as e:
            self.game.notification_manager.add_notification(
                f"Erro ao salvar: {e}", (255, 100, 100)
            )
            print(f"Erro save: {e}")

    def _quick_save(self):
        """Salva rapidamente no último slot usado"""
        self._save_to_slot(self.last_save_slot)

    def _open_inventory(self):
        """Abre o inventário"""
        from src.states.inventory_state import InventoryState

        self.game.state_manager.change_state(InventoryState(self.game))

    def _open_profile(self):
        """Abre o perfil do herói"""
        from src.states.profile_state import ProfileState

        self.game.state_manager.change_state(ProfileState(self.game))

    def _open_map(self):
        """Abre o mapa"""
        from src.states.map_state import MapState

        self.game.state_manager.change_state(MapState(self.game))

    def _open_group(self):
        """Abre a tela de grupo"""
        from src.states.group_state import GroupState

        self.game.state_manager.change_state(GroupState(self.game))

    def _open_settings(self):
        """Abre menu de configurações"""
        from src.states.settings_state import SettingsState

        self.game.state_manager.push_state(SettingsState(self.game, from_game=True))

    def _exit_to_main_menu(self):
        """Sai para o menu principal"""
        from src.states.menu_state import MenuState

        self.game.state_manager.change_state(MenuState(self.game))

    def handle_event(self, event):
        """Processa eventos"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.show_save_menu:
                    self.show_save_menu = False
                elif self.show_load_menu:
                    self.show_load_menu = False
                else:
                    self._toggle_menu()

            elif event.key == pygame.K_F5:
                self._quick_save()
            elif event.key == pygame.K_F1:
                self._open_inventory()
                return
            elif event.key == pygame.K_F2:
                self._open_profile()
                return
            elif event.key == pygame.K_F3:
                self._open_map()
                return
            elif event.key == pygame.K_F4:
                self._open_group()
                return
            elif event.key == pygame.K_b:  # Debug Batalha
                self._trigger_battle()
                return

            # Se menu aberto, ignora outros inputs
            if self.show_menu:
                return

            # Teclas de movimento (WASD ou setas)
            if event.key in [pygame.K_w, pygame.K_UP]:
                print("⬆️ Movendo para cima")
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                print("⬇️ Movendo para baixo")
            elif event.key in [pygame.K_a, pygame.K_LEFT]:
                print("⬅️ Movendo para esquerda")
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                print("➡️ Movendo para direita")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.show_save_menu:
                ButtonManager.handle_button_click(self.save_buttons, event, self.game)
            elif self.show_load_menu:
                ButtonManager.handle_button_click(self.load_buttons, event, self.game)
            elif self.show_menu:
                ButtonManager.handle_button_click(self.menu_buttons, event, self.game)
            else:
                # Sidebar sempre visível
                ButtonManager.handle_button_click(
                    self.sidebar_buttons, event, self.game
                )
                ButtonManager.handle_button_click(self.buttons, event, self.game)

    def _render_load_menu(self, surface):
        """Renderiza overlay de seleção de load"""
        screen_width, screen_height = surface.get_size()
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Caixa do menu
        menu_w = self.game.ui_scaler.scale(500, "x")
        menu_h = self.game.ui_scaler.scale(450, "y")
        menu_x = (screen_width - menu_w) // 2
        menu_y = self.game.ui_scaler.scale(300, "y")

        menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
        pygame.draw.rect(surface, (30, 30, 40), menu_rect, border_radius=15)
        pygame.draw.rect(surface, (100, 200, 255), menu_rect, 2, border_radius=15)

        # Título
        title_font = self.game.ui_scaler.get_themed_font("title")
        title_text = title_font.render("CARREGAR JOGO", True, (255, 255, 255))
        surface.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, menu_y + 20)
        )

        ButtonManager.render_buttons(self.load_buttons, surface, self.game.game_config)

    def _render_save_menu(self, surface):
        """Renderiza overlay de seleção de save"""
        screen_width, screen_height = surface.get_size()
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Caixa do menu
        menu_w = self.game.ui_scaler.scale(500, "x")
        menu_h = self.game.ui_scaler.scale(400, "y")
        menu_x = (screen_width - menu_w) // 2
        menu_y = self.game.ui_scaler.scale(300, "y")

        menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
        pygame.draw.rect(surface, (30, 30, 40), menu_rect, border_radius=15)
        pygame.draw.rect(surface, (100, 255, 100), menu_rect, 2, border_radius=15)

        # Título
        title_font = self.game.ui_scaler.get_themed_font("title")
        title_text = title_font.render("SALVAR JOGO", True, (255, 255, 255))
        surface.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, menu_y + 30)
        )

        # Subtítulo
        sub_font = self.game.ui_scaler.get_themed_font("menu")
        sub_text = sub_font.render(
            "Escolha um slot para sobrescrever", True, (200, 200, 200)
        )
        surface.blit(
            sub_text, (screen_width // 2 - sub_text.get_width() // 2, menu_y + 80)
        )

        ButtonManager.render_buttons(self.save_buttons, surface, self.game.game_config)

    def _render_menu_overlay(self, surface):
        """Renderiza overlay do menu in-game"""
        screen_width, screen_height = surface.get_size()
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Caixa do menu
        menu_w = self.game.ui_scaler.scale(400, "x")
        menu_h = self.game.ui_scaler.scale(500, "y")
        menu_x = (screen_width - menu_w) // 2
        menu_y = self.game.ui_scaler.scale(290, "y")

        menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
        pygame.draw.rect(surface, (30, 30, 40), menu_rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 150), menu_rect, 2, border_radius=15)

        # Título
        title_font = self.game.ui_scaler.get_themed_font("title")
        title_text = title_font.render("MENU DE PAUSA", True, (255, 255, 255))
        surface.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, menu_y + 30)
        )

        ButtonManager.render_buttons(self.menu_buttons, surface, self.game.game_config)

    def _render_sidebar(self, surface):
        """Renderiza menu lateral esquerdo fixo"""
        # Fundo do sidebar
        sidebar_w = self.game.ui_scaler.scale(90, "x")
        sidebar_h = self.game.ui_scaler.scale(455, "y")
        sidebar_x = self.game.ui_scaler.scale(5, "x")
        sidebar_y = self.game.ui_scaler.scale(115, "y")

        sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, sidebar_w, sidebar_h)
        pygame.draw.rect(surface, (20, 20, 30), sidebar_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 60, 80), sidebar_rect, 2, border_radius=10)

        # Renderiza botões
        ButtonManager.render_buttons(
            self.sidebar_buttons, surface, self.game.game_config
        )

    def _render_game_area(self, surface, screen_width, game_area_height):
        """Renderiza a área principal do jogo"""
        # Título temporário
        title_font = self.game.ui_scaler.get_themed_font("title")
        title_text = title_font.render(
            "🌍 ÁREA DE EXPLORAÇÃO 🌍", True, (255, 255, 255)
        )
        surface.blit(
            title_text,
            (
                screen_width // 2 - title_text.get_width() // 2,
                int(game_area_height * 0.15),
            ),
        )

        # Mensagem de desenvolvimento
        dev_font = self.game.ui_scaler.get_themed_font("menu")
        dev_text1 = dev_font.render(
            "🚧 Mundo em Desenvolvimento 🚧", True, (255, 200, 100)
        )
        dev_text2 = dev_font.render(
            "Use WASD ou Setas para se mover", True, (200, 200, 200)
        )
        dev_text3 = dev_font.render("ESC para abrir o menu", True, (180, 180, 180))

        center_y = game_area_height // 2
        spacing = int(game_area_height * 0.05)

        surface.blit(
            dev_text1,
            (
                screen_width // 2 - dev_text1.get_width() // 2,
                center_y - spacing,
            ),
        )
        surface.blit(
            dev_text2,
            (
                screen_width // 2 - dev_text2.get_width() // 2,
                center_y + spacing,
            ),
        )
        surface.blit(
            dev_text3,
            (
                screen_width // 2 - dev_text3.get_width() // 2,
                center_y + spacing * 2,
            ),
        )

    def _render_hud_phantasy_star(
        self, surface, screen_width, screen_height, game_area_height
    ):
        """Renderiza HUD horizontal inferior estilo Phantasy Star 1"""
        # Altura já calculada e passada via game_area_height (que é o Y inicial do HUD)
        hud_y = game_area_height
        hud_height = screen_height - hud_y

        # Fundo do HUD (cor sólida escura)
        hud_rect = pygame.Rect(0, hud_y, screen_width, hud_height)
        pygame.draw.rect(surface, (20, 20, 30), hud_rect)

        # Borda superior do HUD
        pygame.draw.line(surface, (100, 100, 150), (0, hud_y), (screen_width, hud_y), 3)

        # Divisão em seções (estilo Phantasy Star)
        section_width = screen_width // 4

        # Seção 1: Nome e Classe
        self._render_hud_section_name(
            surface, 20, hud_y + 20, section_width - 40, hud_height - 40
        )

        # Linha divisória
        pygame.draw.line(
            surface,
            (60, 60, 80),
            (section_width, hud_y + 10),
            (section_width, hud_y + hud_height - 10),
            2,
        )

        # Seção 2: HP e MP
        self._render_hud_section_vitals(
            surface, section_width + 20, hud_y + 20, section_width - 40, hud_height - 40
        )

        # Linha divisória
        pygame.draw.line(
            surface,
            (60, 60, 80),
            (section_width * 2, hud_y + 10),
            (section_width * 2, hud_y + hud_height - 10),
            2,
        )

        # Seção 3: Nível e Experiência
        self._render_hud_section_level(
            surface,
            section_width * 2 + 20,
            hud_y + 20,
            section_width - 40,
            hud_height - 40,
        )

        # Linha divisória
        pygame.draw.line(
            surface,
            (60, 60, 80),
            (section_width * 3, hud_y + 10),
            (section_width * 3, hud_y + hud_height - 10),
            2,
        )

        # Seção 4: Gold e Localização
        self._render_hud_section_extras(
            surface,
            section_width * 3 + 20,
            hud_y + 20,
            section_width - 40,
            hud_height - 40,
        )

    def _render_hud_section_name(self, surface, x, y, width, height):
        """Renderiza seção de nome e classe"""
        scaler = self.game.ui_scaler

        # Nome do herói
        name_font = scaler.get_themed_font("title")
        name_text = name_font.render(self.hero.name, True, (255, 255, 100))
        surface.blit(name_text, (x, y))

        # Classe
        class_font = scaler.get_themed_font("menu")
        class_name = self.hero.hero_class.value.upper()
        class_text = class_font.render(class_name, True, (150, 200, 255))
        surface.blit(class_text, (x, y + int(height * 0.25)))

        # Ícone ou sprite do personagem
        icon_size = int(height * 0.4)
        icon_rect = pygame.Rect(x, y + int(height * 0.45), icon_size, icon_size)

        # Fundo do ícone
        pygame.draw.rect(surface, (20, 20, 30), icon_rect, border_radius=8)

        if self.hero.image_face:
            # Escala a imagem para caber no box
            face_img = pygame.transform.scale(
                self.hero.image_face, (icon_size, icon_size)
            )
            surface.blit(face_img, icon_rect)
        else:
            # Placeholder
            pygame.draw.rect(surface, (50, 50, 70), icon_rect, border_radius=8)

        # Borda
        pygame.draw.rect(surface, (100, 100, 150), icon_rect, 2, border_radius=8)

    def _render_hud_section_vitals(self, surface, x, y, width, height):
        """Renderiza seção de HP e MP com barras"""
        scaler = self.game.ui_scaler
        label_font = scaler.get_themed_font("menu_small")
        value_font = scaler.get_themed_font("title_small")

        # Altura relativa das barras
        bar_height = int(height * 0.12)
        spacing = int(height * 0.05)

        # HP
        hp_label = label_font.render("HP", True, (200, 200, 200))
        surface.blit(hp_label, (x, y))

        hp_current = self.hero.stats.vida_atual
        hp_max = self.hero.stats.vida_maxima
        hp_text = value_font.render(f"{hp_current}/{hp_max}", True, (100, 255, 100))
        text_x = x + int(width * 0.2)
        surface.blit(hp_text, (text_x, y - 2))

        # Barra de HP
        bar_width = width - int(width * 0.05)
        bar_y = y + int(height * 0.15)

        # Fundo da barra
        pygame.draw.rect(
            surface,
            (40, 40, 50),
            (x, bar_y, bar_width, bar_height),
            border_radius=5,
        )

        # Barra preenchida
        hp_ratio = hp_current / hp_max if hp_max > 0 else 0
        filled_width = int(bar_width * hp_ratio)
        hp_color = (
            (100, 255, 100)
            if hp_ratio > 0.5
            else (255, 200, 100) if hp_ratio > 0.25 else (255, 100, 100)
        )
        pygame.draw.rect(
            surface, hp_color, (x, bar_y, filled_width, bar_height), border_radius=5
        )

        # Borda da barra
        pygame.draw.rect(
            surface,
            (150, 150, 150),
            (x, bar_y, bar_width, bar_height),
            2,
            border_radius=5,
        )

        # MP (Offset Y relativo)
        mp_y_offset = int(height * 0.45)

        mp_label = label_font.render("MP", True, (200, 200, 200))
        surface.blit(mp_label, (x, y + mp_y_offset))

        mp_current = self.hero.stats.mana_atual
        mp_max = self.hero.stats.mana_maxima
        mp_text = value_font.render(f"{mp_current}/{mp_max}", True, (100, 150, 255))
        surface.blit(mp_text, (text_x, y + mp_y_offset - 2))

        # Barra de MP
        bar_y_mp = y + mp_y_offset + int(height * 0.15)

        # Fundo da barra
        pygame.draw.rect(
            surface,
            (40, 40, 50),
            (x, bar_y_mp, bar_width, bar_height),
            border_radius=5,
        )

        # Barra preenchida
        mp_ratio = mp_current / mp_max if mp_max > 0 else 0
        filled_width = int(bar_width * mp_ratio)
        pygame.draw.rect(
            surface,
            (100, 150, 255),
            (x, bar_y_mp, filled_width, bar_height),
            border_radius=5,
        )

        # Borda da barra
        pygame.draw.rect(
            surface,
            (150, 150, 150),
            (x, bar_y_mp, bar_width, bar_height),
            2,
            border_radius=5,
        )

    def _render_hud_section_level(self, surface, x, y, width, height):
        """Renderiza seção de nível e experiência"""
        scaler = self.game.ui_scaler
        label_font = scaler.get_themed_font("menu_small")
        value_font = scaler.get_themed_font("title")

        # Nível
        level_label = label_font.render("NÍVEL", True, (200, 200, 200))
        surface.blit(level_label, (x, y))

        level_text = value_font.render(str(self.hero.level), True, (255, 215, 0))
        surface.blit(level_text, (x, y + int(height * 0.15)))

        # Experiência (Offset Y relativo)
        exp_y_offset = int(height * 0.45)

        exp_label = label_font.render("EXP", True, (200, 200, 200))
        surface.blit(exp_label, (x, y + exp_y_offset))

        exp_font = scaler.get_themed_font("menu")
        exp_text = exp_font.render(str(self.hero.experience), True, (200, 255, 200))
        surface.blit(exp_text, (x, y + exp_y_offset + int(height * 0.15)))

    def _render_hud_section_extras(self, surface, x, y, width, height):
        """Renderiza seção de gold e localização"""
        scaler = self.game.ui_scaler
        label_font = scaler.get_themed_font("menu_small")
        value_font = scaler.get_themed_font("title_small")

        # Gold
        gold_label = label_font.render("GOLD", True, (200, 200, 200))
        surface.blit(gold_label, (x, y))

        gold_text = value_font.render(f"{self.hero.gold} G", True, (255, 215, 0))
        surface.blit(gold_text, (x, y + int(height * 0.15)))

        # Localização (Offset Y relativo)
        loc_y_offset = int(height * 0.45)

        loc_label = label_font.render("ZONA", True, (200, 200, 200))
        surface.blit(loc_label, (x, y + loc_y_offset))

        loc_font = scaler.get_themed_font("menu_small")
        loc_text = loc_font.render(f"Zona {self.hero.zone_id}", True, (150, 200, 255))
        surface.blit(loc_text, (x, y + loc_y_offset + int(height * 0.15)))

    def enter(self):
        """Chamado ao entrar no estado"""
        print(
            f"🎮 Entrando no jogo com {self.hero.name if self.hero else 'nenhum herói'}"
        )

    def exit(self):
        """Chamado ao sair do estado"""
        print("🎮 Saindo do jogo")

    def update(self):
        """Atualiza o estado do jogo"""
        # Atualiza botões do menu lateral
        ButtonManager.update_buttons(self.sidebar_buttons, self.game)

        # Atualiza botões dos menus se visíveis
        if self.show_menu:
            ButtonManager.update_buttons(self.menu_buttons, self.game)
        elif self.show_save_menu:
            ButtonManager.update_buttons(self.save_buttons, self.game)
        elif self.show_load_menu:
            ButtonManager.update_buttons(self.load_buttons, self.game)

    def render(self, surface):
        """Renderiza o estado do jogo"""
        # Limpa a tela
        surface.fill((0, 0, 0))

        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Calcula altura do HUD escalada
        hud_height_base = 200
        hud_height = self.game.ui_scaler.scale(hud_height_base, "y")

        game_area_height = screen_height - hud_height

        # Renderiza área do jogo
        self._render_game_area(surface, screen_width, game_area_height)

        # Renderiza HUD
        self._render_hud_phantasy_star(
            surface, screen_width, screen_height, game_area_height
        )

        # Renderiza sidebar
        self._render_sidebar(surface)

        # Overlays
        if self.show_menu:
            self._render_menu_overlay(surface)
        elif self.show_save_menu:
            self._render_save_menu(surface)
        elif self.show_load_menu:
            self._render_load_menu(surface)

        # Notificações
        self.game.notification_manager.render(surface)

    def _render_hud_phantasy_star(
        self, surface, screen_width, screen_height, game_area_height
    ):
        """Renderiza HUD horizontal inferior estilo Phantasy Star 1"""
        # Altura já calculada e passada via game_area_height (que é o Y inicial do HUD)
        hud_y = game_area_height
        hud_height = screen_height - hud_y

        # Fundo do HUD (cor sólida escura)
        hud_rect = pygame.Rect(0, hud_y, screen_width, hud_height)
        pygame.draw.rect(surface, (20, 20, 30), hud_rect)

        # Borda superior do HUD
        pygame.draw.line(surface, (100, 100, 150), (0, hud_y), (screen_width, hud_y), 3)

        # Divisão em seções (estilo Phantasy Star)
        section_width = screen_width // 4

        # Seção 1: Nome e Classe
        self._render_hud_section_name(
            surface, 20, hud_y + 20, section_width - 40, hud_height - 40
        )

        # Linha divisória
        pygame.draw.line(
            surface,
            (60, 60, 80),
            (section_width, hud_y + 10),
            (section_width, hud_y + hud_height - 10),
            2,
        )

        # Seção 2: HP e MP
        self._render_hud_section_vitals(
            surface, section_width + 20, hud_y + 20, section_width - 40, hud_height - 40
        )

        # Linha divisória
        pygame.draw.line(
            surface,
            (60, 60, 80),
            (section_width * 2, hud_y + 10),
            (section_width * 2, hud_y + hud_height - 10),
            2,
        )

        # Seção 3: Nível e Experiência
        self._render_hud_section_level(
            surface,
            section_width * 2 + 20,
            hud_y + 20,
            section_width - 40,
            hud_height - 40,
        )

        # Linha divisória
        pygame.draw.line(
            surface,
            (60, 60, 80),
            (section_width * 3, hud_y + 10),
            (section_width * 3, hud_y + hud_height - 10),
            2,
        )

        # Seção 4: Gold e Localização
        self._render_hud_section_extras(
            surface,
            section_width * 3 + 20,
            hud_y + 20,
            section_width - 40,
            hud_height - 40,
        )
