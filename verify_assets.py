import pygame
import sys
import os
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.append(os.getcwd())

from config.game_config import GameConfig
from src.database.database_manager import DatabaseManager
from src.entities.hero import HeroClass
from src.ui.inventory_ui import InventoryUI


def verify():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((800, 600))  # Necessário para carregar imagens

    print("🚀 Iniciando verificação...")

    # 1. Inicializa Database
    db_manager = DatabaseManager()
    db_manager.initialize_game_tables()

    # 2. Inicializa GameConfig e Managers
    config = GameConfig()
    config.initialize_managers(db_manager)

    # 3. Verifica ResourceManager
    print("\n🖼️ Verificando ResourceManager:")
    rm = config.resource_manager

    # Hero Images
    hero_face = rm.get_hero_image("barbaro", "face")
    print(f"  - Hero Face (Barbaro): {'✅ OK' if hero_face else '❌ FALHA'}")

    hero_body = rm.get_hero_image("barbaro", "body")
    print(f"  - Hero Body (Barbaro): {'✅ OK' if hero_body else '❌ FALHA'}")

    # Enemy Images
    enemy_img = rm.get_enemy_image("Orc Warrior")
    print(f"  - Enemy Image (Orc Warrior): {'✅ OK' if enemy_img else '❌ FALHA'}")

    # Item Icons (Placeholder)
    item_icon = rm.get_item_icon("Espada de Ferro")
    print(f"  - Item Icon (Espada de Ferro): {'✅ OK' if item_icon else '❌ FALHA'}")

    # 4. Verifica HeroManager e Assets
    print("\n🦸 Verificando HeroManager:")
    hero_manager = config.hero_manager
    # Cria um herói de teste
    hero = hero_manager.create_hero("TestHero", HeroClass.BARBARIAN, {"forca": 10})

    print(f"  - Hero Created: {hero.name}")
    print(f"  - Hero Image Face: {'✅ OK' if hero.image_face else '❌ FALHA'}")
    print(f"  - Hero Image Body: {'✅ OK' if hero.image_body else '❌ FALHA'}")
    print(f"  - Hero Inventory: {hero.inventory}")

    # 5. Verifica EnemyManager
    print("\n👾 Verificando EnemyManager:")
    enemy_manager = config.enemy_manager
    enemies = enemy_manager.get_all_enemies()
    print(f"  - Total Enemies Loaded: {len(enemies)}")
    if enemies:
        first_enemy = enemies[0]
        print(f"  - First Enemy: {first_enemy.name}")
        print(f"  - Enemy Image: {'✅ OK' if first_enemy.image else '❌ FALHA'}")

    # 6. Verifica InventoryUI
    print("\n🎒 Verificando InventoryUI:")
    # Adiciona item ao inventário
    hero.inventory.append(
        {"name": "Espada de Ferro", "quantity": 1, "description": "Uma espada."}
    )

    # Mock Game object for UI
    class MockGame:
        def __init__(self, config, hero_mgr):
            self.game_config = config
            self.hero_manager = hero_mgr

    mock_game = MockGame(config, hero_manager)
    inventory_ui = InventoryUI(mock_game)

    surface = pygame.Surface((400, 600))
    try:
        inventory_ui.render(surface, pygame.Rect(0, 0, 400, 600))
        print("  - InventoryUI Render: ✅ OK")
    except Exception as e:
        print(f"  - InventoryUI Render: ❌ FALHA ({e})")

    # Limpeza
    hero_manager.delete_hero("TestHero")
    db_manager.close()
    pygame.quit()


if __name__ == "__main__":
    verify()
