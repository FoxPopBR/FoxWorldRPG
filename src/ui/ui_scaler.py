"""
Sistema Profissional de UI Scaling
===================================

Baseado nas melhores práticas de Unity, Godot e Pygame:

1. **Virtual Resolution (Resolução de Referência)**
   - Toda UI é desenhada em 1920x1080 (base)
   - Sistema escala automaticamente para resolução real

2. **Canvas Scaler Pattern**
   - Um único ponto de controle para toda escala
   - Cache de fontes para performance
   - Suporta múltiplos modos de escala (width, height, balanced)

3. **Aspect Ratio Preservation**
   - Usa escala independente por eixo (X e Y)
   - Mantém proporções corretas em aspect ratios diferentes

Técnicas Matemáticas Aplicadas:
-------------------------------

1. **Linear Scaling**:
   scale_x = current_width / base_width
   scale_y = current_height / base_height

2. **Uniform Scaling** (para fontes/elementos que devem manter proporção):
   scale = min(scale_x, scale_y)

3. **Letterbox/Pillarbox** (para manter aspect ratio fixo):
   - Calcula offset para centralizar conteúdo
"""

import pygame
from typing import Dict, Tuple, Optional


class UIScaler:
    """
    Singleton que gerencia escalonamento de toda UI do jogo.

    Baseado no padrão Canvas Scaler do Unity e técnicas de
    resolução virtual do Godot/Pygame.
    """

    # Resolução base (virtual) - toda UI é desenhada para isso
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080

    _instance: Optional["UIScaler"] = None

    def __new__(cls, *args, **kwargs):
        """Garante singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, current_resolution: Tuple[int, int] = (1920, 1080)):
        """
        Inicializa o scaler.

        Args:
            current_resolution: Tupla (width, height) da resolução atual
        """
        # Evita reinicialização se já foi criado
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self._font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}
        self._surface_cache: Dict[str, pygame.Surface] = {}

        self.update_resolution(current_resolution)

    def update_resolution(self, resolution: Tuple[int, int]):
        """
        Atualiza resolução e recalcula fatores de escala.
        DEVE ser chamado quando resolução muda.

        Args:
            resolution: Nova resolução (width, height)
        """
        self.width, self.height = resolution

        # Fatores de escala independentes por eixo
        self.scale_x = self.width / self.BASE_WIDTH
        self.scale_y = self.height / self.BASE_HEIGHT

        # ✅ Escala uniforme BALANCEADA (Unity Match 0.5 - Padrão da Indústria)
        # Média entre scale_x e scale_y para melhor aproveitamento de espaço
        self.scale_uniform = (self.scale_x + self.scale_y) / 2

        # Mantém escala mínima para casos específicos (letterboxing)
        self.scale_min = min(self.scale_x, self.scale_y)
        self.scale_max = max(self.scale_x, self.scale_y)

        # 🔍 DEBUG: Mostra valores de escala
        print(f"\n🔍 UISCALER DEBUG - Resolução: {self.width}x{self.height}")
        print(f"   scale_x: {self.scale_x:.4f}")
        print(f"   scale_y: {self.scale_y:.4f}")
        print(f"   scale_uniform (BALANCED): {self.scale_uniform:.4f}")
        print(f"   scale_min: {self.scale_min:.4f}")
        print(
            f"   Aspect Ratio: {(self.width / self.height):.3f} (base: {(self.BASE_WIDTH / self.BASE_HEIGHT):.3f})\n"
        )

        # Limpa caches quando resolução muda
        self._font_cache.clear()
        self._surface_cache.clear()

    # ==========================================
    # MÉTODOS DE ESCALA DE VALORES
    # ==========================================

    def scale(self, value: float, axis: str = "uniform") -> int:
        """
        Escala um valor numérico.

        Args:
            value: Valor base (em coordenadas 1920x1080)
            axis: 'x', 'y', 'uniform' (padrão), 'width', 'height'

        Returns:
            Valor escalado para resolução atual
        """
        if axis in ("x", "width"):
            return int(value * self.scale_x)
        elif axis in ("y", "height"):
            return int(value * self.scale_y)
        else:  # 'uniform' ou qualquer outro
            return int(value * self.scale_uniform)

    def scale_tuple(self, values: Tuple[float, float]) -> Tuple[int, int]:
        """
        Escala uma tupla (x, y) usando escala independente.

        Args:
            values: Tupla (x, y) em coordenadas base

        Returns:
            Tupla (x, y) escalada
        """
        return (int(values[0] * self.scale_x), int(values[1] * self.scale_y))

    # ==========================================
    # MÉTODOS PARA RECTS E POSICIONAMENTO
    # ==========================================

    def rect(self, x: float, y: float, width: float, height: float) -> pygame.Rect:
        """
        Cria um pygame.Rect escalado.

        Args:
            x, y: Posição base
            width, height: Dimensões base

        Returns:
            Rect escalado para resolução atual
        """
        return pygame.Rect(
            int(x * self.scale_x),
            int(y * self.scale_y),
            int(width * self.scale_x),
            int(height * self.scale_y),
        )

    def center_x(self, element_width: float) -> int:
        """
        Retorna posição X para centralizar elemento.

        Args:
            element_width: Largura do elemento (em coordenadas base)

        Returns:
            Posição X centralizada (escalada)
        """
        base_center_x = (self.BASE_WIDTH - element_width) // 2
        return int(base_center_x * self.scale_x)

    def center_y(self, element_height: float) -> int:
        """
        Retorna posição Y para centralizar elemento.

        Args:
            element_height: Altura do elemento (em coordenadas base)

        Returns:
            Posição Y centralizada (escalada)
        """
        base_center_y = (self.BASE_HEIGHT - element_height) // 2
        return int(base_center_y * self.scale_y)

    # ==========================================
    # MÉTODOS PARA FONTES
    # ==========================================

    def font_size(self, base_size: int) -> int:
        """
        Calcula tamanho de fonte escalado.
        Usa escala uniforme para manter legibilidade.

        Args:
            base_size: Tamanho de fonte em 1920x1080

        Returns:
            Tamanho escalado (mínimo 10px para legibilidade)
        """
        scaled = int(base_size * self.scale_uniform)
        return max(scaled, 10)  # Tamanho mínimo

    def get_font(
        self, font_path: Optional[str], base_size: int, system_font: bool = False
    ) -> pygame.font.Font:
        """
        Retorna fonte escalada com cache.

        Args:
            font_path: Caminho para arquivo de fonte ou nome da fonte do sistema
            base_size: Tamanho base da fonte
            system_font: Se True, usa pygame.font.SysFont
        """
        scaled_size = self.font_size(base_size)
        cache_key = (font_path or "default", scaled_size, system_font)

        if cache_key not in self._font_cache:
            if system_font and font_path:
                font = pygame.font.SysFont(font_path, scaled_size)
            elif font_path:
                font = pygame.font.Font(font_path, scaled_size)
            else:
                font = pygame.font.Font(None, scaled_size)

            self._font_cache[cache_key] = font

        return self._font_cache[cache_key]

    # ==========================================
    # MÉTODOS UTILITÁRIOS
    # ==========================================

    def unscale_pos(self, screen_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Converte posição da tela (ex: mouse) para coordenadas base.
        Útil para detectar cliques em elementos definidos em coordenadas base.

        Args:
            screen_pos: Posição (x, y) na tela real

        Returns:
            Posição (x, y) em coordenadas base (1920x1080)
        """
        return (int(screen_pos[0] / self.scale_x), int(screen_pos[1] / self.scale_y))

    def get_scale_factors(self) -> Dict[str, float]:
        """
        Retorna dicionário com todos os fatores de escala.
        Útil para debug.
        """
        return {
            "width": self.width,
            "height": self.height,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "scale_uniform": self.scale_uniform,
            "base_width": self.BASE_WIDTH,
            "base_height": self.BASE_HEIGHT,
        }

    def clear_caches(self):
        """Limpa todos os caches. Útil ao mudar assets."""
        self._font_cache.clear()
        self._surface_cache.clear()

    # ==========================================
    # INTEGRAÇÃO COM UITheme (Métodos Convenientes)
    # ==========================================

    def get_themed_font(self, font_type: str) -> pygame.font.Font:
        """
        Retorna fonte do tema já escalada.

        Args:
            font_type: 'title_large', 'title', 'menu', 'hud', etc.

        Returns:
            Fonte escalada baseada no tema

        Exemplo:
            font = scaler.get_themed_font('title')  # Retorna fonte de título escalada
        """
        from src.ui.ui_theme import get_theme

        theme = get_theme()

        size_map = {
            "title_large": theme.FONT_TITLE_LARGE,
            "title": theme.FONT_TITLE_MEDIUM,
            "title_small": theme.FONT_TITLE_SMALL,
            "subtitle": theme.FONT_TITLE_SMALL,
            "menu": theme.FONT_MENU_MEDIUM,
            "menu_large": theme.FONT_MENU_LARGE,
            "menu_small": theme.FONT_MENU_SMALL,
            "button": theme.BUTTON_MAIN_FONT,
            "hud": theme.FONT_HUD_MEDIUM,
            "hud_large": theme.FONT_HUD_LARGE,
        }

        base_size = size_map.get(font_type, theme.FONT_MENU_MEDIUM)
        return self.get_font(None, base_size)

    def get_button_rect(
        self, x: float, y: float, button_type: str = "main"
    ) -> pygame.Rect:
        """
        Cria rect de botão baseado no tema.

        Args:
            x, y: Posição base
            button_type: 'main', 'secondary', 'small'

        Returns:
            Rect de botão escalado
        """
        from src.ui.ui_theme import get_theme

        theme = get_theme()

        if button_type == "main":
            return self.rect(x, y, theme.BUTTON_MAIN_WIDTH, theme.BUTTON_MAIN_HEIGHT)
        elif button_type == "secondary":
            return self.rect(
                x, y, theme.BUTTON_SECONDARY_WIDTH, theme.BUTTON_SECONDARY_HEIGHT
            )
        else:  # 'small'
            return self.rect(x, y, theme.BUTTON_SMALL_WIDTH, theme.BUTTON_SMALL_HEIGHT)

    def get_spacing(self, spacing_type: str = "medium") -> int:
        """
        Retorna espaçamento do tema, escalado.

        Args:
            spacing_type: 'tiny', 'small', 'medium', 'large', 'huge'

        Returns:
            Espaçamento escalado
        """
        from src.ui.ui_theme import get_theme

        theme = get_theme()

        spacing_map = {
            "tiny": theme.SPACING_TINY,
            "small": theme.SPACING_SMALL,
            "medium": theme.SPACING_MEDIUM,
            "large": theme.SPACING_LARGE,
            "huge": theme.SPACING_HUGE,
        }

        base = spacing_map.get(spacing_type, theme.SPACING_MEDIUM)
        return self.scale(base)

    def scale_image(
        self,
        image: pygame.Surface,
        target_width: int = None,
        target_height: int = None,
        maintain_aspect: bool = True,
    ) -> pygame.Surface:
        """
        Escala uma imagem para target width ou height mantendo aspect ratio.

        Args:
            image: Superfície pygame a ser escalada
            target_width: Largura alvo (em pixels da tela real)
            target_height: Altura alvo (em pixels da tela real)
            maintain_aspect: Se True, mantém proporção da imagem

        Returns:
            Imagem escalada

        Uso:
            # Escalar para 60% da largura da tela
            scaled = scaler.scale_image(image, target_width=int(screen_width * 0.6))
        """
        if not image:
            return image

        original_width = image.get_width()
        original_height = image.get_height()

        if not maintain_aspect:
            # Escala direta sem manter proporção
            if target_width and target_height:
                return pygame.transform.scale(image, (target_width, target_height))
            elif target_width:
                return pygame.transform.scale(image, (target_width, original_height))
            elif target_height:
                return pygame.transform.scale(image, (original_width, target_height))
            return image

        # Mantém aspect ratio
        if target_width and target_height:
            # Usa o menor fator de escala para garantir que cabe
            scale_factor = min(
                target_width / original_width, target_height / original_height
            )
        elif target_width:
            scale_factor = target_width / original_width
        elif target_height:
            scale_factor = target_height / original_height
        else:
            return image  # Sem dimensão alvo, retorna original

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        return pygame.transform.scale(image, (new_width, new_height))
