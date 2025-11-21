# config/theme_manager.py - VERSÃO MELHORADA
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


class ThemeManager:
    """Gerenciador de temas do jogo com validação robusta"""

    def __init__(self):
        self.themes: Dict[str, Dict[str, Any]] = {}
        self.current_theme: str = "default"
        self.themes_path = Path("assets/themes")
        self._load_all_themes()

    def _load_all_themes(self):
        """Carrega todos os temas disponíveis com validação robusta"""
        try:
            self.themes_path.mkdir(parents=True, exist_ok=True)

            # Verifica se o tema padrão existe e é válido
            default_theme_path = self.themes_path / "default.json"
            if not default_theme_path.exists() or self._is_theme_corrupted(
                default_theme_path
            ):
                print("🔄 Recriando tema padrão...")
                self._create_default_theme()

            # Carrega todos os temas
            loaded_themes = 0
            for theme_file in self.themes_path.glob("*.json"):
                theme_name = theme_file.stem
                try:
                    with open(theme_file, "r", encoding="utf-8") as f:
                        theme_data = json.load(f)

                    # ✅ CORREÇÃO: Valida estrutura básica do tema
                    if self._validate_theme_structure(theme_data):
                        self.themes[theme_name] = theme_data
                        loaded_themes += 1
                        # print(f"✅ Tema carregado: {theme_name}")
                    else:
                        print(f"❌ Tema inválido ignorado: {theme_name}")

                except Exception as e:
                    print(f"❌ Erro ao carregar tema {theme_name}: {e}")

            # print(f"🎨 Total de temas carregados: {loaded_themes}")

            if not self.themes:
                print("⚠️  Nenhum tema carregado, criando tema padrão de emergência")
                self._create_default_theme()

        except Exception as e:
            print(f"💥 Erro crítico ao carregar temas: {e}")
            self._create_default_theme()

    def _is_theme_corrupted(self, theme_path: Path) -> bool:
        """Verifica se um arquivo de tema está corrompido"""
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                json.load(f)
            return False
        except:
            return True

    def _validate_theme_structure(self, theme_data: Dict[str, Any]) -> bool:
        """Valida a estrutura básica de um tema"""
        required_sections = ["name", "colors", "fonts", "images"]
        required_colors = ["background", "text", "button_normal", "button_hover"]

        # Verifica se todas as seções necessárias existem
        if not all(section in theme_data for section in required_sections):
            return False

        # Verifica se as cores essenciais existem
        colors = theme_data.get("colors", {})
        if not all(color in colors for color in required_colors):
            return False

        return True

    def _create_default_theme(self):
        """Cria o tema padrão"""
        default_theme = {
            "name": "Tema Padrão",
            "version": "1.0",
            "author": "Sistema",
            "colors": {
                "background": [30, 30, 45],
                "ui_background": [45, 45, 60],
                "ui_border": [70, 130, 180],
                "text": [255, 255, 255],
                "text_secondary": [200, 200, 200],
                "highlight": [100, 160, 210],
                "button_normal": [70, 130, 180],
                "button_hover": [100, 160, 210],
                "button_disabled": [50, 50, 70],
                "warning": [220, 120, 60],
                "error": [220, 80, 60],
                "success": [60, 180, 75],
            },
            "fonts": {"title": None, "menu": None, "button": None, "hud": None},
            "images": {
                "background": None,
                "button_normal": None,
                "button_hover": None,
                "button_disabled": None,
                "logo": None,
            },
            "sounds": {
                "button_click": None,
                "button_hover": None,
                "background_music": None,
            },
            "animations": {"transition_speed": 0.3, "button_scale_on_hover": 1.05},
            "ui": {
                "border_radius": 8,
                "border_width": 2,
                "shadow_enabled": True,
                "shadow_color": [0, 0, 0, 128],
                "shadow_offset": [2, 2],
            },
        }

        self.themes["default"] = default_theme

        # Salva o tema padrão
        try:
            with open(self.themes_path / "default.json", "w", encoding="utf-8") as f:
                json.dump(default_theme, f, indent=4, ensure_ascii=False)
            print("✅ Tema padrão criado/recriado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao salvar tema padrão: {e}")

    def set_theme(self, theme_name: str) -> bool:
        """Define o tema atual"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            # print(f"🎨 Tema alterado para: {theme_name}")
            return True
        else:
            print(f"❌ Tema não encontrado: {theme_name}")
            return False

    def get_theme(self) -> Dict[str, Any]:
        """Retorna o tema atual"""
        return self.themes.get(self.current_theme, self.themes["default"])

    def get_color(self, color_key: str) -> tuple:
        """Retorna uma cor do tema atual"""
        theme = self.get_theme()
        color = theme["colors"].get(color_key, [255, 255, 255])
        return tuple(color)

    def get_image_path(self, image_key: str) -> Optional[str]:
        """Retorna o caminho de uma imagem do tema"""
        theme = self.get_theme()
        return theme["images"].get(image_key)

    def get_font_path(self, font_key: str) -> Optional[str]:
        """Retorna o caminho de uma fonte do tema"""
        theme = self.get_theme()
        return theme["fonts"].get(font_key)

    def get_sound_path(self, sound_key: str) -> Optional[str]:
        """Retorna o caminho de um som do tema"""
        theme = self.get_theme()
        return theme["sounds"].get(sound_key)

    def get_ui_setting(self, setting_key: str, default=None):
        """Retorna uma configuração de UI do tema"""
        theme = self.get_theme()
        return theme["ui"].get(setting_key, default)

    def get_animation_setting(self, setting_key: str, default=None):
        """Retorna uma configuração de animação do tema"""
        theme = self.get_theme()
        return theme["animations"].get(setting_key, default)

    def create_theme_from_current(
        self, new_theme_name: str, author: str = "Usuário"
    ) -> bool:
        """Cria um novo tema baseado no tema atual"""
        try:
            current_theme = self.get_theme().copy()
            current_theme["name"] = new_theme_name
            current_theme["author"] = author

            self.themes[new_theme_name] = current_theme

            # Salva o novo tema
            with open(
                self.themes_path / f"{new_theme_name}.json", "w", encoding="utf-8"
            ) as f:
                json.dump(current_theme, f, indent=4, ensure_ascii=False)

            print(f"✅ Novo tema criado: {new_theme_name}")
            return True

        except Exception as e:
            print(f"❌ Erro ao criar tema: {e}")
            return False

    def get_available_themes(self) -> List[str]:
        """Retorna lista de temas disponíveis"""
        return list(self.themes.keys())
