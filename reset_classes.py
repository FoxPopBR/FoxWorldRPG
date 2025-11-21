import sqlite3
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath("."))

from src.database.database_manager import DatabaseManager
from src.core.game_config import GameConfig


def reset_classes():
    print("\n--- Resetting Hero Classes ---")

    # Inicializa DB Manager
    config = GameConfig()
    db = DatabaseManager(config)

    try:
        # Drop table
        cursor = db.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS hero_classes")
        db.connection.commit()
        print("✅ Dropped hero_classes table")

        # Recreate table using the updated HeroClassesTable class
        from src.database.datamaker.hero_classes import HeroClassesTable

        creator = HeroClassesTable(db)

        if creator.create_table():
            print("✅ Created hero_classes table")
            if creator.insert_base_data():
                print("✅ Inserted base data with fixed IDs")
            else:
                print("❌ Failed to insert base data")
        else:
            print("❌ Failed to create table")

        # Verify IDs
        cursor.execute("SELECT id, class_key FROM hero_classes ORDER BY id")
        classes = cursor.fetchall()
        print("\n--- New IDs ---")
        for cid, key in classes:
            print(f"ID {cid}: {key}")

    except Exception as e:
        print(f"❌ Error resetting classes: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    reset_classes()
