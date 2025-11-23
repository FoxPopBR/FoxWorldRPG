import pygame
from pathlib import Path
from config.display_config import DisplayConfig
from config.settings_manager import SettingsManager
from src.core.resource_manager import ResourceManager
from src.ui.ui_theme import UITheme, get_theme
from src.ui.theme_manager import ThemeManager


class GameConfig:
    """
    Centraliza as configurações e gerenciadores do jogo.
    """

    GAME_VERSION = "0.0.01"

    def __init__(self):
        # 1. Inicializa DatabaseManager (Base de tudo)
        from src.database.database_manager import DatabaseManager

        self.database = DatabaseManager()

        # 1.5. Inicializa as tabelas do jogo
        self.database.initialize_game_tables()

        # 2. Inicializa SettingsManager (Precisa do Database)
        self.settings_manager = SettingsManager(self.database)

        # 3. Inicializa DisplayConfig (Precisa do SettingsManager)
        self.display_config = DisplayConfig(self.settings_manager)

        # 4. Inicializa ThemeManager
        self.theme_manager = ThemeManager()

        # 5. Inicializa ResourceManager
        # Define o caminho base dos assets (assumindo que main.py está na raiz)
        assets_path = Path("assets")
        self.resource_manager = ResourceManager(assets_path, self.theme_manager)

        # 6. Inicializa HeroManager (Precisa do Database e ResourceManager)
        from src.entities.hero_manager import HeroManager

        self.hero_manager = HeroManager(self.database, self.resource_manager)

        # Tema de UI
        self.theme = get_theme()

    def clear_cache(self):
        """Limpa o cache de recursos"""
        if self.resource_manager:
            self.resource_manager.clear_cache()

    def get_color(self, color_name):
        """Retorna uma cor do tema ou uma cor padrão"""
        # Mapeamento de compatibilidade para o novo UITheme
        color_map = {
            "background": self.theme.COLOR_BACKGROUND,
            "text": self.theme.COLOR_TEXT_PRIMARY,
            "text_secondary": self.theme.COLOR_TEXT_SECONDARY,
            "primary": self.theme.COLOR_PRIMARY,
            "secondary": self.theme.COLOR_SECONDARY,
            "accent": self.theme.COLOR_ACCENT,
            "success": self.theme.COLOR_SUCCESS,
            "warning": self.theme.COLOR_WARNING,
            "error": self.theme.COLOR_ERROR,
            "white": (255, 255, 255),
            "black": (0, 0, 0),
        }
        return color_map.get(color_name, (255, 255, 255))

    def get_font(self, font_type, size):
        """
        Retorna uma fonte carregada.

        Args:
            font_type: 'title', 'menu', 'text'
            size: Tamanho da fonte
        """
        # Por enquanto usa a fonte padrão do Pygame ou uma fonte do sistema
        # Idealmente deveria usar o ResourceManager para carregar fontes customizadas
        return pygame.font.Font(None, int(size))
