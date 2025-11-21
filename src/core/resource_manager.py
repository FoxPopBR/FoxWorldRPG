import pygame
import os
from pathlib import Path
from typing import Optional, Dict, Tuple


class ResourceManager:
    """Gerenciador central de recursos (imagens, sons, fontes)"""

    def __init__(self, assets_path: Path, theme_manager):
        self.assets_path = assets_path
        self.theme_manager = theme_manager

        # Caches
        self._image_cache: Dict[str, pygame.Surface] = {}
        self._font_cache: Dict[str, pygame.font.Font] = {}
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}

    def get_image(self, image_key: str) -> Optional[pygame.Surface]:
        """Obtém uma imagem do tema atual"""
        if image_key in self._image_cache:
            return self._image_cache[image_key]

        image_path = self.theme_manager.get_image_path(image_key)
        if image_path:
            return self.load_image(image_path, image_key)

        return None

    def load_image(
        self, relative_path: str, cache_key: str = None
    ) -> Optional[pygame.Surface]:
        """Carrega uma imagem de um caminho relativo"""
        if cache_key and cache_key in self._image_cache:
            return self._image_cache[cache_key]

        full_path = self.assets_path / relative_path
        if full_path.exists():
            try:
                image = pygame.image.load(str(full_path))
                # Só converte se o display estiver inicializado
                if pygame.display.get_surface() is not None:
                    image = image.convert_alpha()

                if cache_key:
                    self._image_cache[cache_key] = image
                return image
            except Exception as e:
                print(f"Erro ao carregar imagem {relative_path}: {e}")

        return None

    def get_font(self, font_type: str, size: int) -> pygame.font.Font:
        """Obtém uma fonte do tema atual"""
        cache_key = f"{font_type}_{size}"

        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        font_path = self.theme_manager.get_font_path(font_type)
        try:
            if font_path and (self.assets_path / font_path).exists():
                full_path = self.assets_path / font_path
                font = pygame.font.Font(str(full_path), size)
            else:
                font = pygame.font.Font(None, size)

            self._font_cache[cache_key] = font
            return font

        except Exception as e:
            print(f"AVISO: Erro ao carregar fonte {font_type}: {e}")
            return pygame.font.Font(None, size)

    def get_sound(self, sound_key: str) -> Optional[pygame.mixer.Sound]:
        """Obtém um som do tema atual"""
        if sound_key in self._sound_cache:
            return self._sound_cache[sound_key]

        sound_path = self.theme_manager.get_sound_path(sound_key)
        if sound_path:
            full_path = self.assets_path / sound_path
            if full_path.exists():
                try:
                    sound = pygame.mixer.Sound(str(full_path))
                    self._sound_cache[sound_key] = sound
                    return sound
                except Exception as e:
                    print(f"Erro ao carregar som {sound_key}: {e}")

        return None

    def clear_cache(self):
        """Limpa o cache de recursos"""
        self._image_cache.clear()
        self._font_cache.clear()
        self._sound_cache.clear()

    # --- Métodos Específicos de Entidades ---

    def get_hero_image(self, class_key: str, image_type: str) -> pygame.Surface:
        """
        Carrega imagem de herói.
        image_type: 'face', 'body', 'class'
        """
        cache_key = f"hero_{class_key}_{image_type}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        # Mapeamento de nomes (Chave interna -> Nome do arquivo)
        name_map = {
            "paladino": "paladin",
            "druida": "druid",
            "feiticeiro": "mago",
            # 'barbaro' e 'necromante' são iguais
        }

        file_class_name = name_map.get(class_key, class_key)

        # Tenta carregar do caminho padrão: images/classes/{class}_{type}.png
        filename = f"{file_class_name}_{image_type}.png"
        path = Path("images/classes") / filename

        image = self.load_image(str(path), cache_key)
        if image:
            return image

        # Fallback: Gera placeholder se não encontrar
        print(f"AVISO: Imagem de herói não encontrada: {path}")
        return self._create_placeholder(
            100, 100, (100, 100, 100), text=f"{class_key[:3]}"
        )

    def get_enemy_image(self, enemy_name: str) -> pygame.Surface:
        """
        Carrega imagem de inimigo pelo nome.
        Ex: "Orc Warrior" -> tenta carregar "orc.png" (simplificação do nome)
        """
        lower_name = enemy_name.lower()

        # Mapeamentos manuais para correções de nomes
        name_map = {
            "goblin": "goblim",
            "forest wolf": "lobo",
            "dark mage": "necromante_face",  # Placeholder provisório
        }

        if lower_name in name_map:
            simple_name = name_map[lower_name]
        else:
            # Simplifica o nome para buscar o arquivo (primeira palavra, lowercase)
            simple_name = lower_name.split()[0]

        cache_key = f"enemy_{simple_name}"

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        filename = f"{simple_name}.png"
        path = Path("images/enemy") / filename

        image = self.load_image(str(path), cache_key)
        if image:
            return image

        # Tenta nome exato se a simplificação falhou
        exact_name = enemy_name.lower().replace(" ", "_")
        filename_exact = f"{exact_name}.png"
        path_exact = Path("images/enemy") / filename_exact

        image = self.load_image(str(path_exact), cache_key)
        if image:
            return image

        # Fallback
        print(f"AVISO: Imagem de inimigo não encontrada: {simple_name} ou {exact_name}")
        return self._create_placeholder(64, 64, (200, 50, 50), text="Enemy")

    def get_item_icon(self, item_name: str) -> pygame.Surface:
        """
        Carrega ícone de item.
        Se não existir, gera um placeholder.
        """
        # Simplifica nome para arquivo
        simple_name = item_name.lower().replace(" ", "_")
        cache_key = f"icon_{simple_name}"

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        filename = f"{simple_name}.png"
        path = Path("images/icons") / filename

        image = self.load_image(str(path), cache_key)
        if image:
            return image

        # Fallback: Gera ícone placeholder
        return self._create_placeholder(32, 32, (50, 50, 200), text="?")

    def _create_placeholder(
        self, width: int, height: int, color: Tuple[int, int, int], text: str = ""
    ) -> pygame.Surface:
        """Cria uma imagem placeholder"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(color)
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)

        if text:
            if not pygame.font.get_init():
                pygame.font.init()
            font = pygame.font.Font(None, 20)
            text_surf = font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(width // 2, height // 2))
            surface.blit(text_surf, text_rect)

        return surface
