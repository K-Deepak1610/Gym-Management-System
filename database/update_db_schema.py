import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'gym.db'))

def update_schema():
    if not os.path.exists(db_path):
        print("Database not found, no need to alter. It will be created fresh via db.py.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if risk_score exists
    cursor.execute("PRAGMA table_info(members)")
    columns = [row[1] for row in cursor.fetchall()]
    
    try:
        if 'risk_score' not in columns:
            cursor.execute("ALTER TABLE members ADD COLUMN risk_score INTEGER DEFAULT 0")
            print("Added risk_score to members.")
        if 'goal' not in columns:
            cursor.execute("ALTER TABLE members ADD COLUMN goal TEXT")
            print("Added goal to members.")
            
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            price REAL NOT NULL,
            features TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS member_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            weight REAL,
            body_fat_percentage REAL,
            recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        print("Schema successfully updated with SaaS premium features!")
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
