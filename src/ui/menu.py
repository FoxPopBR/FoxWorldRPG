"""
Menu Principal do FoxWorld RPG - Com efeitos visuais e botões com textura
"""

import pygame
import math
from src.ui.button import Button
from src.ui.ui_theme import get_theme
from src.ui.menu_assets import load_menu_visual_assets, render_menu_background
from src.ui.particles import ParticleSystem


class MainMenu:
    def __init__(self, game):
        self.game = game
        self.scaler = game.ui_scaler
        self.theme = get_theme()
        self.base_button_width = 400
        self.base_button_height = 70
        self.base_button_spacing = 90
        self.base_title_y = 20
        self.base_first_button_y = 620
        self.buttons = []
        self.focused_index = 0

        # Carrega assets visuais do menu usando helper
        self.menu_assets = load_menu_visual_assets(game)
        self.background_image = self.menu_assets["background"]
        self.button_image_normal = self.menu_assets["button_normal"]
        self.button_image_pressed = self.menu_assets["button_pressed"]

        # Carrega título separadamente
        self.title_image = None
        self._load_title_image()

        # Efeito de flash de tela cheia
        self.animation_time = 0
        self.flash_duration = 0.8
        self.flash_intensity = 0

        # Efeito de balanço suave do título
        self.floating_cycle = 4.0
        self.floating_amplitude = 4

        # Sistema de partículas (Restaurado)
        self.particle_system = ParticleSystem(count=60)

        self._create_ui()

    def _load_title_image(self):
        """Carrega apenas a imagem do título do jogo"""
        try:
            title_path = (
                self.game.game_config.resource_manager.assets_path
                / "images"
                / "titles"
                / "title_FoxWorldRPG.png"
            )
            if title_path.exists():
                self.title_image = pygame.image.load(str(title_path))
                if pygame.display.get_surface():
                    self.title_image = self.title_image.convert_alpha()
        except Exception as e:
            print(f"Erro ao carregar título: {e}")

    def _create_ui(self):
        """Cria os botões do menu"""
        self.buttons.clear()
        base_x = (self.theme.BASE_WIDTH - self.base_button_width) // 2

        button_configs = [
            ("Novo Jogo", self._new_game),
            ("Continuar", self._continue_game),
            ("Configurações", self._settings),
            ("Sair", self._quit),
        ]

        for i, (text, action) in enumerate(button_configs):
            self.buttons.append(
                Button(
                    base_x,
                    self.base_first_button_y + i * self.base_button_spacing,
                    self.base_button_width,
                    self.base_button_height,
                    text,
                    action,
                    font_size=self.theme.FONT_MENU_LARGE,
                    text_color=(255, 255, 255),
                    button_image_normal=self.button_image_normal,
                    button_image_pressed=self.button_image_pressed,
                )
            )

    def _new_game(self):
        from src.states.game_slot_select_state import GameSlotSelectState

        self.game.state_manager.change_state(GameSlotSelectState(self.game))

    def _continue_game(self):
        from src.states.game_slot_select_state import GameSlotSelectState

        self.game.state_manager.change_state(GameSlotSelectState(self.game))

    def _settings(self):
        from src.states.settings_state import SettingsState

        self.game.state_manager.push_state(SettingsState(self.game))

    def _quit(self):
        self.game.running = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_RETURN:
                self._new_game()
            elif event.key == pygame.K_DOWN:
                self._focus_next_button()
            elif event.key == pygame.K_UP:
                self._focus_previous_button()

        for button in self.buttons:
            if button.handle_event(event):
                break

    def _focus_next_button(self):
        self.focused_index = (self.focused_index + 1) % len(self.buttons)

    def _focus_previous_button(self):
        self.focused_index = (self.focused_index - 1) % len(self.buttons)

    def update(self):
        dt = 1.0 / 60.0
        self.animation_time += dt
        mouse_pos = pygame.mouse.get_pos()

        # Atualiza partículas
        self.particle_system.update_dimensions(
            self.theme.BASE_WIDTH, self.theme.BASE_HEIGHT
        )
        self.particle_system.update()

        # Atualiza animação de flash
        if self.flash_intensity > 0:
            self.flash_intensity -= dt / self.flash_duration
            if self.flash_intensity < 0:
                self.flash_intensity = 0

        # Atualiza botões
        for button in self.buttons:
            button.update(mouse_pos, dt=dt)

    def render(self, surface):
        sw, sh = surface.get_width(), surface.get_height()

        # Renderiza background SEM escurecimento (darkness=0)
        render_menu_background(surface, self.background_image, self.theme, darkness=0.0)

        # Renderiza partículas
        self.particle_system.render(surface)

        # Renderiza título com balanço
        if self.title_image:
            title_scaled = self.scaler.scale_image(
                self.title_image, target_width=int(sw * 0.52)
            )
            tx = (sw - title_scaled.get_width()) // 2
            ty = self.scaler.scale(self.base_title_y, "y") + self._get_floating_offset()
            surface.blit(title_scaled, (tx, ty))
        else:
            # Fallback de texto
            font = self.scaler.get_themed_font("title")
            text = font.render("FOXWORLD RPG", True, self.theme.COLOR_TEXT_PRIMARY)
            surface.blit(
                text,
                text.get_rect(
                    center=(sw // 2, self.scaler.scale(self.base_title_y, "y"))
                ),
            )

        # Renderiza botões
        for button in self.buttons:
            button.render(surface)

        # Renderiza flash de tela cheia por último (sobre tudo)
        if self.flash_intensity > 0:
            self._render_screen_flash(surface, self.flash_intensity)

    def _render_screen_flash(self, surface, intensity):
        """Renderiza um flash de tela cheia suave"""
        flash_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        color = (255, 245, 220, int(intensity))
        flash_surface.fill(color)
        surface.blit(flash_surface, (0, 0))

    def _get_floating_offset(self):
        """Calcula o deslocamento vertical do balanço"""
        angle = (
            (self.animation_time % self.floating_cycle)
            / self.floating_cycle
            * 2
            * math.pi
        )
        return int(self.scaler.scale(math.sin(angle) * self.floating_amplitude, "y"))
