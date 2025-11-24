import pygame
import json
import os
from typing import Tuple, Dict, Optional


class IconAtlas:
    """
    Gerenciador de sprite atlas de ícones.
    Carrega uma única imagem com múltiplos ícones em grade e extrai individualmente.
    Suporta mapeamento via JSON (icon_registry.json).
    """

    def __init__(self, atlas_path: str, icon_size: int = 32):
        """
        Args:
            atlas_path: Caminho para a imagem do atlas
            icon_size: Tamanho de cada ícone (32x32 pixels)
        """
        self.atlas_path = atlas_path
        self.icon_size = icon_size
        self.atlas_image = None
        self.icon_cache: Dict[Tuple[int, int], pygame.Surface] = {}
        self.registry = {}

        # Carrega imagem
        try:
            self.atlas_image = pygame.image.load(atlas_path).convert_alpha()
            print(f"✅ Icon Atlas carregado: {atlas_path}")
        except Exception as e:
            print(f"❌ Erro ao carregar icon atlas: {e}")
            # Cria uma imagem placeholder
            self.atlas_image = pygame.Surface((icon_size, icon_size))
            self.atlas_image.fill((100, 100, 100))

        # Carrega registro JSON se existir
        registry_path = os.path.join("assets", "data", "icon_registry.json")
        if os.path.exists(registry_path):
            try:
                with open(registry_path, "r", encoding="utf-8") as f:
                    self.registry = json.load(f)
                print(
                    f"✅ Registro de ícones carregado: {len(self.registry)} categorias"
                )
            except Exception as e:
                print(f"❌ Erro ao carregar registro de ícones: {e}")

    def get_icon(self, row: int, col: int) -> pygame.Surface:
        """
        Extrai um ícone específico do atlas.

        Args:
            row: Linha do ícone (0-indexed, de cima para baixo)
            col: Coluna do ícone (0-indexed, da esquerda para direita)

        Returns:
            Surface do pygame com o ícone
        """
        # Verifica cache
        cache_key = (row, col)
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]

        # Calcula posição no atlas
        x = col * self.icon_size
        y = row * self.icon_size

        # Extrai o ícone (subsurface)
        try:
            icon_rect = pygame.Rect(x, y, self.icon_size, self.icon_size)
            icon = self.atlas_image.subsurface(icon_rect).copy()
        except Exception as e:
            print(f"⚠️ Erro ao extrair ícone ({row}, {col}): {e}")
            # Retorna placeholder
            icon = pygame.Surface((self.icon_size, self.icon_size))
            icon.fill((150, 150, 150))
            pygame.draw.rect(icon, (200, 200, 200), icon.get_rect(), 2)

        # Armazena no cache
        self.icon_cache[cache_key] = icon
        return icon

    def get_icon_by_name(self, category: str, name: str) -> Optional[pygame.Surface]:
        """
        Retorna ícone buscando pelo nome no registro JSON.

        Args:
            category: Categoria no JSON (ex: 'weapons', 'armor')
            name: Chave do item no JSON (ex: 'iron_sword')
        """
        if category in self.registry and name in self.registry[category]:
            data = self.registry[category][name]
            row, col = data["coords"]
            return self.get_icon(row, col)
        return None

    def get_scaled_icon(self, row: int, col: int, target_size: int) -> pygame.Surface:
        """
        Extrai e redimensiona um ícone.

        Args:
            row: Linha do ícone
            col: Coluna do ícone
            target_size: Tamanho desejado (ex: 40 para 40x40)

        Returns:
            Surface redimensionado
        """
        icon = self.get_icon(row, col)
        if target_size != self.icon_size:
            icon = pygame.transform.scale(icon, (target_size, target_size))
        return icon

    def clear_cache(self):
        """Limpa o cache de ícones."""
        self.icon_cache.clear()
