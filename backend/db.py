import sqlite3
import os
import sys

class Database:
    def __init__(self):
        # Database file path relative to this file
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'gym.db'))
        self.schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql'))
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database if it doesn't exist
        if not os.path.exists(self.db_path):
            self.initialize_database()

    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # This allows accessing columns by name
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to SQLite: {e}")
            return None

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        if not conn: return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"Query Error: {e}")
            print(f"Query: {query}")
            return None
        finally:
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Fetch All Error: {e}")
            return []
        finally:
            conn.close()

    def fetch_one(self, query, params=None):
        conn = self.get_connection()
        if not conn: return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Fetch One Error: {e}")
            return None
        finally:
            conn.close()

    def initialize_database(self):
        """Creates tables using the schema.sql file."""
        print("Initializing SQLite database from schema.sql...")
        if not os.path.exists(self.schema_path):
            print(f"Critical Error: Schema file not found at {self.schema_path}")
            return

        conn = self.get_connection()
        if not conn: return

        try:
            with open(self.schema_path, 'r') as f:
                schema_script = f.read()
            
            # sqlite3.executescript can run multiple SQL statements separated by ;
            conn.executescript(schema_script)
            conn.commit()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            conn.close()

db = Database()
