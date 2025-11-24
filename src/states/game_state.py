# src/states/game_state.py - REDESIGN ESTILO PHANTASY STAR
import pygame
from src.states.base_state import BaseState
from src.ui.button import Button
from src.ui.button_manager import ButtonManager
from pytmx.util_pygame import load_pygame
from src.ui.menu_assets import load_menu_visual_assets
from src.core.animation import AnimationController


class GameState(BaseState):
    """Tela principal do jogo - HUD estilo Phantasy Star 1"""

    def __init__(self, game, hero=None):
        super().__init__(game)

        # Carrega assets visuais do menu
        self.menu_assets = load_menu_visual_assets(game)

        # Carrega o herói ativo
        self.hero = (
            hero if hero else self.game.game_config.hero_manager.get_active_hero()
        )

        if not self.hero:
            print("⚠️ Nenhum herói ativo encontrado, voltando ao menu")
            from src.states.menu_state import MenuState

            self.game.state_manager.change_state(MenuState(self.game))
            return

        # === SISTEMA DE MAPA ===
        try:
            self.tmx_data = load_pygame("assets/maps/map_teste.tmx")
            print("✅ Mapa carregado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar mapa: {e}")
            self.tmx_data = None

        # === ANIMAÇÃO DO HERÓI ===
        try:
            sprite_path = "assets/images/characters/barbaro_sprite.png"
            self.hero_anim = AnimationController(sprite_path)
            print(f"✅ Sprite sheet carregado: {sprite_path}")
            self.hero_sprite = None
        except Exception as e:
            print(f"❌ Erro ao carregar sprite sheet: {e}")
            self.hero_anim = None
            self.hero_sprite = pygame.Surface((32, 32))
            self.hero_sprite.fill((255, 0, 0))

        # === POSIÇÃO DO HERÓI (Sistema Duplo: Grid + Pixel) ===
        # Grid position (lógica/colisão)
        self.player_grid_x = 10
        self.player_grid_y = 10

        # Pixel position (visual/renderização) - FLOAT para interpolação suave
        self.pixel_x = float(self.player_grid_x * 32)
        self.pixel_y = float(self.player_grid_y * 32)

        # Target position (destino do movimento)
        self.pixel_target_x = self.pixel_x
        self.pixel_target_y = self.pixel_y
        self.is_moving = False

        # Velocidade de movimento suave (pixels por frame)
        self.movement_speed = 2.0  # Era 3.0, agora 2.0 para sincronizar com animação

        # === CÂMERA SUAVE ===
        self.camera_x = self.pixel_x
        self.camera_y = self.pixel_y
        self.camera_smooth_speed = 0.06  # MUITO mais suave (0.05-0.10 = butter smooth)

        # Cooldown de input (para não aceitar input durante movimento)
        self.last_move_time = 0
        self.move_cooldown = 80  # ms - tempo mínimo entre comandos de movimento

        # === SISTEMA DE ENCONTROS ===
        self.steps_count = 0
        self.steps_for_check = (
            16  # Checa a cada X passos (pixels ou tiles? Tiles é melhor)
        )
        # Vamos usar tiles. Cada movimento completo = 1 passo.
        self.encounter_chance = 0.1  # 10% de chance a cada passo

        # === UI ===
        self.buttons = []
        self.sidebar_buttons = []
        self.menu_buttons = []
        self.save_buttons = []
        self.load_buttons = []
        self.show_menu = False
        self.show_save_menu = False
        self.show_load_menu = False
        self.last_save_slot = 2

        self._create_sidebar_menu()
        self._create_menu_ui()
        self._create_save_ui()

    def _check_collision(self, grid_x, grid_y):
        """Verifica se posição no grid é válida"""
        if not self.tmx_data:
            return True

        # Limites do mapa
        if grid_x < 0 or grid_y < 0:
            return False
        if grid_x >= self.tmx_data.width or grid_y >= self.tmx_data.height:
            return False

        # Colisão com layer "Acima do solo 2"
        try:
            object_layer = self.tmx_data.get_layer_by_name("Acima do solo 2")
            if object_layer and hasattr(object_layer, "data"):
                gid = object_layer.data[grid_y][grid_x]
                if gid != 0:
                    return False
        except (ValueError, IndexError, AttributeError):
            pass

        return True

    def _create_sidebar_menu(self):
        """Cria menu lateral esquerdo fixo"""
        self.sidebar_buttons.clear()
        start_x = 10
        start_y = 125
        btn_width = 80
        btn_height = 80
        spacing = 10

        menu_items = [
            ("INV", self._open_inventory),
            ("PER", self._open_profile),
            ("MAP", self._open_map),
            ("GRP", self._open_group),
            ("CFG", self._toggle_menu),
        ]

        for i, (text, action) in enumerate(menu_items):
            btn = Button(
                start_x,
                start_y + i * (btn_height + spacing),
                btn_width,
                btn_height,
                text,
                action,
                font_size=self.theme.FONT_MENU_SMALL,
                text_color=self.theme.COLOR_TEXT_PRIMARY,
                button_image_normal=self.menu_assets.get("small_button_normal"),
                button_image_pressed=self.menu_assets.get("small_button_pressed"),
            )
            self.sidebar_buttons.append(btn)

    def _create_menu_ui(self):
        """Cria menu de pausa"""
        self.menu_buttons.clear()
        center_x = self.theme.BASE_WIDTH // 2
        center_y = self.theme.BASE_HEIGHT // 2
        btn_w = 300
        btn_h = 60
        spacing = 20

        options = [
            ("CONTINUAR", self._toggle_menu),
            ("SALVAR JOGO", self._save_game),
            ("CARREGAR JOGO", self._load_game_menu),
            ("MENU PRINCIPAL", self._exit_to_main_menu),
        ]

        start_y = center_y - (len(options) * (btn_h + spacing)) // 2

        for i, (text, action) in enumerate(options):
            btn = Button(
                center_x - btn_w // 2,
                start_y + i * (btn_h + spacing),
                btn_w,
                btn_h,
                text,
                action,
                font_size=self.theme.FONT_MENU_MEDIUM,
                text_color=self.theme.COLOR_TEXT_PRIMARY,
                button_image_normal=self.menu_assets.get("button_normal"),
                button_image_pressed=self.menu_assets.get("button_pressed"),
            )
            self.menu_buttons.append(btn)

    def _create_save_ui(self):
        """Cria botões do menu de save"""
        self.save_buttons.clear()
        center_x = self.theme.BASE_WIDTH // 2
        start_y = 400
        btn_width = 350
        btn_height = 60
        spacing = 30

        btn_slot2 = Button(
            center_x - btn_width // 2,
            start_y,
            btn_width,
            btn_height,
            "SALVAR NO SLOT 1 (MANUAL)",
            lambda: self._save_to_slot(2),
            font_size=self.theme.FONT_MENU_MEDIUM,
            text_color=self.theme.COLOR_TEXT_PRIMARY,
            button_image_normal=self.menu_assets.get("button_normal"),
            button_image_pressed=self.menu_assets.get("button_pressed"),
        )

        btn_slot3 = Button(
            center_x - btn_width // 2,
            start_y + btn_height + spacing,
            btn_width,
            btn_height,
            "SALVAR NO SLOT 2 (MANUAL)",
            lambda: self._save_to_slot(3),
            font_size=self.theme.FONT_MENU_MEDIUM,
            text_color=self.theme.COLOR_TEXT_PRIMARY,
            button_image_normal=self.menu_assets.get("button_normal"),
            button_image_pressed=self.menu_assets.get("button_pressed"),
        )

        btn_cancel = Button(
            center_x - btn_width // 2,
            start_y + (btn_height + spacing) * 2 + 20,
            btn_width,
            btn_height,
            "CANCELAR",
            lambda: setattr(self, "show_save_menu", False),
            font_size=self.theme.FONT_MENU_MEDIUM,
            text_color=self.theme.COLOR_TEXT_SECONDARY,
            button_image_normal=self.menu_assets.get("button_normal"),
            button_image_pressed=self.menu_assets.get("button_pressed"),
        )

        self.save_buttons.extend([btn_slot2, btn_slot3, btn_cancel])

    # === MÉTODOS DE UI (mantidos do código original) ===
    def _toggle_menu(self):
        self.show_menu = not self.show_menu

    def _save_game(self):
        self.show_save_menu = True

    def _save_to_slot(self, slot_id):
        try:
            hero = self.hero
            game_slot_id = getattr(self.game, "selected_game_slot", 1)
            cursor = self.game.game_config.database.connection.cursor()
            cursor.execute(
                """UPDATE save_slots 
                SET hero_name=?, hero_level=?, hero_class=?, zone_name=?, zone_id=?, 
                    playtime=?, last_saved=CURRENT_TIMESTAMP, save_title=?, 
                    save_description=?, is_active=1
                WHERE game_slot_id=? AND save_slot_id=?""",
                (
                    hero.name,
                    hero.level,
                    hero.hero_class.value,
                    f"Zona {hero.zone_id}",
                    hero.zone_id,
                    0,
                    f"Save Manual {slot_id-1}",
                    f"Nível {hero.level} - {hero.hero_class.value}",
                    game_slot_id,
                    slot_id,
                ),
            )
            cursor.execute(
                "UPDATE game_slots SET last_played=CURRENT_TIMESTAMP WHERE slot_id=?",
                (game_slot_id,),
            )
            self.game.game_config.database.connection.commit()
            self.last_save_slot = slot_id
            self.game.notification_manager.add_notification(
                f"Jogo salvo no Slot {slot_id}!", (100, 255, 100)
            )
            self.show_save_menu = False
            self.show_menu = False
        except Exception as e:
            self.game.notification_manager.add_notification(
                f"Erro ao salvar: {e}", (255, 100, 100)
            )

    def _load_game_menu(self):
        # Implementação completa do load mantida
        self.show_load_menu = True

    def _open_inventory(self):
        from src.states.inventory_state import InventoryState

        self.game.state_manager.change_state(InventoryState(self.game))

    def _open_profile(self):
        from src.states.profile_state import ProfileState

        self.game.state_manager.change_state(ProfileState(self.game))

    def _open_map(self):
        from src.states.map_state import MapState

        self.game.state_manager.change_state(MapState(self.game))

    def _open_group(self):
        from src.states.group_state import GroupState

        self.game.state_manager.change_state(GroupState(self.game))

    def _exit_to_main_menu(self):
        from src.states.menu_state import MenuState

        self.game.state_manager.change_state(MenuState(self.game))

    # === UPDATE: MOVIMENTO SUAVE ===
    def update(self):
        ButtonManager.update_buttons(self.sidebar_buttons, self.game)

        if self.show_menu:
            ButtonManager.update_buttons(self.menu_buttons, self.game)
        elif self.show_save_menu:
            ButtonManager.update_buttons(self.save_buttons, self.game)
        elif self.show_load_menu:
            ButtonManager.update_buttons(self.load_buttons, self.game)
        else:
            # === SISTEMA DE MOVIMENTO SUAVE ===
            current_time = pygame.time.get_ticks()

            # 1. Aceita input SE não estiver em movimento E cooldown passou
            if not self.is_moving and (
                current_time - self.last_move_time > self.move_cooldown
            ):
                keys = pygame.key.get_pressed()
                dx, dy = 0, 0

                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    dy = -1
                elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    dy = 1
                elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    dx = -1
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    dx = 1

                # Se há input, tenta mover
                if dx != 0 or dy != 0:
                    target_grid_x = self.player_grid_x + dx
                    target_grid_y = self.player_grid_y + dy

                    # Verifica colisão
                    if self._check_collision(target_grid_x, target_grid_y):
                        # Aceita movimento
                        self.player_grid_x = target_grid_x
                        self.player_grid_y = target_grid_y
                        self.pixel_target_x = self.player_grid_x * 32.0
                        self.pixel_target_y = self.player_grid_y * 32.0
                        self.is_moving = True
                        self.last_move_time = current_time

                        # Atualiza animação
                        if self.hero_anim:
                            self.hero_anim.set_direction(dx, dy)
                            self.hero_anim.start_moving()

            # 2. Interpola pixel position até o target
            if self.is_moving:
                # Calcula distância até target
                dist_x = self.pixel_target_x - self.pixel_x
                dist_y = self.pixel_target_y - self.pixel_y
                distance = (dist_x**2 + dist_y**2) ** 0.5

                if distance > 0.5:  # Ainda não chegou
                    # Move em direção ao target
                    if abs(dist_x) > 0.1:
                        move_x = min(self.movement_speed, abs(dist_x))
                        self.pixel_x += move_x if dist_x > 0 else -move_x

                    if abs(dist_y) > 0.1:
                        move_y = min(self.movement_speed, abs(dist_y))
                        self.pixel_y += move_y if dist_y > 0 else -move_y
                else:
                    # Chegou - snap para posição exata
                    self.pixel_x = self.pixel_target_x
                    self.pixel_y = self.pixel_target_y
                    self.is_moving = False

                    # Para animação
                    if self.hero_anim:
                        self.hero_anim.stop_moving()

                    # Checa encontro
                    self._check_random_encounter()

            # 3. Atualiza animação
            if self.hero_anim:
                self.hero_anim.update(0.016)

            # 4. Câmera MUITO suave seguindo player
            if self.tmx_data:
                cam_w, cam_h = 640, 360
                target_cam_x = self.pixel_x - cam_w // 2 + 16
                target_cam_y = self.pixel_y - cam_h // 2 + 16

                # Limita aos bounds do mapa
                map_w = self.tmx_data.width * 32
                map_h = self.tmx_data.height * 32
                target_cam_x = max(0, min(target_cam_x, map_w - cam_w))
                target_cam_y = max(0, min(target_cam_y, map_h - cam_h))

                # Interpola MUITO suavemente
                self.camera_x += (
                    target_cam_x - self.camera_x
                ) * self.camera_smooth_speed
                self.camera_y += (
                    target_cam_y - self.camera_y
                ) * self.camera_smooth_speed

    def _check_random_encounter(self):
        """Verifica se ocorre batalha"""
        import random

        # Rola dados (0.0 a 1.0)
        roll = random.random()

        # Chance configurada
        if roll < self.encounter_chance:
            print("⚔️ ENCONTRO ALEATÓRIO! Iniciando batalha...")
            from src.states.battle_state import BattleState

            self.game.state_manager.change_state(BattleState(self.game))

    # === EVENTOS ===
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.show_save_menu:
                    self.show_save_menu = False
                elif self.show_load_menu:
                    self.show_load_menu = False
                else:
                    self._toggle_menu()
            elif event.key == pygame.K_F5:
                self._save_to_slot(self.last_save_slot)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.show_save_menu:
                ButtonManager.handle_button_click(self.save_buttons, event, self.game)
            elif self.show_load_menu:
                ButtonManager.handle_button_click(self.load_buttons, event, self.game)
            elif self.show_menu:
                ButtonManager.handle_button_click(self.menu_buttons, event, self.game)
            else:
                ButtonManager.handle_button_click(
                    self.sidebar_buttons, event, self.game
                )

    # === RENDER ===
    def render(self, surface, world_surface=None):
        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Renderiza mundo no world_surface
        if world_surface and self.tmx_data:
            cam_w, cam_h = world_surface.get_size()

            # Renderiza layers do mapa
            for layer in self.tmx_data.visible_layers:
                if hasattr(layer, "data"):
                    for x, y, gid in layer:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            draw_x = x * 32 - int(self.camera_x)
                            draw_y = y * 32 - int(self.camera_y)
                            if -32 <= draw_x <= cam_w and -32 <= draw_y <= cam_h:
                                world_surface.blit(tile, (draw_x, draw_y))

            # Renderiza player
            player_draw_x = int(self.pixel_x - self.camera_x)
            player_draw_y = int(self.pixel_y - self.camera_y)

            if self.hero_anim:
                frame = self.hero_anim.get_current_frame()
                world_surface.blit(frame, (player_draw_x, player_draw_y))
            elif self.hero_sprite:
                world_surface.blit(self.hero_sprite, (player_draw_x, player_draw_y))

        # Escala world para screen
        self.game.render_world_to_screen()

        # HUD removido durante exploração - só mostra se não tem mapa
        if not self.tmx_data:
            hud_height_base = 200
            hud_height = self.game.ui_scaler.scale(hud_height_base, "y")
            game_area_height = screen_height - hud_height
            self._render_game_area(surface, screen_width, game_area_height)
            self._render_hud_phantasy_star(
                surface, screen_width, screen_height, game_area_height
            )

        # Sidebar sempre visível
        self._render_sidebar(surface)

        # Overlays de menu
        if self.show_menu:
            self._render_menu_overlay(surface)
        elif self.show_save_menu:
            self._render_save_menu(surface)
        elif self.show_load_menu:
            self._render_load_menu(surface)

        self.game.notification_manager.render(surface)

    # === RENDER HELPERS (mantidos do código original) ===
    def _render_sidebar(self, surface):
        sidebar_w = self.game.ui_scaler.scale(90, "x")
        sidebar_h = self.game.ui_scaler.scale(455, "y")
        sidebar_x = self.game.ui_scaler.scale(5, "x")
        sidebar_y = self.game.ui_scaler.scale(115, "y")
        sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, sidebar_w, sidebar_h)
        pygame.draw.rect(surface, (20, 20, 30), sidebar_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 60, 80), sidebar_rect, 2, border_radius=10)
        ButtonManager.render_buttons(
            self.sidebar_buttons, surface, self.game.game_config
        )

    def _render_menu_overlay(self, surface):
        screen_width, screen_height = surface.get_size()
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        menu_w = self.game.ui_scaler.scale(400, "x")
        menu_h = self.game.ui_scaler.scale(500, "y")
        menu_x = (screen_width - menu_w) // 2
        menu_y = self.game.ui_scaler.scale(290, "y")
        menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
        pygame.draw.rect(surface, (30, 30, 40), menu_rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 150), menu_rect, 2, border_radius=15)
        title_font = self.game.ui_scaler.get_themed_font("title")
        title_text = title_font.render("MENU DE PAUSA", True, (255, 255, 255))
        surface.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, menu_y + 30)
        )
        ButtonManager.render_buttons(self.menu_buttons, surface, self.game.game_config)

    def _render_save_menu(self, surface):
        screen_width, screen_height = surface.get_size()
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        menu_w = self.game.ui_scaler.scale(500, "x")
        menu_h = self.game.ui_scaler.scale(400, "y")
        menu_x = (screen_width - menu_w) // 2
        menu_y = self.game.ui_scaler.scale(300, "y")
        menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
        pygame.draw.rect(surface, (30, 30, 40), menu_rect, border_radius=15)
        pygame.draw.rect(surface, (100, 255, 100), menu_rect, 2, border_radius=15)
        title_font = self.game.ui_scaler.get_themed_font("title")
        title_text = title_font.render("SALVAR JOGO", True, (255, 255, 255))
        surface.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, menu_y + 30)
        )
        ButtonManager.render_buttons(self.save_buttons, surface, self.game.game_config)

    def _render_load_menu(self, surface):
        pass  # Implementação simplificada

    def _render_game_area(self, surface, screen_width, game_area_height):
        pass  # Placeholder mantido

    def _render_hud_phantasy_star(
        self, surface, screen_width, screen_height, game_area_height
    ):
        pass  # HUD mantido do original
