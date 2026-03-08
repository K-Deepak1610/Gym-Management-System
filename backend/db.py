import mysql.connector
from mysql.connector import Error, pooling
import time
import sys
import os

class Database:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'titanfit_gym'
        }
        self.pool = None
        self._initialize_pool()
        self.initialize_database()

    def _initialize_pool(self):
        try:
            # Using connection pooling for better stability and persistence
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="titanfit_pool",
                pool_size=5,
                pool_reset_session=True,
                **self.config
            )
        except Error as e:
            print(f"Error creating connection pool: {e}")
            # If database doesn't exist, we might need to connect without it first
            self._create_database_if_not_exists()
            self._initialize_pool()

    def _create_database_if_not_exists(self):
        temp_config = self.config.copy()
        db_name = temp_config.pop('database')
        try:
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Critical Error: Could not create database: {e}")
            sys.exit(1)

    def get_connection(self):
        try:
            return self.pool.get_connection()
        except Error as e:
            print(f"Error getting connection from pool: {e}")
            # Try to re-initialize if pool is broken
            self._initialize_pool()
            return self.pool.get_connection()

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor
        except Error as e:
            print(f"Query Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"Fetch All Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def fetch_one(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"Fetch One Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def initialize_database(self):
        """Creates tables using IF NOT EXISTS and ensures missing columns are added."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS trainers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                specialization VARCHAR(100),
                phone VARCHAR(20),
                experience INT DEFAULT 0,
                salary DECIMAL(10, 2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT,
                phone VARCHAR(20),
                membership_plan VARCHAR(50),
                join_date DATE,
                expiry_date DATE,
                trainer_id INT,
                status VARCHAR(20) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                member_id INT,
                attendance_date DATE,
                status VARCHAR(20),
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS equipment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                quantity INT DEFAULT 1,
                gym_condition VARCHAR(50),
                last_maintenance DATE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                member_id INT,
                amount DECIMAL(10, 2),
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_method VARCHAR(50) DEFAULT 'Cash',
                notes TEXT,
                status VARCHAR(20) DEFAULT 'Paid',
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS activity_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                action TEXT,
                admin_name VARCHAR(100) DEFAULT 'Admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS announcements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200),
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for q in queries:
            self.execute_query(q)

        # Robustly add columns if missing (handles cases where IF NOT EXISTS for ADD COLUMN is not supported)
        schema_updates = [
            ("trainers", "experience", "INT DEFAULT 0"),
            ("trainers", "salary", "DECIMAL(10, 2) DEFAULT 0.00"),
            ("members", "trainer_id", "INT"),
            ("members", "status", "VARCHAR(20) DEFAULT 'Active'"),
            ("payments", "status", "VARCHAR(20) DEFAULT 'Paid'")
        ]
        
        for table, column, definition in schema_updates:
            try:
                # Check if column exists
                cols = self.fetch_all(f"DESCRIBE {table}")
                if not any(c['Field'] == column for c in cols):
                    self.execute_query(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                    print(f"Added missing column {column} to {table}")
            except Exception as e:
                print(f"Error updating schema for {table}.{column}: {e}")

db = Database()
