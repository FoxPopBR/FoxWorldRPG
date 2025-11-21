import sqlite3
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath("."))

from src.ui.button import Button
import pygame


def verify_button_fix():
    print("\n--- Verifying Button Fix ---")
    try:
        pygame.init()
        btn = Button(0, 0, 100, 50, "Test")

        # Teste 1: update sem game (deve funcionar)
        btn.update((0, 0))
        print("✅ Button.update((0,0)) passed")

        # Teste 2: update com game (deve funcionar)
        class MockGame:
            class Config:
                current_resolution = (800, 600)

            game_config = Config()

        btn.update((0, 0), MockGame())
        print("✅ Button.update((0,0), game) passed")

    except Exception as e:
        print(f"❌ Button fix FAILED: {e}")


def verify_db_ids():
    print("\n--- Verifying DB IDs ---")
    db_path = "saves/game_data.sqlite"
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, class_key FROM hero_classes ORDER BY id")
    classes = cursor.fetchall()

    expected_ids = {
        "barbaro": 1,
        "paladino": 2,
        "druida": 3,
        "feiticeiro": 4,
        "necromante": 5,
    }

    all_ok = True
    for cid, key in classes:
        if expected_ids.get(key) != cid:
            print(
                f"❌ ID Mismatch for {key}: Expected {expected_ids.get(key)}, got {cid}"
            )
            all_ok = False
        else:
            print(f"✅ {key}: ID {cid} OK")

    if all_ok:
        print("✅ All Class IDs are correct and stable.")

    conn.close()


if __name__ == "__main__":
    verify_button_fix()
    verify_db_ids()
