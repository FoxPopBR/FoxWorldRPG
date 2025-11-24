import pygame
from src.states.base_state import BaseState
from src.ui.menu import MainMenu


class MenuState(BaseState):
    """Estado do menu principal"""

    def __init__(self, game):
        super().__init__(game)
        self.menu = MainMenu(game)

    def handle_event(self, event):
        self.menu.handle_event(event)

    def update(self):
        self.menu.update()

    def render(self, surface, world_surface=None):
        self.menu.render(surface)

    def enter(self):
        print("Entrando no menu principal")

    def on_resize(self, old_size, new_size):
        """Recria o menu quando a resolução muda"""
        self.menu = MainMenu(self.game)
