-- TitanFit Gym Management System Enterprise Schema

CREATE DATABASE IF NOT EXISTS titanfit_gym;
USE titanfit_gym;

-- 1. Trainers table (No changes needed, but ensuring it exists)
CREATE TABLE IF NOT EXISTS trainers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Members table (Updated with status and trainer_id)
CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    phone VARCHAR(20),
    membership_plan VARCHAR(50),
    join_date DATE,
    expiry_date DATE,
    trainer_id INT DEFAULT NULL,
    status ENUM('Active', 'Expiring Soon', 'Expired') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE SET NULL
);

-- 3. Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    attendance_date DATE,
    status ENUM('Present', 'Absent') DEFAULT 'Absent',
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    UNIQUE KEY (member_id, attendance_date)
);

-- 4. Payments table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'Cash',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- 5. Announcements table
CREATE TABLE IF NOT EXISTS announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Equipment table (NEW)
CREATE TABLE IF NOT EXISTS equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity INT DEFAULT 1,
    gym_condition VARCHAR(50) DEFAULT 'Good',
    last_maintenance DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Activity Log table (NEW)
CREATE TABLE IF NOT EXISTS activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    admin_name VARCHAR(100) DEFAULT 'Admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed Sample Equipment if empty
INSERT INTO equipment (name, quantity, gym_condition, last_maintenance) 
SELECT 'Treadmill', 5, 'Good', '2024-01-10'
WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE name = 'Treadmill');

INSERT INTO equipment (name, quantity, gym_condition, last_maintenance) 
SELECT 'Dumbbells Set', 12, 'Excellent', '2024-02-15'
WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE name = 'Dumbbells Set');
