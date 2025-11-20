# src/ui/button_manager.py
import pygame
from typing import List, Optional
from .button import Button

class ButtonManager:
    """
    Gerenciador centralizado para botões com assinatura consistente.
    Resolve problemas de incompatibilidade entre diferentes estados.
    """
    
    @staticmethod
    def handle_button_click(buttons: List[Button], event, game=None) -> bool:
        """
        Manipula clique em botões - compatível com chamadas antigas e novas.
        
        Args:
            buttons: Lista de botões
            event: Evento do pygame
            game: Instância do jogo (opcional para compatibilidade)
            
        Returns:
            bool: True se algum botão foi clicado
        """
        if not buttons:
            return False
            
        for button in buttons:
            try:
                # Tenta a assinatura nova primeiro (com game)
                if game is not None:
                    if hasattr(button, 'is_clicked') and callable(button.is_clicked):
                        if button.is_clicked(event, game):
                            if hasattr(button, 'action') and button.action:
                                button.action()
                            return True
                # Fallback para assinatura antiga (sem game)
                else:
                    if hasattr(button, 'is_clicked') and callable(button.is_clicked):
                        if button.is_clicked(event):
                            if hasattr(button, 'action') and button.action:
                                button.action()
                            return True
            except Exception as e:
                print(f"⚠️ Erro ao processar clique do botão: {e}")
                continue
                
        return False

    @staticmethod
    def update_buttons(buttons: List[Button], game=None):
        """
        Atualiza o estado de todos os botões (hover, etc.)
        
        Args:
            buttons: Lista de botões
            game: Instância do jogo (opcional)
        """
        if not buttons:
            return
            
        mouse_pos = pygame.mouse.get_pos()
        
        for button in buttons:
            try:
                if hasattr(button, 'update'):
                    if game is not None:
                        button.update(mouse_pos, game)
                    else:
                        button.update(mouse_pos)
            except Exception as e:
                print(f"⚠️ Erro ao atualizar botão: {e}")
                continue

    @staticmethod
    def render_buttons(buttons: List[Button], surface, game_config):
        """
        Renderiza todos os botões na surface.
        
        Args:
            buttons: Lista de botões
            surface: Surface do pygame para renderizar
            game_config: Configuração do jogo para fontes/cores
        """
        if not buttons:
            return
            
        for button in buttons:
            try:
                if hasattr(button, 'render'):
                    button.render(surface, game_config)
            except Exception as e:
                print(f"⚠️ Erro ao renderizar botão: {e}")
                continue

    @staticmethod
    def create_button(x, y, width, height, text, action=None, font_size=24):
        """
        Cria um botão com configuração padrão.
        
        Args:
            x, y: Posição
            width, height: Dimensões
            text: Texto do botão
            action: Função callback
            font_size: Tamanho da fonte
            
        Returns:
            Button: Instância do botão
        """
        return Button(x, y, width, height, text, action, font_size)