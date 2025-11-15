import pygame
from typing import List
from src.ui.button import Button

class ButtonManager:
    """Gerenciador centralizado para botões"""
    
    @staticmethod
    def update_buttons(buttons: List[Button], game) -> None:
        """Atualiza todos os botões de uma lista"""
        mouse_pos = pygame.mouse.get_pos()
        screen_size = game.screen.get_size()
        for button in buttons:
            button.update(mouse_pos, screen_size[0], screen_size[1], game.game_config)
    
    @staticmethod
    def render_buttons(buttons: List[Button], surface, game_config) -> None:
        """Renderiza todos os botões de uma lista"""
        for button in buttons:
            button.render(surface, game_config)
    
    @staticmethod
    def handle_button_click(buttons: List[Button], event) -> bool:
        """Processa clique em botões e retorna True se algum botão foi clicado"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in buttons:
                if button.is_hovered():
                    button.click()
                    return True
        return False