# src/ui/button.py
import pygame
from src.ui.ui_scaler import UIScaler
from src.ui.ui_theme import get_theme, UITheme


class Button:
    """
    Botão com suporte a hover, clique e escalonamento responsivo via UIScaler.
    """

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        action=None,
        font_size=None,
        text_color=None,
        bg_color=None,
        hover_color=None,
        button_image_normal=None,
        button_image_pressed=None,
    ):
        """
        Inicializa o botão.
        Se cores/fontes não forem fornecidas, usa o tema padrão.
        Se imagens forem fornecidas, usa texturas em vez de cores sólidas.
        """
        self.base_rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

        # Obtém tema para defaults
        theme = get_theme()

        self.font_size = font_size if font_size is not None else theme.BUTTON_MAIN_FONT
        self.text_color = (
            text_color if text_color is not None else theme.COLOR_TEXT_PRIMARY
        )

        # Cores (usadas quando não há imagem)
        self.normal_color = (
            bg_color if bg_color is not None else theme.COLOR_BUTTON_DEFAULT
        )
        self.hover_color = (
            hover_color if hover_color is not None else theme.COLOR_BUTTON_HOVER
        )
        self.click_color = theme.COLOR_BUTTON_ACTIVE
        self.border_color = theme.COLOR_TEXT_SECONDARY

        # Imagens de textura
        self.image_normal = button_image_normal
        self.image_pressed = button_image_pressed
        self.scaled_image_normal = None
        self.scaled_image_pressed = None

        # Estado de clique com delay
        self.hovered = False
        self.clicked = False
        self.is_pressing = False
        self.press_timer = 0
        self.press_delay = 0.2  # 200ms para mostrar o efeito antes da ação
        self.pressed_scale = 0.95  # 95% do tamanho quando pressionado

        # Instância do scaler (singleton)
        self.scaler = UIScaler()

    @property
    def rect(self):
        """Retorna o retângulo base do botão"""
        return self.base_rect

    def _get_scaled_rect(self):
        """Calcula o retângulo escalado usando UIScaler"""
        return self.scaler.rect(
            self.base_rect.x,
            self.base_rect.y,
            self.base_rect.width,
            self.base_rect.height,
        )

    def is_clicked(self, event, game=None):
        """
        Verifica se o botão foi clicado.
        Argumento 'game' mantido para compatibilidade, mas não é mais necessário.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            scaled_rect = self._get_scaled_rect()

            if scaled_rect.collidepoint(mouse_pos):
                self.clicked = True
                return True

        return False

    def handle_event(self, event, game=None):
        """
        Processa eventos do botão.
        Retorna True se o evento foi consumido (clique).
        """
        if self.is_clicked(event, game):
            self.on_click()
            return True
        return False

    def update(self, mouse_pos, game=None, dt=1 / 60):
        """
        Atualiza o estado do botão (hover e timer de clique).
        """
        scaled_rect = self._get_scaled_rect()
        self.hovered = scaled_rect.collidepoint(mouse_pos)

        # Sistema de delay de clique
        if self.is_pressing:
            self.press_timer += dt
            if self.press_timer >= self.press_delay:
                self.is_pressing = False
                self.press_timer = 0
                # Executa a ação após o delay
                if self.action:
                    self.action()

        # Reset do estado de clique
        if self.clicked:
            self.clicked = False

    def is_hovered(self, mouse_pos, game=None):
        """Verifica se o mouse está sobre o botão."""
        scaled_rect = self._get_scaled_rect()
        return scaled_rect.collidepoint(mouse_pos)

    def on_click(self):
        """Inicia o efeito de clique com delay"""
        self.is_pressing = True
        self.press_timer = 0

    def render(self, surface, game_config=None):
        """
        Renderiza o botão na surface.
        Suporta texturas de imagem ou cores sólidas.
        """
        try:
            scaled_rect = self._get_scaled_rect()

            # Usa imagem se disponível, senão usa cores
            if self.image_normal and self.image_pressed:
                self._render_with_image(surface, scaled_rect)
            else:
                self._render_with_color(surface, scaled_rect)

            # Renderiza o texto sobre o botão
            self._render_text(surface, scaled_rect)

        except Exception as e:
            print(f"❌ Erro ao renderizar botão '{self.text}': {e}")
            # Fallback básico
            pygame.draw.rect(surface, (255, 0, 0), self.base_rect)

    def _render_with_image(self, surface, scaled_rect):
        """Renderiza o botão usando imagens de textura"""
        # Seleciona a imagem baseada no estado
        if self.is_pressing:
            current_image = self.image_pressed
            # Reduz o tamanho quando pressionado
            button_width = int(scaled_rect.width * self.pressed_scale)
            button_height = int(scaled_rect.height * self.pressed_scale)
        else:
            current_image = self.image_normal
            button_width = scaled_rect.width
            button_height = scaled_rect.height

        # Escala a imagem para o tamanho do botão
        scaled_image = pygame.transform.smoothscale(
            current_image, (button_width, button_height)
        )

        # Centraliza a imagem escalada
        image_x = scaled_rect.centerx - button_width // 2
        image_y = scaled_rect.centery - button_height // 2

        surface.blit(scaled_image, (image_x, image_y))

    def _render_with_color(self, surface, scaled_rect):
        """Renderiza o botão usando cores sólidas (fallback)"""
        # Define cores baseadas no estado
        if self.is_pressing:
            color = self.click_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.normal_color

        # Desenha o botão
        pygame.draw.rect(surface, color, scaled_rect, border_radius=8)
        pygame.draw.rect(surface, self.border_color, scaled_rect, 2, border_radius=8)

    def _render_text(self, surface, scaled_rect):
        """Renderiza o texto centralizado sobre o botão"""
        # Escala a fonte para caber melhor no botão
        font = self.scaler.get_font(None, self.font_size)

        text_surface = font.render(self.text, True, self.text_color)

        # Ajusta posição do texto se o botão está pressionado
        center_y = scaled_rect.centery
        if self.is_pressing:
            # Move o texto um pouco para baixo quando pressionado
            center_y += self.scaler.scale(2, "y")

        text_rect = text_surface.get_rect(center=(scaled_rect.centerx, center_y))
        surface.blit(text_surface, text_rect)
