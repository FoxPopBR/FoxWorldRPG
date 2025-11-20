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
        
    def render(self, surface):
        self.menu.render(surface)
        
    def enter(self):
        print("Entrando no menu principal")
    
    def on_resize(self, old_size, new_size):
        """Recria o menu quando a resolução muda"""
        self.menu = MainMenu(self.game)

    def _continue_game(self):
        """Continua o jogo com o herói atual"""
        current_hero = self.game.hero_manager.get_current_hero()
        
        if not current_hero:
            print("⚠️ Nenhum herói encontrado. Crie um novo personagem.")
            self._new_game()
            return
        
        print(f"🎮 Continuando com: {current_hero.name}")
        # Aqui você carrega o estado do jogo com o herói atual
        # from src.states.game_state import GameState
        # self.game.state_manager.change_state(GameState(self.game, current_hero))
