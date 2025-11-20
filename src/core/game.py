# src/core/game.py - VERSÃO CORRIGIDA
import pygame
import sys
from typing import Optional
from config.display_config import DisplayConfig
from config.game_config import GameConfig
from src.core.state_manager import StateManager

class Game:
    def __init__(self):
        # ✅ CORREÇÃO: Inicializa GameConfig SEM database primeiro
        self.game_config = GameConfig(self)
        
        # ✅ CORREÇÃO: Agora inicializa o database
        from src.database.database_manager import DatabaseManager
        database_manager = DatabaseManager()

        # ✅ INICIALIZAÇÃO DAS TABELAS DO JOGO
        print("🦊 Inicializando tabelas do banco de dados...")
        database_manager.initialize_game_tables(force_recreate_static=False)
        
        # ✅ CORREÇÃO: Completa a inicialização do GameConfig
        self.game_config.initialize_managers(database_manager)
        
        # Agora inicializa DisplayConfig (que precisa do settings_manager)
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
            print("✅ Pygame inicializado com sucesso")
        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar Pygame: {e}")
            sys.exit(1)
        
    def _create_window(self):
        """Cria a janela do jogo baseado nas configurações"""
        try:
            self.screen = pygame.display.set_mode(
                self.display_config.current_resolution,
                self.display_config.get_display_flags()
            )
            pygame.display.set_caption("FoxWorld RPG")
            print(f"✅ Janela criada: {self.display_config.current_resolution}")
        except Exception as e:
            print(f"❌ ERRO: Falha ao criar janela: {e}")
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
            print("🚀 Iniciando FoxWorld RPG...")
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
        """Limpeza antes de sair do jogo"""
        print("🧹 Realizando limpeza...")

        try:
            # Fecha o banco de dados
            if hasattr(self, 'game_config') and hasattr(self.game_config, 'database'):
                self.game_config.database.close()
                print("✅ Banco de dados fechado")
        except Exception as e:
            print(f"⚠️ Erro ao fechar banco de dados: {e}")

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