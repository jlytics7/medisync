-- MediSync Pharmacy Management System - database schema
-- Import with:  mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS pharmacy_db;
USE pharmacy_db;

-- Staff accounts
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    idnumber VARCHAR(50) NOT NULL UNIQUE
);

-- Medicine inventory
CREATE TABLE IF NOT EXISTS medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    quantity INT NOT NULL DEFAULT 0,
    expiry_date DATE
);

-- Purchase records
CREATE TABLE IF NOT EXISTS purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT NOT NULL,
    quantity INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    purchase_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_purchases_medicine
        FOREIGN KEY (medicine_id) REFERENCES medicines (id)
);

-- ---------------------------------------------------------------------
-- Demo data (safe to remove)
-- ---------------------------------------------------------------------

-- Demo login: category = Pharmacist, ID number = PH-2025-001
INSERT INTO users (username, category, idnumber)
VALUES ('Jessica M.', 'Pharmacist', 'PH-2025-001');

INSERT INTO medicines (medicine_name, category, price, quantity, expiry_date) VALUES
    ('Paracetamol 500mg',  'Painkiller',    5.50,  120, '2027-06-30'),
    ('Amoxicillin 500mg',  'Antibiotic',    12.75,  45, '2026-12-31'),
    ('Cetirizine 10mg',    'Antihistamine', 8.25,   8, '2027-03-15'),
    ('Vitamin C 500mg',    'Supplement',    6.00,   0, '2027-01-31'),
    ('Ibuprofen 200mg',    'Painkiller',    7.40,  60, '2026-11-30');
