# config/game_config.py - VERSÃO CORRIGIDA
import pygame
import os
from pathlib import Path
from typing import Optional, Dict, Any


class GameConfig:
    """Configurações gerais do jogo SEM importação circular"""

    def __init__(self, game=None):
        # Paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.ASSETS_PATH = self.BASE_DIR / "assets"
        self.SAVE_PATH = self.BASE_DIR / "saves"

        # Referência ao jogo
        self.game = game

        # ✅ CORREÇÃO: Inicialização adiada para evitar circularidade
        self.database = None
        self.settings_manager = None
        self.hero_manager = None
        self.enemy_manager = None
        self.theme_manager = None
        self.resource_manager = None  # Novo ResourceManager

    def initialize_managers(self, database_manager):
        """✅ CORREÇÃO: Inicializa managers DEPOIS para evitar importação circular"""
        from config.settings_manager import SettingsManager
        from config.theme_manager import ThemeManager
        from src.entities.hero_manager import HeroManager
        from src.entities.enemy_manager import EnemyManager
        from src.core.resource_manager import ResourceManager

        self.database = database_manager
        self.settings_manager = SettingsManager(self.database)
        self.theme_manager = ThemeManager()

        # Inicializa ResourceManager
        self.resource_manager = ResourceManager(self.ASSETS_PATH, self.theme_manager)

        # Inicializa Managers de Entidades
        self.hero_manager = HeroManager(self.database, self.resource_manager)
        self.enemy_manager = EnemyManager(self.database, self.resource_manager)

        # Aplica o tema atual do banco de dados
        current_theme = self.settings_manager.get_current_theme()
        self.theme_manager.set_theme(current_theme)

    def get_color(self, color_key: str) -> tuple:
        """Obtém uma cor do tema atual"""
        return self.theme_manager.get_color(color_key)

    def get_font(self, font_type: str, size: int) -> pygame.font.Font:
        """Obtém uma fonte via ResourceManager"""
        if self.resource_manager:
            return self.resource_manager.get_font(font_type, size)
        return pygame.font.Font(None, size)

    def get_image(self, image_key: str) -> Optional[pygame.Surface]:
        """Obtém uma imagem via ResourceManager"""
        if self.resource_manager:
            return self.resource_manager.get_image(image_key)
        return None

    def get_sound(self, sound_key: str) -> Optional[pygame.mixer.Sound]:
        """Obtém um som via ResourceManager"""
        if self.resource_manager:
            return self.resource_manager.get_sound(sound_key)
        return None

    def get_ui_setting(self, setting_key: str, default=None):
        """Obtém uma configuração de UI do tema"""
        return self.theme_manager.get_ui_setting(setting_key, default)

    def get_animation_setting(self, setting_key: str, default=None):
        """Obtém uma configuração de animação do tema"""
        return self.theme_manager.get_animation_setting(setting_key, default)

    def clear_cache(self):
        """Limpa o cache de recursos"""
        if self.resource_manager:
            self.resource_manager.clear_cache()

    def cleanup(self):
        """Limpeza final"""
        if self.database:
            self.database.close()

    def get_class_image(self, class_key):
        """Obtém imagem da classe (ícone) via ResourceManager"""
        if self.resource_manager:
            # Usa a imagem 'class' como ícone principal da classe
            return self.resource_manager.get_hero_image(class_key, "class")
        return None

    @property
    def current_resolution(self):
        """Retorna a resolução atual do jogo para escalonamento de UI"""
        if self.game and hasattr(self.game, "display_config"):
            return self.game.display_config.current_resolution
        return (1920, 1080)  # Fallback padrão
