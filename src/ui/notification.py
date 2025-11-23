# src/ui/notification.py
import pygame
import time


class NotificationManager:
    """Gerencia notificações em tela (toasts) - REFATORADO UIScaler"""

    def __init__(self, game):
        self.game = game
        self.notifications = []
        self.font = None

        # Acesso aos sistemas
        self.theme = game.game_config.theme
        self.ui_scaler = game.ui_scaler

    def add_notification(self, message, color=None, duration=3.0):
        """Adiciona uma nova notificação"""
        if color is None:
            color = self.theme.COLOR_TEXT_PRIMARY

        self.notifications.append(
            {
                "message": message,
                "color": color,
                "start_time": time.time(),
                "duration": duration,
                "alpha": 255,
            }
        )
        print(f"🔔 Notificação: {message}")  # Mantém log no terminal

    def update(self):
        """Atualiza estado das notificações"""
        current_time = time.time()

        # Remove notificações expiradas
        self.notifications = [
            n
            for n in self.notifications
            if current_time - n["start_time"] < n["duration"]
        ]

        # Atualiza transparência (fade out)
        for n in self.notifications:
            elapsed = current_time - n["start_time"]
            fade_time = 1.0
            if elapsed > n["duration"] - fade_time:  # Fade out no último segundo
                n["alpha"] = int(255 * (n["duration"] - elapsed) / fade_time)
            else:
                n["alpha"] = 255

    def render(self, surface):
        """Renderiza notificações na tela"""
        if not self.notifications:
            return

        if not self.font:
            self.font = self.ui_scaler.get_themed_font("menu")

        screen_width = surface.get_width()
        base_y_start = 50
        y_pos = self.ui_scaler.scale(base_y_start, "y")

        bg_padding_x = self.ui_scaler.scale(40, "x")
        bg_padding_y = self.ui_scaler.scale(20, "y")
        spacing = self.ui_scaler.scale(10, "y")

        for n in self.notifications:
            # Cria superfície de texto com alpha
            text_surface = self.font.render(n["message"], True, n["color"])
            text_surface.set_alpha(n["alpha"])

            # Fundo semi-transparente
            bg_rect = text_surface.get_rect(center=(screen_width // 2, y_pos))
            bg_rect.inflate_ip(bg_padding_x, bg_padding_y)

            bg_surface = pygame.Surface(
                (bg_rect.width, bg_rect.height), pygame.SRCALPHA
            )

            # Alpha do fundo proporcional ao alpha do texto
            bg_alpha = int(200 * (n["alpha"] / 255))
            bg_color = (*self.theme.COLOR_BG_MODAL, bg_alpha)
            bg_surface.fill(bg_color)

            # Borda
            border_color = (*self.theme.COLOR_BORDER_ACTIVE, n["alpha"])
            pygame.draw.rect(bg_surface, border_color, bg_surface.get_rect(), 2)

            surface.blit(bg_surface, bg_rect)
            surface.blit(text_surface, text_surface.get_rect(center=bg_rect.center))

            y_pos += bg_rect.height + spacing
