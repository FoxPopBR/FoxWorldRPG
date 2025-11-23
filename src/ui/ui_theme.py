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
    # Paletas de cores por tema
    THEMES = {
        "Dark": {
            "bg_primary": (15, 15, 25),
            "bg_secondary": (25, 25, 35),
            "bg_card": (30, 30, 40),
            "bg_modal": (40, 40, 50),
            "primary": (60, 60, 80),
            "secondary": (80, 80, 100),
            "accent": (255, 200, 0),
            "text_primary": (255, 255, 255),
            "text_secondary": (200, 200, 200),
            "border_default": (60, 60, 80),
            "border_active": (100, 150, 255),
        },
        "Light": {
            "bg_primary": (240, 240, 245),
            "bg_secondary": (255, 255, 255),
            "bg_card": (255, 255, 255),
            "bg_modal": (230, 230, 240),
            "primary": (200, 200, 220),
            "secondary": (180, 180, 200),
            "accent": (255, 140, 0),
            "text_primary": (20, 20, 30),
            "text_secondary": (60, 60, 80),
            "border_default": (200, 200, 220),
            "border_active": (100, 150, 255),
        },
        "Blue": {
            "bg_primary": (10, 20, 40),
            "bg_secondary": (20, 30, 60),
            "bg_card": (25, 40, 80),
            "bg_modal": (30, 50, 90),
            "primary": (40, 80, 160),
            "secondary": (60, 100, 200),
            "accent": (0, 200, 255),
            "text_primary": (240, 250, 255),
            "text_secondary": (180, 200, 220),
            "border_default": (40, 80, 160),
            "border_active": (0, 200, 255),
        },
        "Green": {
            "bg_primary": (10, 30, 15),
            "bg_secondary": (20, 45, 25),
            "bg_card": (25, 55, 30),
            "bg_modal": (30, 65, 40),
            "primary": (40, 100, 50),
            "secondary": (60, 140, 70),
            "accent": (100, 255, 100),
            "text_primary": (240, 255, 240),
            "text_secondary": (180, 220, 180),
            "border_default": (40, 100, 50),
            "border_active": (100, 255, 100),
        },
    }

    # Cores de fundo (Inicializadas com Dark)
    COLOR_BG_PRIMARY: Tuple[int, int, int] = THEMES["Dark"]["bg_primary"]
    COLOR_BG_SECONDARY: Tuple[int, int, int] = THEMES["Dark"]["bg_secondary"]
    COLOR_BG_DARK: Tuple[int, int, int] = THEMES["Dark"]["bg_primary"]
    COLOR_BG_CARD: Tuple[int, int, int] = THEMES["Dark"]["bg_card"]
    COLOR_BG_MODAL: Tuple[int, int, int] = THEMES["Dark"]["bg_modal"]
    COLOR_BACKGROUND: Tuple[int, int, int] = THEMES["Dark"]["bg_primary"]

    # Cores gerais
    COLOR_PRIMARY: Tuple[int, int, int] = THEMES["Dark"]["primary"]
    COLOR_SECONDARY: Tuple[int, int, int] = THEMES["Dark"]["secondary"]
    COLOR_ACCENT: Tuple[int, int, int] = THEMES["Dark"]["accent"]
    COLOR_SUCCESS: Tuple[int, int, int] = (100, 255, 100)
    COLOR_WARNING: Tuple[int, int, int] = (255, 200, 100)
    COLOR_ERROR: Tuple[int, int, int] = (255, 100, 100)

    # Cores de borda
    COLOR_BORDER_DEFAULT: Tuple[int, int, int] = THEMES["Dark"]["border_default"]
    COLOR_BORDER_HOVER: Tuple[int, int, int] = (100, 100, 150)
    COLOR_BORDER_EMPTY: Tuple[int, int, int] = (100, 100, 120)
    COLOR_BORDER_ACTIVE: Tuple[int, int, int] = THEMES["Dark"]["border_active"]
    COLOR_BORDER_SELECTED: Tuple[int, int, int] = (255, 200, 0)
    COLOR_BORDER_WARNING: Tuple[int, int, int] = (255, 100, 100)

    # Cores de acento (extras)
    COLOR_ACCENT_BLUE: Tuple[int, int, int] = (100, 150, 255)
    COLOR_ACCENT_GREEN: Tuple[int, int, int] = (100, 255, 100)
    COLOR_ACCENT_RED: Tuple[int, int, int] = (255, 100, 100)
    COLOR_ACCENT_GOLD: Tuple[int, int, int] = (255, 215, 0)

    # Cores de texto
    COLOR_TEXT_PRIMARY: Tuple[int, int, int] = THEMES["Dark"]["text_primary"]
    COLOR_TEXT_SECONDARY: Tuple[int, int, int] = THEMES["Dark"]["text_secondary"]
    COLOR_TEXT_HINT: Tuple[int, int, int] = (150, 150, 150)
    COLOR_TEXT_SUCCESS: Tuple[int, int, int] = (100, 255, 100)
    COLOR_TEXT_WARNING: Tuple[int, int, int] = (255, 200, 100)
    COLOR_TEXT_ERROR: Tuple[int, int, int] = (255, 100, 100)

    # Cores de botão
    COLOR_BUTTON_DEFAULT: Tuple[int, int, int] = THEMES["Dark"]["primary"]
    COLOR_BUTTON_HOVER: Tuple[int, int, int] = THEMES["Dark"]["secondary"]
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

    def load_theme(self, theme_name: str):
        """Carrega as cores de um tema específico"""
        if theme_name not in self.THEMES:
            print(f"⚠️ Tema '{theme_name}' não encontrado, usando Dark")
            theme_name = "Dark"

        theme = self.THEMES[theme_name]

        # Atualiza cores
        self.COLOR_BG_PRIMARY = theme["bg_primary"]
        self.COLOR_BG_SECONDARY = theme["bg_secondary"]
        self.COLOR_BG_DARK = theme["bg_primary"]
        self.COLOR_BG_CARD = theme["bg_card"]
        self.COLOR_BG_MODAL = theme["bg_modal"]
        self.COLOR_BACKGROUND = theme["bg_primary"]

        self.COLOR_PRIMARY = theme["primary"]
        self.COLOR_SECONDARY = theme["secondary"]
        self.COLOR_ACCENT = theme["accent"]

        self.COLOR_BORDER_DEFAULT = theme["border_default"]
        self.COLOR_BORDER_ACTIVE = theme["border_active"]

        self.COLOR_TEXT_PRIMARY = theme["text_primary"]
        self.COLOR_TEXT_SECONDARY = theme["text_secondary"]

        self.COLOR_BUTTON_DEFAULT = theme["primary"]
        self.COLOR_BUTTON_HOVER = theme["secondary"]

        print(f"🎨 UITheme atualizado para: {theme_name}")


# Instância global do tema (singleton)
UI_THEME = UITheme()


def get_theme() -> UITheme:
    """Retorna a instância do tema UI"""
    return UI_THEME
