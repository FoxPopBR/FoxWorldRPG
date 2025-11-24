import pygame
import sys
import os

# Adiciona diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    pygame.init()

    # Configuração
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    ICON_SIZE = 32
    SCALE = 2  # Zoom para ver melhor
    DISPLAY_SIZE = ICON_SIZE * SCALE
    MARGIN = 10

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("FoxWorld RPG - Icon Atlas Viewer")

    # Carrega Atlas
    atlas_path = "assets/images/icons/icons_Drop_Shadow.png"
    if not os.path.exists(atlas_path):
        print(f"❌ Arquivo não encontrado: {atlas_path}")
        return

    try:
        atlas = pygame.image.load(atlas_path).convert_alpha()
    except Exception as e:
        print(f"❌ Erro ao carregar imagem: {e}")
        return

    atlas_w, atlas_h = atlas.get_size()
    rows = atlas_h // ICON_SIZE
    cols = atlas_w // ICON_SIZE

    print(f"Atlas Size: {atlas_w}x{atlas_h}")
    print(f"Grid: {rows} rows x {cols} cols")

    font = pygame.font.SysFont("Arial", 12)
    clock = pygame.time.Clock()

    scroll_y = 0
    max_scroll = max(
        0, (rows * (DISPLAY_SIZE + MARGIN)) - SCREEN_HEIGHT + 150
    )  # Mais margem no final

    running = True
    while running:
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * 30
                scroll_y = max(0, min(scroll_y, max_scroll))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Render
        screen.fill((30, 30, 30))

        # Desenha Grid
        start_y = 50 - scroll_y

        # Header
        header = font.render(
            f"Atlas: {atlas_path} | Grid: {rows}x{cols} | Use Scroll do Mouse",
            True,
            (255, 255, 255),
        )
        screen.blit(header, (10, 10))

        y = start_y
        for row in range(rows):
            x = MARGIN
            for col in range(cols):
                # Extrai ícone
                rect = pygame.Rect(
                    col * ICON_SIZE, row * ICON_SIZE, ICON_SIZE, ICON_SIZE
                )
                try:
                    icon = atlas.subsurface(rect)
                    scaled_icon = pygame.transform.scale(
                        icon, (DISPLAY_SIZE, DISPLAY_SIZE)
                    )

                    # Desenha ícone
                    screen.blit(scaled_icon, (x, y))
                    pygame.draw.rect(
                        screen, (100, 100, 100), (x, y, DISPLAY_SIZE, DISPLAY_SIZE), 1
                    )

                    # Desenha Coordenada
                    coord_text = font.render(f"{row},{col}", True, (200, 200, 200))
                    screen.blit(coord_text, (x + 5, y + DISPLAY_SIZE + 2))

                    x += DISPLAY_SIZE + MARGIN

                    # Quebra de linha se passar da largura
                    if x + DISPLAY_SIZE > SCREEN_WIDTH:
                        x = MARGIN
                        y += DISPLAY_SIZE + MARGIN + 20

                except ValueError:
                    pass  # Fim da imagem

            # Nova linha forçada se não quebrou antes
            if x != MARGIN:
                y += DISPLAY_SIZE + MARGIN + 20

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
