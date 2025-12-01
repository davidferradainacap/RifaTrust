-- MySQL Initialization Script for RifaTrust
-- This script is executed when the MySQL container is first created

-- Set character set and collation
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS RifaTrust CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE RifaTrust;

-- Grant all privileges to the application user
GRANT ALL PRIVILEGES ON RifaTrust.* TO 'rifatrust_user'@'%';
FLUSH PRIVILEGES;

-- Display confirmation
SELECT 'Database RifaTrust initialized successfully' AS Status;
