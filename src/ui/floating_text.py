import pygame


class FloatingText:
    def __init__(self, x, y, text, color, duration=1.0, speed_y=-30):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.timer = 0
        self.speed_y = speed_y
        self.alpha = 255

    def update(self, dt):
        self.timer += dt
        self.y += self.speed_y * dt

        # Fade out
        if self.timer > self.duration * 0.7:
            fade_duration = self.duration * 0.3
            fade_progress = (self.timer - (self.duration * 0.7)) / fade_duration
            self.alpha = max(0, 255 * (1 - fade_progress))

    def is_finished(self):
        return self.timer >= self.duration


class FloatingTextManager:
    def __init__(self, game):
        self.game = game
        self.texts = []
        self.font = (
            None  # Carregado sob demanda ou no init se game tiver assets prontos
        )

    def add_text(self, x, y, text, color=(255, 255, 255)):
        self.texts.append(FloatingText(x, y, text, color))

    def update(self):
        dt = self.game.clock.get_time() / 1000.0
        for text in self.texts[:]:
            text.update(dt)
            if text.is_finished():
                self.texts.remove(text)

    def render(self, surface):
        if not self.font:
            self.font = self.game.ui_scaler.get_themed_font("title")  # Fonte maior

        for text in self.texts:
            surf = self.font.render(text.text, True, text.color)
            surf.set_alpha(text.alpha)
            surface.blit(surf, (text.x - surf.get_width() // 2, text.y))
