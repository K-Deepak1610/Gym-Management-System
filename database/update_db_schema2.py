import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'gym.db'))

def update_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            email TEXT
        )
        ''')
        
        # Check if admin exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            from werkzeug.security import generate_password_hash
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          ('admin', generate_password_hash('admin123'), 'admin'))
            print("Seeded default admin user (admin / admin123)")
            
        conn.commit()
        print("Schema successfully updated with authentication system!")
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
