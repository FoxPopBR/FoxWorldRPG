#!/usr/bin/env python3
"""
FoxWorld RPG - Main Entry Point
Sistema de Debug: Altere DEBUG_MODE para controlar verbosidade
"""
import sys
import os
import traceback

# ============================================
# CONFIGURAÇÃO DE DEBUG
# ============================================
DEBUG_MODE = False  # Altere para True para ativar modo debug

# Adiciona o diretório raiz ao Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.core.game import Game


def debug_print(message):
    """Imprime mensagem apenas se DEBUG_MODE estiver ativo"""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")


def main():
    try:
        debug_print("Inicializando FoxWorld RPG...")
        game = Game(debug_mode=DEBUG_MODE)

        debug_print("Carregando estado inicial do menu...")
        from src.states.menu_state import MenuState

        game.state_manager.push_state(MenuState(game))

        debug_print("Iniciando loop principal do jogo...")
        game.run()

    except KeyboardInterrupt:
        print("\n🎮 Jogo finalizado pelo usuário (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        if DEBUG_MODE:
            print("\n📋 Traceback completo:")
            traceback.print_exc()
        else:
            print("💡 Ative DEBUG_MODE no main.py para ver detalhes completos")
        sys.exit(1)


if __name__ == "__main__":
    main()
