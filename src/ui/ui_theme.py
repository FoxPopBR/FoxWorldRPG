"""
src/ui/ui_theme.py

ARQUIVO CENTRAL DE TEMA E CONSTANTES DE UI
==========================================

Este arquivo concentra TODAS as definições de:
- Tamanhos de fonte
- Dimensões de elementos
- Espaçamentos
- Cores
- Posições relativas

IMPORTANTE: Nenhum outro arquivo deve ter valores hardcoded de UI!
Todos devem usar este arquivo como fonte única de verdade.
"""

from typing import Tuple
from dataclasses import dataclass


@dataclass
class UITheme:
    """Tema centralizado da UI - fonte única de verdade para toda a interface"""

    # ==================== RESOLUÇÃO BASE ====================
    # Toda a UI é projetada para esta resolução virtual
    BASE_WIDTH: int = 1920
    BASE_HEIGHT: int = 1080

    # ==================== TAMANHOS DE FONTE ====================
    # Títulos principais
    FONT_TITLE_LARGE: int = 72  # Título do jogo (menu principal)
    FONT_TITLE_MEDIUM: int = 60  # Títulos de tela
    FONT_TITLE_SMALL: int = 48  # Subtítulos

    # Texto de menu e botões
    FONT_MENU_LARGE: int = 32  # Botões grandes
    FONT_MENU_MEDIUM: int = 24  # Texto de menu normal
    FONT_MENU_SMALL: int = 20  # Texto secundário
    FONT_MENU_TINY: int = 18  # Hints e informações

    # HUD e gameplay
    FONT_HUD_LARGE: int = 28  # Informações principais do HUD
    FONT_HUD_MEDIUM: int = 22  # Informações secundárias
    FONT_HUD_SMALL: int = 18  # Detalhes e hints

    # Diálogos e notificações
    FONT_DIALOG: int = 24
    FONT_NOTIFICATION: int = 20

    # ==================== DIMENSÕES DE BOTÕES ====================
    # Botões principais (menu)
    BUTTON_MAIN_WIDTH: int = 300
    BUTTON_MAIN_HEIGHT: int = 70
    BUTTON_MAIN_FONT: int = 28

    # Botões secundários
    BUTTON_SECONDARY_WIDTH: int = 200
    BUTTON_SECONDARY_HEIGHT: int = 50
    BUTTON_SECONDARY_FONT: int = 22

    # Botões pequenos (ações)
    BUTTON_SMALL_WIDTH: int = 150
    BUTTON_SMALL_HEIGHT: int = 40
    BUTTON_SMALL_FONT: int = 18

    # ==================== ESPAÇAMENTOS ====================
    SPACING_TINY: int = 10
    SPACING_SMALL: int = 20
    SPACING_MEDIUM: int = 40
    SPACING_LARGE: int = 60
    SPACING_HUGE: int = 100

    # ==================== MARGENS ====================
    MARGIN_SCREEN: int = 50  # Margem das bordas da tela
    MARGIN_SECTION: int = 30  # Margem entre seções
    MARGIN_ELEMENT: int = 15  # Margem interna de elementos

    # ==================== CARDS E PAINÉIS ====================
    # Slots de jogo
    SLOT_CARD_WIDTH: int = 550
    SLOT_CARD_HEIGHT: int = 260
    SLOT_CARD_SPACING_X: int = 60
    SLOT_CARD_SPACING_Y: int = 60
    SLOT_CARD_BORDER_RADIUS: int = 15

    # Save slots
    SAVE_CARD_WIDTH: int = 450
    SAVE_CARD_HEIGHT: int = 280
    SAVE_CARD_SPACING: int = 40

    # Modal/Dialog
    MODAL_WIDTH: int = 600
    MODAL_HEIGHT: int = 200
    MODAL_BORDER_RADIUS: int = 20

    # ==================== CORES DO TEMA ====================
    # Cores de fundo
    COLOR_BG_DARK: Tuple[int, int, int] = (15, 15, 25)
    COLOR_BG_CARD: Tuple[int, int, int] = (30, 30, 40)
    COLOR_BG_MODAL: Tuple[int, int, int] = (40, 40, 50)

    # Cores de borda
    COLOR_BORDER_EMPTY: Tuple[int, int, int] = (100, 255, 100)  # Verde (slot vazio)
    COLOR_BORDER_ACTIVE: Tuple[int, int, int] = (100, 150, 255)  # Azul (slot ocupado)
    COLOR_BORDER_SELECTED: Tuple[int, int, int] = (255, 200, 0)  # Dourado (selecionado)
    COLOR_BORDER_WARNING: Tuple[int, int, int] = (255, 100, 100)  # Vermelho (aviso)

    # Cores de texto
    COLOR_TEXT_PRIMARY: Tuple[int, int, int] = (255, 255, 255)
    COLOR_TEXT_SECONDARY: Tuple[int, int, int] = (200, 200, 200)
    COLOR_TEXT_HINT: Tuple[int, int, int] = (150, 150, 150)
    COLOR_TEXT_SUCCESS: Tuple[int, int, int] = (100, 255, 100)
    COLOR_TEXT_WARNING: Tuple[int, int, int] = (255, 200, 100)
    COLOR_TEXT_ERROR: Tuple[int, int, int] = (255, 100, 100)

    # Cores de botão
    COLOR_BUTTON_DEFAULT: Tuple[int, int, int] = (60, 60, 80)
    COLOR_BUTTON_HOVER: Tuple[int, int, int] = (80, 80, 100)
    COLOR_BUTTON_ACTIVE: Tuple[int, int, int] = (100, 100, 120)
    COLOR_BUTTON_DANGER: Tuple[int, int, int] = (200, 50, 50)
    COLOR_BUTTON_DANGER_HOVER: Tuple[int, int, int] = (255, 80, 80)

    # ==================== POSIÇÕES RELATIVAS ====================
    # Títulos
    TITLE_Y_POS: int = 100
    SUBTITLE_Y_POS: int = 170

    # Menu principal - botões verticais centralizados
    MENU_START_Y_OFFSET: int = 0  # Calculado dinamicamente para centralizar

    # ==================== HUD (GameState) ====================
    HUD_SIDEBAR_WIDTH: int = 250
    HUD_SIDEBAR_SPACING: int = 15
    HUD_PORTRAIT_SIZE: int = 120
    HUD_BAR_HEIGHT: int = 20
    HUD_INFO_SPACING: int = 10


# Instância global do tema (singleton)
UI_THEME = UITheme()


def get_theme() -> UITheme:
    """Retorna a instância do tema UI"""
    return UI_THEME
