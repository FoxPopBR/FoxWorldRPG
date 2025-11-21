import sqlite3
import os

db_path = "saves/game_data.sqlite"

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get valid class IDs
        cursor.execute("SELECT id FROM hero_classes")
        valid_ids = [row[0] for row in cursor.fetchall()]

        if not valid_ids:
            print("❌ No hero classes found! Something is wrong.")
        else:
            print(f"✅ Valid Class IDs: {valid_ids}")

            # Find invalid players
            placeholders = ",".join(["?"] * len(valid_ids))
            query = f"SELECT name, hero_class_id FROM players WHERE hero_class_id NOT IN ({placeholders})"
            cursor.execute(query, valid_ids)
            invalid_players = cursor.fetchall()

            if invalid_players:
                print(f"⚠️ Found {len(invalid_players)} players with invalid class IDs:")
                for name, cid in invalid_players:
                    print(f"   - {name} (ClassID: {cid})")

                # Delete them
                delete_query = (
                    f"DELETE FROM players WHERE hero_class_id NOT IN ({placeholders})"
                )
                cursor.execute(delete_query, valid_ids)
                conn.commit()
                print(f"🗑️ Deleted {cursor.rowcount} invalid players.")
            else:
                print("✅ No invalid players found.")

        conn.close()
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
