import sqlite3
import os


def drop_classes():
    print("\n--- Dropping Hero Classes Table ---")
    db_path = "saves/game_data.sqlite"

    if not os.path.exists(db_path):
        print("❌ Database not found")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS hero_classes")
        conn.commit()
        print("✅ Dropped hero_classes table")
        conn.close()
    except Exception as e:
        print(f"❌ Error dropping table: {e}")


if __name__ == "__main__":
    drop_classes()
