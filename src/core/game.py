# src/core/game.py - VERSÃO CORRIGIDA
import pygame
import sys
from typing import Optional
from config.display_config import DisplayConfig
from config.game_config import GameConfig
from src.core.state_manager import StateManager


class Game:
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode

        # ✅ CORREÇÃO: Inicializa GameConfig SEM database primeiro
        self.game_config = GameConfig(self)

        # ✅ CORREÇÃO: Agora inicializa o database
        from src.database.database_manager import DatabaseManager

        database_manager = DatabaseManager()

        # ✅ INICIALIZAÇÃO DAS TABELAS DO JOGO
        if self.debug_mode:
            print("🦊 Inicializando tabelas do banco de dados...")
        database_manager.initialize_game_tables(force_recreate_static=False)

        # ✅ CORREÇÃO: Completa a inicialização do GameConfig
        self.game_config.initialize_managers(database_manager)

        # Agora inicializa DisplayConfig (que precisa do settings_manager)
        self.display_config = DisplayConfig(self.game_config.settings_manager)

        self._initialize_pygame()
        self._initialize_audio()
        self._create_window()

        # Inicializa o UIScaler com a resolução atual
        from src.ui.ui_scaler import UIScaler

        self.ui_scaler = UIScaler(self.display_config.current_resolution)

        self.state_manager = StateManager(self)

        # ✅ Inicializa gerenciador de notificações
        from src.ui.notification import NotificationManager

        self.notification_manager = NotificationManager()

        self.running = True
        self.clock = pygame.time.Clock()

    def _initialize_pygame(self):
        """Inicializa o Pygame e sistemas relacionados"""
        try:
            pygame.init()
            pygame.font.init()
            if self.debug_mode:
                print("✅ Pygame inicializado com sucesso")
        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar Pygame: {e}")
            sys.exit(1)

    def _initialize_audio(self):
        """Inicializa o sistema de áudio e aplica configurações"""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            # Aplica configurações iniciais
            self.apply_audio_settings()
            if self.debug_mode:
                print("✅ Sistema de áudio inicializado")
        except Exception as e:
            print(f"⚠️ Falha ao inicializar áudio: {e}")

    def apply_audio_settings(self):
        """Aplica as configurações de áudio do SettingsManager ao Pygame"""
        try:
            settings = self.game_config.settings_manager.get_audio_settings()

            master_vol = float(settings.get("master_volume", 1.0))
            music_vol = float(settings.get("music_volume", 0.8))
            sfx_vol = float(settings.get("sfx_volume", 0.9))

            # Aplica volumes (Master multiplica os outros)
            final_music_vol = master_vol * music_vol
            final_sfx_vol = master_vol * sfx_vol

            pygame.mixer.music.set_volume(final_music_vol)

            # Para sons, idealmente teríamos um SoundManager, mas podemos definir
            # o volume global se tivermos sons carregados ou futuros sons
            # Por enquanto, apenas armazenamos para uso ao tocar sons
            self.sfx_volume = final_sfx_vol

            if self.debug_mode:
                print(
                    f"🔊 Áudio atualizado: Music={final_music_vol:.2f}, SFX={final_sfx_vol:.2f}"
                )

        except Exception as e:
            print(f"⚠️ Erro ao aplicar configurações de áudio: {e}")

    def _create_window(self):
        """Cria a janela do jogo baseado nas configurações"""
        try:
            self.screen = pygame.display.set_mode(
                self.display_config.current_resolution,
                self.display_config.get_display_flags(),
            )
            pygame.display.set_caption("FoxWorld RPG")
            if self.debug_mode:
                print(f"✅ Janela criada: {self.display_config.current_resolution}")

            # Summary log
            print("✅ Sistema inicializado: Vídeo OK, Áudio OK, Banco de Dados OK")

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
        self.notification_manager.update()

    def render(self):
        """Renderiza o jogo"""
        self.screen.fill(self.game_config.get_color("background"))
        self.state_manager.render(self.screen)

        # Renderiza notificações por cima de tudo
        self.notification_manager.render(self.screen, self.game_config)

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
        if self.debug_mode:
            print("🧹 Realizando limpeza...")

        try:
            # Fecha o banco de dados
            if hasattr(self, "game_config") and hasattr(self.game_config, "database"):
                self.game_config.database.close()
                if self.debug_mode:
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
                self.display_config.get_display_flags(),
            )
            print(
                f"🖥️  Modo de display alterado para: {self.display_config.current_resolution}"
            )

            # Notifica todos os estados sobre a mudança de resolução
            self.state_manager.on_resize(
                old_resolution, self.display_config.current_resolution
            )

        except Exception as e:
            print(f"🔴 ERRO: Falha ao alterar modo de display: {e}")
            raise

    def apply_video_settings(self, resolution, fullscreen, vsync):
        """Aplica as configurações de vídeo"""
        self.display_config.current_resolution = resolution
        self.display_config.fullscreen = fullscreen
        self.display_config.vsync = vsync
        self.display_config.save_to_file()

        # Recria a janela com as novas configurações
        self.screen = pygame.display.set_mode(
            self.display_config.current_resolution,
            self.display_config.get_display_flags(),
        )

        # CRÍTICO: Atualiza o UIScaler com a nova resolução
        self.ui_scaler.update_resolution(resolution)
