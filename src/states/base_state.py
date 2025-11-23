from abc import ABC, abstractmethod
import pygame
from typing import Tuple


class BaseState(ABC):
    """Classe base para todos os estados do jogo"""

    def __init__(self, game):
        self.game = game

    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface):
        pass

    def enter(self):
        """Chamado quando o estado entra em foco"""
        pass

    def exit(self):
        """Chamado quando o estado sai de foco"""
        pass

    def on_resize(self, old_size: Tuple[int, int], new_size: Tuple[int, int]):
        """Chamado quando a janela é redimensionada"""
        pass

    @property
    def ui_scaler(self):
        """Atalho para o scaler de UI"""
        return self.game.ui_scaler

    @property
    def theme(self):
        """Atalho para o tema atual"""
        from src.ui.ui_theme import get_theme

        return get_theme()
