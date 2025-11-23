"""
Helper para carregar assets visuais padrão do menu
Usado em todas as telas relacionadas ao menu principal
"""

import pygame


def load_menu_visual_assets(game):
    """
    Carrega assets visuais padrão do menu (background e botões)
    usando o ThemeManager para resolver os caminhos.

    Returns:
        dict com 'background', 'button_normal', 'button_pressed',
        'small_button_normal', 'small_button_pressed'
    """
    assets = {
        "background": None,
        "button_normal": None,
        "button_pressed": None,
        "small_button_normal": None,
        "small_button_pressed": None,
    }

    try:
        # Obtém o ThemeManager do jogo
        # Se não existir no objeto game, tenta importar (fallback)
        theme_manager = getattr(game, "theme_manager", None)

        if not theme_manager:
            from src.ui.theme_manager import ThemeManager

            theme_manager = ThemeManager()
            print(
                "⚠️ ThemeManager criado localmente em load_menu_visual_assets (não encontrado em game)"
            )

        assets_path = game.game_config.resource_manager.assets_path

        # Mapeamento de chaves do ThemeManager para chaves do dicionário local
        key_map = {
            "menu_background": "background",
            "button_normal": "button_normal",
            "button_pressed": "button_pressed",
            "small_button_normal": "small_button_normal",
            "small_button_pressed": "small_button_pressed",
        }

        for theme_key, local_key in key_map.items():
            rel_path = theme_manager.get_image_path(theme_key)
            if rel_path:
                full_path = assets_path / rel_path
                if full_path.exists():
                    img = pygame.image.load(str(full_path))
                    if pygame.display.get_surface():
                        if "button" in local_key:
                            img = img.convert_alpha()
                        else:
                            img = img.convert()
                    assets[local_key] = img
                else:
                    print(f"⚠️ Asset não encontrado: {full_path}")

    except Exception as e:
        print(f"Erro ao carregar assets do menu: {e}")

    return assets


def render_menu_background(surface, background_image, theme, darkness=0.5):
    """
    Renderiza background do menu com camada de escurecimento

    Args:
        surface: Superfície pygame onde renderizar
        background_image: Imagem de fundo (ou None para cor sólida)
        theme: Tema atual do jogo
        darkness: Intensidade do escurecimento (0.0 a 1.0, padrão 0.5)
    """
    sw, sh = surface.get_width(), surface.get_height()

    # Renderiza background
    if background_image:
        surface.blit(pygame.transform.scale(background_image, (sw, sh)), (0, 0))
    else:
        surface.fill(theme.COLOR_BACKGROUND)

    # Camada de escurecimento para dar foco no menu
    if darkness > 0:
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(255 * darkness)))
        surface.blit(overlay, (0, 0))
