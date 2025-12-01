-- Script para configurar la base de datos del Sistema de Rifas

-- Crear la base de datos con codificación UTF-8
CREATE DATABASE IF NOT EXISTS rifas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear el usuario y otorgar privilegios
CREATE USER IF NOT EXISTS 'rifas_user'@'localhost' IDENTIFIED BY 'rifas_password';
GRANT ALL PRIVILEGES ON rifas_db.* TO 'rifas_user'@'localhost';
FLUSH PRIVILEGES;

-- Seleccionar la base de datos
USE rifas_db;

-- Mostrar confirmación
SELECT 'Base de datos rifas_db creada exitosamente' AS Status;
