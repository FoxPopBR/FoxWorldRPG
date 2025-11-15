from typing import Dict, Any
from src.database.database_manager import DatabaseManager

class SettingsManager:
    """Gerenciador de configurações usando banco de dados"""
    
    def __init__(self, database_manager: DatabaseManager):
        self.db = database_manager
        self._load_default_settings()
    
    def _load_default_settings(self):
        """Carrega configurações padrão se não existirem"""
        # Primeiro verifica se há configurações corrompidas
        video_settings = self.get_video_settings()
        
        # Se houver valores problemáticos, reseta as configurações de vídeo
        needs_reset = False
        for key, value in video_settings.items():
            if isinstance(value, str) and value in ('True', 'False', 'true', 'false'):
                needs_reset = True
                break
        
        if needs_reset or not video_settings:
            print("Configurações de vídeo corrompidas ou ausentes. Recarregando padrões...")
            self.db.delete_all_settings('video')
            self._set_default_video_settings()
        
        # Configurações de áudio padrão
        if self.db.get_setting('audio', 'master_volume') is None:
            self._set_default_audio_settings()
        
        # Configurações de controle padrão
        if self.db.get_setting('controls', 'key_up') is None:
            self._set_default_control_settings()
        
        # Configurações de jogo padrão
        if self.db.get_setting('game', 'current_theme') is None:
            self._set_default_game_settings()
    
    def _set_default_video_settings(self):
        """Define configurações padrão de vídeo"""
        self.set_video_setting('resolution', (1920, 1080))
        self.set_video_setting('fullscreen', False)
        self.set_video_setting('vsync', True)
        self.set_video_setting('fps', 60)
    
    def _set_default_audio_settings(self):
        """Define configurações padrão de áudio"""
        self.set_audio_setting('master_volume', 1.0)
        self.set_audio_setting('music_volume', 0.8)
        self.set_audio_setting('sfx_volume', 0.9)
        self.set_audio_setting('voice_volume', 1.0)
    
    def _set_default_control_settings(self):
        """Define configurações padrão de controle"""
        self.set_control_setting('key_up', 'w')
        self.set_control_setting('key_down', 's')
        self.set_control_setting('key_left', 'a')
        self.set_control_setting('key_right', 'd')
        self.set_control_setting('key_action', 'e')
        self.set_control_setting('key_inventory', 'i')
        self.set_control_setting('key_journal', 'j')
        self.set_control_setting('key_map', 'm')
    
    def _set_default_game_settings(self):
        """Define configurações padrão de jogo"""
        self.set_game_setting('current_theme', 'default')
        self.set_game_setting('language', 'pt_BR')
        self.set_game_setting('difficulty', 'normal')
        self.set_game_setting('autosave', True)
        self.set_game_setting('autosave_interval', 15)
    
    # Métodos para configurações de vídeo
    def get_video_settings(self) -> Dict[str, Any]:
        return self.db.get_all_settings('video')
    
    def set_video_setting(self, key: str, value: Any):
        self.db.set_setting('video', key, value)
    
    def get_video_setting(self, key: str, default: Any = None) -> Any:
        return self.db.get_setting('video', key, default)
    
    # Métodos para configurações de áudio
    def get_audio_settings(self) -> Dict[str, Any]:
        return self.db.get_all_settings('audio')
    
    def set_audio_setting(self, key: str, value: Any):
        self.db.set_setting('audio', key, value)
    
    def get_audio_setting(self, key: str, default: Any = None) -> Any:
        return self.db.get_setting('audio', key, default)
    
    # Métodos para configurações de controle
    def get_control_settings(self) -> Dict[str, Any]:
        return self.db.get_all_settings('controls')
    
    def set_control_setting(self, key: str, value: Any):
        self.db.set_setting('controls', key, value)
    
    def get_control_setting(self, key: str, default: Any = None) -> Any:
        return self.db.get_setting('controls', key, default)
    
    # Métodos para configurações de jogo
    def get_game_settings(self) -> Dict[str, Any]:
        return self.db.get_all_settings('game')
    
    def set_game_setting(self, key: str, value: Any):
        self.db.set_setting('game', key, value)
    
    def get_game_setting(self, key: str, default: Any = None) -> Any:
        return self.db.get_setting('game', key, default)
    
    # Métodos para temas
    def get_current_theme(self) -> str:
        return self.get_game_setting('current_theme', 'default')
    
    def set_current_theme(self, theme_name: str):
        self.set_game_setting('current_theme', theme_name)
    
    def reset_all_settings(self):
        """Reseta todas as configurações para os padrões"""
        self.db.delete_all_settings()
        self._load_default_settings()
        print("Todas as configurações foram resetadas para os valores padrão")
    
    def export_settings(self) -> Dict[str, Dict[str, Any]]:
        """Exporta todas as configurações para dicionário"""
        return {
            'video': self.get_video_settings(),
            'audio': self.get_audio_settings(),
            'controls': self.get_control_settings(),
            'game': self.get_game_settings()
        }
    
    def import_settings(self, settings: Dict[str, Dict[str, Any]]):
        """Importa configurações de um dicionário"""
        for category, category_settings in settings.items():
            for key, value in category_settings.items():
                self.db.set_setting(category, key, value)