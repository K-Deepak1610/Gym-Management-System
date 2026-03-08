-- TitanFit Gym Management System SQLite Schema

-- 1. Trainers table
CREATE TABLE IF NOT EXISTS trainers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT,
    phone TEXT,
    experience INTEGER DEFAULT 0,
    salary REAL DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Members table
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    phone TEXT,
    membership_plan TEXT,
    join_date DATE,
    expiry_date DATE,
    trainer_id INTEGER,
    status TEXT DEFAULT 'Active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE SET NULL
);

-- 3. Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    attendance_date DATE,
    status TEXT DEFAULT 'Absent',
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    UNIQUE (member_id, attendance_date)
);

-- 4. Payments table
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    amount REAL NOT NULL,
    payment_method TEXT DEFAULT 'Cash',
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    status TEXT DEFAULT 'Paid',
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- 5. Announcements table
CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. Equipment table
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    gym_condition TEXT DEFAULT 'Good',
    last_maintenance DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 7. Activity Log table
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    admin_name TEXT DEFAULT 'Admin',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed Sample Equipment if empty
INSERT INTO equipment (name, quantity, gym_condition, last_maintenance) 
SELECT 'Treadmill', 5, 'Good', '2024-01-10'
WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE name = 'Treadmill');

INSERT INTO equipment (name, quantity, gym_condition, last_maintenance) 
SELECT 'Dumbbells Set', 12, 'Excellent', '2024-02-15'
WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE name = 'Dumbbells Set');
