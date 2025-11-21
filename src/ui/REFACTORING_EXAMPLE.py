"""
AGORA, com UITheme + UIScaler integrados, refatorar states é SIMPLES!
=======================================================================

# ANTES (ruim - valores hardcoded em cada arquivo):
title_font = game.game_config.get_font("title", 60)  # 60 hardcoded!
button = Button(100, 200, 300, 70, "TEXTO", ...)     # todos hardcoded!

# DEPOIS (bom - usa tema central):
scaler = game.ui_scaler
title_font = scaler.get_themed_font('title')         # Pega do tema!
button_rect = scaler.get_button_rect(100, 200, 'main')  # Dimensões do tema!

# Com isso, mudar o tamanho de TODOS os títulos do jogo é...
# ...alterar UMA LINHA no ui_theme.py!

EXEMPLO PRÁTICO - Menu Refatorado:
===================================
"""

import pygame
from src.ui.ui_theme import get_theme


class MainMenuREFACTORED:
    def render(self, surface):
        scaler = self.game.ui_scaler
        theme = get_theme()

        # Fundo
        surface.fill(theme.COLOR_BG_DARK)

        # Título - ZERO valores hardcoded!
        title_font = scaler.get_themed_font("title_large")
        title_text = title_font.render("FOXWORLD RPG", True, theme.COLOR_TEXT_PRIMARY)
        title_x = scaler.center_x(title_text.get_width())
        title_y = scaler.scale(theme.TITLE_Y_POS, "y")
        surface.blit(title_text, (title_x, title_y))

        # Subtítulo
        subtitle_font = scaler.get_themed_font("menu")
        subtitle = subtitle_font.render(
            "Uma Aventura Épica", True, theme.COLOR_TEXT_SECONDARY
        )
        subtitle_x = scaler.center_x(subtitle.get_width())
        subtitle_y = scaler.scale(theme.SUBTITLE_Y_POS, "y")
        surface.blit(subtitle, (subtitle_x, subtitle_y))

        # Botões - dimensões do tema!
        for i, button in enumerate(self.buttons):
            button.render(surface, self.game.game_config)


"""
ESTRATÉGIA DE REFATORAÇÃO
==========================

Para cada state, seguir este padrão:

1. Import no topo:
   from src.ui.ui_theme import get_theme

2. No __init__ ou _create_ui:
   scaler = self.game.ui_scaler
   theme = get_theme()

3. Substituir valores hardcoded:
   - Tamanhos de fonte: scaler.get_themed_font('tipo')
   - Dimensões de botão: Button com valores de theme.BUTTON_*
   - Cores: theme.COLOR_*
   - Espaçamentos: theme.SPACING_*
   - Posições: theme.TITLE_Y_POS, etc.

4. Para renderização:
   - Usar scaler.rect(), scaler.center_x(), scaler.scale()
   
Isso torna cada arquivo MUITO mais limpo e fácil de manter!
"""
