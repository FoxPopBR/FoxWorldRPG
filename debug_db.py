import sqlite3
import os

db_path = "saves/game_data.sqlite"

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("\n--- HERO CLASSES ---")
        cursor.execute("SELECT * FROM hero_classes")
        classes = cursor.fetchall()
        for c in classes:
            print(f"ID: {c['id']}, Key: {c['class_key']}, Name: {c['name']}")

        print("\n--- PLAYERS ---")
        cursor.execute("SELECT id, name, hero_class_id FROM players")
        players = cursor.fetchall()
        for p in players:
            print(f"ID: {p['id']}, Name: {p['name']}, ClassID: {p['hero_class_id']}")

        conn.close()
    except Exception as e:
        print(f"❌ Error reading database: {e}")
