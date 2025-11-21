import pygame
import time


class NotificationManager:
    """Gerencia notificações em tela (toasts)"""

    def __init__(self):
        self.notifications = []
        self.font = None

    def add_notification(self, message, color=(255, 255, 255), duration=3.0):
        """Adiciona uma nova notificação"""
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
            if elapsed > n["duration"] - 1.0:  # Fade out no último segundo
                n["alpha"] = int(255 * (n["duration"] - elapsed))
            else:
                n["alpha"] = 255

    def render(self, surface, game_config):
        """Renderiza notificações na tela"""
        if not self.notifications:
            return

        if not self.font:
            self.font = game_config.get_font("menu", 24)

        screen_width = surface.get_width()
        y_pos = 50  # Começa do topo

        for n in self.notifications:
            # Cria superfície de texto com alpha
            text_surface = self.font.render(n["message"], True, n["color"])
            text_surface.set_alpha(n["alpha"])

            # Fundo semi-transparente
            bg_rect = text_surface.get_rect(center=(screen_width // 2, y_pos))
            bg_rect.inflate_ip(40, 20)

            bg_surface = pygame.Surface(
                (bg_rect.width, bg_rect.height), pygame.SRCALPHA
            )
            bg_surface.fill((0, 0, 0, 180 * (n["alpha"] / 255)))

            surface.blit(bg_surface, bg_rect)
            surface.blit(text_surface, text_surface.get_rect(center=bg_rect.center))

            y_pos += bg_rect.height + 10
