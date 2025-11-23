from typing import Optional, List


class ThemeManager:
    """
    Gerencia caminhos de recursos baseados no tema atual.
    Atua como uma ponte entre chaves de recursos e caminhos de arquivo.
    """

    def __init__(self):
        # Tema atual (Padrão = visual atual com botões de madeira)
        self.current_theme = "Padrão"

        # Temas disponíveis
        # Padrão: Visual atual implementado (menu inicial, configurações)
        # Outros: Placeholders para futuras implementações
        self._available_themes = ["Padrão", "Dark", "Light", "Blue", "Green"]

        # ==================== MAPEAMENTOS DE ASSETS ====================
        # TEMA PADRÃO - Assets Implementados:
        # ✅ Tela Inicial (Menu Principal)
        # ✅ Configurações (Settings, Video, Audio, Theme, Slots)
        # ⏳ Outras telas serão adicionadas conforme implementação

        self.image_paths = {
            # Assets legados (manter para compatibilidade)
            "logo": "images/ui/logo.png",
            "menu_bg": "images/ui/menu_bg.png",
            "button_default": "images/ui/button_default.png",
            "button_hover": "images/ui/button_hover.png",
            "panel_bg": "images/ui/panel_bg.png",
            # ========== TEMA PADRÃO - ASSETS PRINCIPAIS ==========
            # Background da tela inicial/menus
            "menu_background": "images/titles/title_background.jpg",
            # Botões principais (madeira - 400px largura)
            "button_normal": "images/button/button_main_menu_ON.png",
            "button_pressed": "images/button/button_main_menu_OFF.png",
            # Botões pequenos (controles +/-, ~40px)
            "small_button_normal": "images/button/small_button_padrao_ON.png",
            "small_button_pressed": "images/button/small_button_padrao_OFF.png",
            # Título do jogo (usado em menu.py)
            "title_image": "images/titles/title_FoxWorldRPG.png",
        }

        self.font_paths = {
            "title": "fonts/title_font.ttf",
            "menu": "fonts/menu_font.ttf",
            "text": "fonts/text_font.ttf",
            "hud": "fonts/hud_font.ttf",
        }

        self.sound_paths = {
            "click": "sounds/ui/click.wav",
            "hover": "sounds/ui/hover.wav",
            "bgm_menu": "sounds/music/menu_theme.ogg",
        }

    def get_available_themes(self) -> List[str]:
        """Retorna lista de temas disponíveis"""
        return self._available_themes.copy()

    def set_theme(self, theme_name: str) -> bool:
        """Define o tema atual"""
        if theme_name in self._available_themes:
            self.current_theme = theme_name

            # Atualiza o UITheme global
            from src.ui.ui_theme import get_theme

            get_theme().load_theme(theme_name)

            print(f"🎨 Tema alterado para: {theme_name}")
            return True
        else:
            print(f"⚠️ Tema '{theme_name}' não encontrado")
            return False

    def get_image_path(self, image_key: str) -> Optional[str]:
        """Retorna o caminho relativo para uma imagem"""
        return self.image_paths.get(image_key)

    def get_font_path(self, font_type: str) -> Optional[str]:
        """Retorna o caminho relativo para uma fonte"""
        return self.font_paths.get(font_type)

    def get_sound_path(self, sound_key: str) -> Optional[str]:
        """Retorna o caminho relativo para um som"""
        return self.sound_paths.get(sound_key)
