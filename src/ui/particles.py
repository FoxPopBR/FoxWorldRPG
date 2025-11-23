import pygame
import random
import math


class Particle:
    def __init__(self, x, y, screen_width, screen_height, textures):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.textures = textures
        self.reset(x, y, first_spawn=True)

    def reset(self, x=None, y=None, first_spawn=False):
        if x is None:
            self.x = random.randint(0, self.screen_width)
            if first_spawn:
                self.y = random.randint(0, self.screen_height)
            else:
                self.y = self.screen_height + random.randint(10, 50)
        else:
            self.x = x
            self.y = y

        # Pick a random texture type to ensure VARIETY
        # We have 4 types, so this ensures a mix on screen
        self.texture_idx = random.randint(0, len(self.textures) - 1)

        self.speed_y = random.uniform(-0.2, -0.6)  # Slow float
        self.speed_x = random.uniform(-0.1, 0.1)

        self.life = 255
        self.decay = random.uniform(0.1, 0.3)  # Long life

        # Pulse properties - VERY SLOW to avoid blinking
        self.pulse_speed = random.uniform(0.002, 0.005)
        self.pulse_offset = random.uniform(0, 6.28)

        # Transparency range (10% to 80%)
        self.min_alpha = 25
        self.max_alpha = 204

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= self.decay

        if self.life <= 0 or self.y < -20:
            self.reset()

    def render(self, surface):
        # Smooth Sine Pulse
        # sin() goes -1 to 1. +1 -> 0 to 2. /2 -> 0 to 1.
        pulse = (
            math.sin(pygame.time.get_ticks() * self.pulse_speed + self.pulse_offset) + 1
        ) / 2

        # Map pulse to alpha range
        current_alpha = self.min_alpha + (self.max_alpha - self.min_alpha) * pulse

        # Fade out at end of life
        if self.life < 50:
            current_alpha *= self.life / 50.0

        current_alpha = int(current_alpha)
        if current_alpha < 5:
            return

        # Get the texture
        tex = self.textures[self.texture_idx]

        # Apply alpha
        tex.set_alpha(current_alpha)

        # Center the texture
        w, h = tex.get_size()
        surface.blit(tex, (int(self.x - w // 2), int(self.y - h // 2)))


class ParticleSystem:
    def __init__(self, count=120):
        self.particles = []
        self.count = count
        self.screen_width = 1920
        self.screen_height = 1080
        self.textures = []
        self._generate_textures()

    def _generate_textures(self):
        # Generate textures with EXPLICIT LIGHT RAYS
        # Slightly larger canvas (11x11 to 15x15) to allow rays to extend

        colors = [(255, 255, 255), (255, 250, 200), (200, 240, 255)]

        for color in colors:
            # 1. Starburst (Cross Rays)
            # Canvas 13x13
            s = pygame.Surface((13, 13), pygame.SRCALPHA)
            c = 6
            # Long horizontal ray (faint)
            pygame.draw.line(s, (*color, 100), (0, c), (12, c), 1)
            # Long vertical ray (faint)
            pygame.draw.line(s, (*color, 100), (c, 0), (c, 12), 1)
            # Core glow (brighter)
            pygame.draw.circle(s, (*color, 150), (c, c), 3)
            # Center point (solid)
            s.set_at((c, c), (*color, 255))
            self.textures.append(s)

            # 2. X-Ray (Diagonal Rays)
            s = pygame.Surface((11, 11), pygame.SRCALPHA)
            c = 5
            # Diagonals
            pygame.draw.line(s, (*color, 100), (0, 0), (10, 10), 1)
            pygame.draw.line(s, (*color, 100), (10, 0), (0, 10), 1)
            # Core
            pygame.draw.circle(s, (*color, 180), (c, c), 2)
            s.set_at((c, c), (*color, 255))
            self.textures.append(s)

            # 3. Diamond Flare
            s = pygame.Surface((9, 9), pygame.SRCALPHA)
            c = 4
            # Diamond shape filled with low alpha
            pygame.draw.polygon(s, (*color, 80), [(c, 0), (8, c), (c, 8), (0, c)])
            # Inner diamond brighter
            pygame.draw.polygon(s, (*color, 150), [(c, 2), (6, c), (c, 6), (2, c)])
            # Core
            s.set_at((c, c), (*color, 255))
            self.textures.append(s)

            # 4. Soft Orb (No rays, just glow)
            s = pygame.Surface((9, 9), pygame.SRCALPHA)
            c = 4
            # Outer glow
            pygame.draw.circle(s, (*color, 50), (c, c), 4)
            # Mid glow
            pygame.draw.circle(s, (*color, 100), (c, c), 2)
            # Core
            s.set_at((c, c), (*color, 255))
            self.textures.append(s)

    def update_dimensions(self, width, height):
        self.screen_width = width
        self.screen_height = height

        if not self.particles:
            for _ in range(self.count):
                self.particles.append(
                    Particle(
                        random.randint(0, width),
                        random.randint(0, height),
                        width,
                        height,
                        self.textures,
                    )
                )

    def update(self):
        for p in self.particles:
            p.update()

    def render(self, surface):
        for p in self.particles:
            p.render(surface)
