import pygame


class SpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
            self.sheet_w = self.sheet.get_width()
            self.sheet_h = self.sheet.get_height()

            # Assume 4x4 grid for now, or calculate based on standard sizes
            # If 4x4, frame size is w/4, h/4
            self.cols = 4
            self.rows = 4
            self.frame_w = self.sheet_w // self.cols
            self.frame_h = self.sheet_h // self.rows

        except Exception as e:
            print(f"❌ Erro ao carregar sprite sheet {filename}: {e}")
            raise e

    def get_image(self, col, row):
        x = col * self.frame_w
        y = row * self.frame_h
        rect = pygame.Rect(x, y, self.frame_w, self.frame_h)
        image = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        return image


class AnimationController:
    def __init__(
        self, sprite_sheet_path, animation_speed=120
    ):  # 120ms = metade da velocidade (era 60)
        self.sprite_sheet = SpriteSheet(sprite_sheet_path)
        self.animation_speed = animation_speed
        self.current_time = 0
        self.frame_index = 0
        self.direction = "down"  # down, up, right, left
        self.is_moving = False

        # Mapeamento de linhas (Baseado na imagem fornecida)
        # Row 0: Down (Front)
        # Row 1: Up (Back)
        # Row 2: Right
        # Row 3: Left
        self.row_map = {"down": 0, "up": 1, "right": 2, "left": 3}

        self.frames = {"down": [], "up": [], "right": [], "left": []}
        self._load_frames()

    def _load_frames(self):
        for direction, row in self.row_map.items():
            for col in range(self.sprite_sheet.cols):
                self.frames[direction].append(self.sprite_sheet.get_image(col, row))

    def update(self, dt):
        if self.is_moving:
            self.current_time += dt * 1000  # dt em segundos para ms
            if self.current_time >= self.animation_speed:
                self.current_time = 0
                # Ciclo de caminhada: 1 → 2 → 3 → 1 (pula frame 0 que é idle)
                if self.frame_index == 0:
                    self.frame_index = 1
                else:
                    # Cicla entre 1, 2, 3
                    self.frame_index = ((self.frame_index - 1 + 1) % 3) + 1
        else:
            self.frame_index = 0  # Frame parado (primeiro da linha)
            self.current_time = 0

    def get_current_frame(self):
        return self.frames[self.direction][self.frame_index]

    def set_direction(self, dx, dy):
        if dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"
        elif dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"

    def start_moving(self):
        self.is_moving = True

    def stop_moving(self):
        self.is_moving = False
