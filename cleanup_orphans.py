import sqlite3
import os


def cleanup_orphans():
    print("\n--- Cleaning up Orphaned Players ---")

    db_path = "saves/game_data.sqlite"
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Get all players
        cursor.execute("SELECT name FROM players")
        all_players = [row["name"] for row in cursor.fetchall()]

        # 2. Get players used in game_slots
        cursor.execute(
            "SELECT player_name FROM game_slots WHERE player_name IS NOT NULL"
        )
        active_players = [row["player_name"] for row in cursor.fetchall()]

        # 3. Identify orphans
        orphans = [p for p in all_players if p not in active_players]

        if not orphans:
            print("✅ No orphaned players found.")
        else:
            print(f"⚠️  Found {len(orphans)} orphaned players: {orphans}")

            # 4. Delete orphans
            for orphan in orphans:
                cursor.execute("DELETE FROM players WHERE name = ?", (orphan,))
                print(f"🗑️ Deleted orphan: {orphan}")

            conn.commit()
            print("✅ Cleanup complete.")

        conn.close()

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")


if __name__ == "__main__":
    cleanup_orphans()
