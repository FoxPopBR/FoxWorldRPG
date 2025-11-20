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
        self.theme_manager = None
        
        # Cache de recursos carregados
        self._image_cache: Dict[str, pygame.Surface] = {}
        self._font_cache: Dict[str, pygame.font.Font] = {}
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}
    
    def initialize_managers(self, database_manager):
        """✅ CORREÇÃO: Inicializa managers DEPOIS para evitar importação circular"""
        from config.settings_manager import SettingsManager
        from config.theme_manager import ThemeManager
        
        self.database = database_manager
        self.settings_manager = SettingsManager(self.database)
        self.theme_manager = ThemeManager()
        
        # Aplica o tema atual do banco de dados
        current_theme = self.settings_manager.get_current_theme()
        self.theme_manager.set_theme(current_theme)
        
        self.initialize_resources()
    
    def initialize_resources(self):
        """Inicializa recursos do tema atual"""
        pass
    
    def get_color(self, color_key: str) -> tuple:
        """Obtém uma cor do tema atual"""
        return self.theme_manager.get_color(color_key)
    
    def get_font(self, font_type: str, size: int) -> pygame.font.Font:
        """Obtém uma fonte do tema atual"""
        cache_key = f"{font_type}_{size}"
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        font_path = self.theme_manager.get_font_path(font_type)
        try:
            if font_path and os.path.exists(self.ASSETS_PATH / font_path):
                full_path = self.ASSETS_PATH / font_path
                font = pygame.font.Font(str(full_path), size)
            else:
                font = pygame.font.Font(None, size)
                
            self._font_cache[cache_key] = font
            return font
            
        except Exception as e:
            print(f"AVISO: Erro ao carregar fonte {font_type}: {e}")
            return pygame.font.Font(None, size)
    
    def get_image(self, image_key: str) -> Optional[pygame.Surface]:
        """Obtém uma imagem do tema atual"""
        if image_key in self._image_cache:
            return self._image_cache[image_key]
        
        image_path = self.theme_manager.get_image_path(image_key)
        if image_path and os.path.exists(self.ASSETS_PATH / image_path):
            try:
                full_path = self.ASSETS_PATH / image_path
                image = pygame.image.load(str(full_path)).convert_alpha()
                self._image_cache[image_key] = image
                return image
            except Exception as e:
                print(f"Erro ao carregar imagem {image_key}: {e}")
        
        return None
    
    def get_sound(self, sound_key: str) -> Optional[pygame.mixer.Sound]:
        """Obtém um som do tema atual"""
        if sound_key in self._sound_cache:
            return self._sound_cache[sound_key]
        
        sound_path = self.theme_manager.get_sound_path(sound_key)
        if sound_path and os.path.exists(self.ASSETS_PATH / sound_path):
            try:
                full_path = self.ASSETS_PATH / sound_path
                sound = pygame.mixer.Sound(str(full_path))
                self._sound_cache[sound_key] = sound
                return sound
            except Exception as e:
                print(f"Erro ao carregar som {sound_key}: {e}")
        
        return None
    
    def get_ui_setting(self, setting_key: str, default=None):
        """Obtém uma configuração de UI do tema"""
        return self.theme_manager.get_ui_setting(setting_key, default)
    
    def get_animation_setting(self, setting_key: str, default=None):
        """Obtém uma configuração de animação do tema"""
        return self.theme_manager.get_animation_setting(setting_key, default)
    
    def clear_cache(self):
        """Limpa o cache de recursos (útil ao trocar de tema)"""
        self._image_cache.clear()
        self._font_cache.clear()
        self._sound_cache.clear()
    
    def cleanup(self):
        """Limpeza final"""
        if self.database:
            self.database.close()

    def get_class_image(self, class_key):
        """✅ CORREÇÃO: Carrega imagem da classe SEM método inexistente"""
        image_key = f"class_{class_key}"
        
        if image_key in self._image_cache:
            return self._image_cache[image_key]
        
        # ✅ CORREÇÃO: Define cores padrão para cada classe
        class_colors = {
            'barbaro': (178, 34, 34),      # Vermelho
            'paladino': (255, 215, 0),     # Dourado  
            'druida': (34, 139, 34),       # Verde
            'feiticeiro': (65, 105, 225),  # Azul
            'necromante': (75, 0, 130)     # Roxo
        }
        
        try:
            # Tenta carregar do diretório de assets
            image_path = self.ASSETS_PATH / "images" / "classes" / f"{class_key}_icon.png"
            if image_path.exists():
                image = pygame.image.load(str(image_path)).convert_alpha()
                self._image_cache[image_key] = image
                return image
        except Exception as e:
            print(f"AVISO: Não foi possível carregar imagem da classe {class_key}: {e}")
        
        # Fallback: cria imagem placeholder
        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        color = class_colors.get(class_key, (128, 128, 128))
        
        # Desenha um círculo colorido como placeholder
        pygame.draw.circle(surface, color, (50, 50), 45)
        pygame.draw.circle(surface, (255, 255, 255), (50, 50), 40, 3)
        
        # Adiciona texto da classe
        font = self.get_font('menu', 14)
        text = font.render(class_key[:3].upper(), True, (255, 255, 255))
        text_rect = text.get_rect(center=(50, 50))
        surface.blit(text, text_rect)
        
        self._image_cache[image_key] = surface
        return surface