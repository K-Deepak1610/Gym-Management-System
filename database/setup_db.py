import mysql.connector
from werkzeug.security import generate_password_hash
import sys
import os

# Add the project root to path so we can import db_manager
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.db_manager import DatabaseManager

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'titanfit_gym'
}

def setup_database():
    # Connect without database first to create it
    try:
        # Connect without database first
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"Database '{DB_CONFIG['database']}' ensured.")
        
        # Connect to the database
        conn.database = DB_CONFIG['database']
        
        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        # Execute multi-statement SQL
        for result in cursor.execute(schema_sql, multi=True):
            pass
            
        conn.commit()
        print("Database schema successfully synchronized.")
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return
    
    # Seed Admin User
    admin_pass = generate_password_hash('admin123')
    try:
        cursor.execute("INSERT IGNORE INTO users (username, password, role) VALUES (%s, %s, %s)", 
                       ('admin', admin_pass, 'admin'))
        conn.commit()
        print("Admin user 'admin' with password 'admin123' ensured.")
    except Exception as e:
        print(f"Error seeding admin: {e}")

    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()
