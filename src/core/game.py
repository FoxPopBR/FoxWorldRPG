import pygame
import sys
from typing import Optional
from config.display_config import DisplayConfig
from config.game_config import GameConfig
from src.core.state_manager import StateManager

class Game:
    """Classe principal do jogo"""
    
    def __init__(self):
        # Inicializa GameConfig primeiro
        self.game_config = GameConfig(self)
        
        # Agora inicializa DisplayConfig com o settings_manager
        self.display_config = DisplayConfig(self.game_config.settings_manager)
        
        self._initialize_pygame()
        self._create_window()
        self.state_manager = StateManager(self)
        self.running = True
        self.clock = pygame.time.Clock()
        
    def _initialize_pygame(self):
        """Inicializa o Pygame e sistemas relacionados"""
        try:
            pygame.init()
            pygame.font.init()
            print("Pygame inicializado com sucesso")
        except Exception as e:
            print(f"ERRO: Falha ao inicializar Pygame: {e}")
            sys.exit(1)
        
    def _create_window(self):
        """Cria a janela do jogo baseado nas configurações"""
        try:
            self.screen = pygame.display.set_mode(
                self.display_config.current_resolution,
                self.display_config.get_display_flags()
            )
            pygame.display.set_caption("FoxWorld RPG")
            print(f"Janela criada: {self.display_config.current_resolution}")
        except Exception as e:
            print(f"ERRO: Falha ao criar janela: {e}")
            sys.exit(1)
                
    def handle_events(self):
        """Processa eventos do jogo"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.state_manager.handle_event(event)
                
    def update(self):
        """Atualiza a lógica do jogo"""
        self.state_manager.update()
        
    def render(self):
        """Renderiza o jogo"""
        self.screen.fill(self.game_config.get_color('background'))
        self.state_manager.render(self.screen)
        pygame.display.flip()
        
    def run(self):
        """Loop principal do jogo"""
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(self.display_config.fps)
                
        except KeyboardInterrupt:
            print("\n⏹️  Jogo interrompido pelo usuário")
        except Exception as e:
            print(f"🔴 ERRO CRÍTICO no jogo: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Limpeza final do jogo"""
        try:
            # Salva configurações de display
            self.display_config.save_to_file()
            
            # Limpeza do game_config
            self.game_config.cleanup()
            
            print("✅ Configurações salvas e banco de dados fechado")
        except Exception as e:
            print(f"⚠️  AVISO: Não foi possível salvar configurações: {e}")
        
        pygame.quit()
        print("🎮 Jogo finalizado")
        
    def change_display_mode(self):
        """Muda o modo de display e notifica todos os estados"""
        try:
            old_resolution = self.screen.get_size()
            self.screen = pygame.display.set_mode(
                self.display_config.current_resolution,
                self.display_config.get_display_flags()
            )
            print(f"🖥️  Modo de display alterado para: {self.display_config.current_resolution}")
            
            # Notifica todos os estados sobre a mudança de resolução
            self.state_manager.on_resize(old_resolution, self.display_config.current_resolution)
            
        except Exception as e:
            print(f"🔴 ERRO: Falha ao alterar modo de display: {e}")
            raise