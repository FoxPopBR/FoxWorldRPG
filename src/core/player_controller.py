import pygame


class PlayerController:
    """Controlador de movimento do jogador (Grid-based)"""

    TILE_SIZE = 64  # Tamanho do tile em pixels
    MOVE_DELAY = 150  # Delay entre movimentos em ms

    def __init__(self, x, y, bounds_rect):
        self.grid_x = x
        self.grid_y = y
        self.bounds = bounds_rect
        self.last_move_time = 0
        self.is_moving = False

        # Posição visual (pixel)
        self.pixel_x = x * self.TILE_SIZE
        self.pixel_y = y * self.TILE_SIZE
        self.target_pixel_x = self.pixel_x
        self.target_pixel_y = self.pixel_y

        # Velocidade de interpolação (pixels por frame)
        self.move_speed = 8

    def handle_input(self):
        """Processa input de movimento"""
        if self.is_moving:
            return

        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        if current_time - self.last_move_time < self.MOVE_DELAY:
            return

        dx, dy = 0, 0

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1

        if dx != 0 or dy != 0:
            self._try_move(dx, dy)
            self.last_move_time = current_time

    def _try_move(self, dx, dy):
        """Tenta mover para a nova posição no grid"""
        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy

        # Verifica limites do mapa (em coordenadas de grid)
        # Bounds está em pixels, converter para grid
        min_grid_x = 0
        min_grid_y = 0
        max_grid_x = (self.bounds.width // self.TILE_SIZE) - 1
        max_grid_y = (self.bounds.height // self.TILE_SIZE) - 1

        if (
            min_grid_x <= new_grid_x <= max_grid_x
            and min_grid_y <= new_grid_y <= max_grid_y
        ):

            self.grid_x = new_grid_x
            self.grid_y = new_grid_y
            self.target_pixel_x = self.grid_x * self.TILE_SIZE
            self.target_pixel_y = self.grid_y * self.TILE_SIZE
            self.is_moving = True

    def update(self):
        """Atualiza posição visual (interpolação)"""
        if not self.is_moving:
            return

        # Move em direção ao alvo
        if self.pixel_x < self.target_pixel_x:
            self.pixel_x = min(self.pixel_x + self.move_speed, self.target_pixel_x)
        elif self.pixel_x > self.target_pixel_x:
            self.pixel_x = max(self.pixel_x - self.move_speed, self.target_pixel_x)

        if self.pixel_y < self.target_pixel_y:
            self.pixel_y = min(self.pixel_y + self.move_speed, self.target_pixel_y)
        elif self.pixel_y > self.target_pixel_y:
            self.pixel_y = max(self.pixel_y - self.move_speed, self.target_pixel_y)

        # Verifica se chegou
        if self.pixel_x == self.target_pixel_x and self.pixel_y == self.target_pixel_y:
            self.is_moving = False

    def render(self, surface, offset_x, offset_y):
        """Renderiza o jogador (quadrado placeholder por enquanto)"""
        rect = pygame.Rect(
            offset_x + self.pixel_x,
            offset_y + self.pixel_y,
            self.TILE_SIZE,
            self.TILE_SIZE,
        )
        pygame.draw.rect(surface, (0, 255, 0), rect)  # Verde = Jogador
        pygame.draw.rect(surface, (255, 255, 255), rect, 2)  # Borda branca
