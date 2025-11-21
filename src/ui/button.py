# src/ui/button.py
import pygame
from src.ui.responsive_ui import ResponsiveUI


class Button:
    """
    Botão com suporte a hover, clique e escalonamento responsivo.
    Compatível com assinaturas antigas e novas.
    """

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        action=None,
        font_size=24,
        text_color=(255, 255, 255),
        bg_color=(80, 80, 120),
        hover_color=(100, 100, 200),
    ):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font_size = font_size
        self.hovered = False
        self.clicked = False

        # Cores
        self.normal_color = bg_color
        self.hover_color = hover_color
        self.click_color = (
            min(bg_color[0] + 40, 255),
            min(bg_color[1] + 40, 255),
            min(bg_color[2] + 40, 255),
        )
        self.border_color = (200, 200, 200)
        self.text_color = text_color

    @property
    def rect(self):
        """Retorna o retângulo base do botão para compatibilidade"""
        return self.base_rect

    def is_clicked(self, event, game=None):
        """
        Verifica se o botão foi clicado.
        Suporta assinatura com e sem 'game' para compatibilidade.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Calcula o retângulo escalado
            if game is not None:
                try:
                    screen_width, screen_height = game.game_config.current_resolution
                    scaled_rect = ResponsiveUI.scale_rect(
                        self.base_rect.x,
                        self.base_rect.y,
                        self.base_rect.width,
                        self.base_rect.height,
                        screen_width,
                        screen_height,
                    )
                except AttributeError:
                    # Fallback se game.game_config não estiver disponível
                    scaled_rect = self.base_rect
            else:
                scaled_rect = self.base_rect

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

    def update(self, mouse_pos, game=None):
        """
        Atualiza o estado do botão (hover).
        Suporta assinatura com e sem 'game'.
        """
        # Calcula o retângulo escalado
        if game is not None:
            try:
                screen_width, screen_height = game.game_config.current_resolution
                scaled_rect = ResponsiveUI.scale_rect(
                    self.base_rect.x,
                    self.base_rect.y,
                    self.base_rect.width,
                    self.base_rect.height,
                    screen_width,
                    screen_height,
                )
            except AttributeError:
                scaled_rect = self.base_rect
        else:
            scaled_rect = self.base_rect

        self.hovered = scaled_rect.collidepoint(mouse_pos)

        # Reset do estado de clique
        if self.clicked:
            self.clicked = False

    def is_hovered(self, mouse_pos, game=None):
        """
        Verifica se o mouse está sobre o botão.
        IMPORTANTE: Deve usar o mesmo scaling que render() para consistência!
        """
        if game is not None:
            try:
                screen_width, screen_height = game.game_config.current_resolution
                scaled_rect = ResponsiveUI.scale_rect(
                    self.base_rect.x,
                    self.base_rect.y,
                    self.base_rect.width,
                    self.base_rect.height,
                    screen_width,
                    screen_height,
                )
                return scaled_rect.collidepoint(mouse_pos)
            except AttributeError:
                # Fallback se game.game_config não estiver disponível
                pass

        # Fallback para base_rect (apenas para compatibilidade)
        return self.base_rect.collidepoint(mouse_pos)

    def on_click(self):
        """Executa a ação do botão"""
        if self.action:
            self.action()

    def render(self, surface, game_config):
        """
        Renderiza o botão na surface.
        """
        try:
            # Obtém a resolução atual para escalonamento
            current_resolution = getattr(
                game_config, "current_resolution", (1920, 1080)
            )

            # Calcula retângulo escalado
            scaled_rect = ResponsiveUI.scale_rect(
                self.base_rect.x,
                self.base_rect.y,
                self.base_rect.width,
                self.base_rect.height,
                current_resolution[0],
                current_resolution[1],
            )

            # Define cores baseadas no estado
            if self.clicked:
                color = self.click_color
            elif self.hovered:
                color = self.hover_color
            else:
                color = self.normal_color

            # Desenha o botão
            pygame.draw.rect(surface, color, scaled_rect, border_radius=8)
            pygame.draw.rect(
                surface, self.border_color, scaled_rect, 2, border_radius=8
            )

            # Renderiza o texto
            font = game_config.get_font("menu", self.font_size)
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=scaled_rect.center)
            surface.blit(text_surface, text_rect)

        except Exception as e:
            print(f"❌ Erro ao renderizar botão '{self.text}': {e}")
            # Fallback básico
            pygame.draw.rect(surface, (255, 0, 0), self.base_rect)
