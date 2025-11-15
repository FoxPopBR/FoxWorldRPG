import sys
import os

# Adiciona o diretório raiz ao Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Resto do código...
#!/usr/bin/env python3
import traceback
from src.core.game import Game

def main():
    try:
        game = Game()
        
        # Inicia com o estado do menu principal
        from src.states.menu_state import MenuState
        game.state_manager.push_state(MenuState(game))
        
        game.run()
        
    except Exception as e:
        print(f"Erro fatal no jogo: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()