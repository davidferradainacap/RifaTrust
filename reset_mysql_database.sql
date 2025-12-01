-- ============================================
-- SCRIPT DE REINICIO COMPLETO DE BASE DE DATOS
-- RifaTrust - Borrado y recreación de tablas MySQL
-- ============================================
--
-- INSTRUCCIONES DE USO:
--
-- OPCIÓN 1 - Ejecutar desde archivo (Recomendado):
--   1. Abrir MySQL:
--      mysql -u root -p
--
--   2. Seleccionar tu base de datos:
--      USE rifatrust;
--      (o el nombre de tu base de datos)
--
--   3. Ejecutar el script:
--      source C:/Users/dalde/OneDrive/Desktop/inacap/RS_project/reset_mysql_database.sql
--
--   4. Salir de MySQL:
--      exit
--
--   5. Ejecutar migraciones Django:
--      python manage.py migrate --fake-initial
--
--   6. Crear superusuario:
--      python manage.py createsuperuser
--
--
-- OPCIÓN 2 - Copiar y pegar directamente:
--   1. mysql -u root -p
--   2. USE tu_base_datos;
--   3. Seleccionar TODO este archivo (Ctrl+A)
--   4. Copiar (Ctrl+C)
--   5. Pegar en la consola de MySQL (clic derecho)
--   6. Presionar Enter
--   7. exit
--   8. python manage.py migrate --fake-initial
--   9. python manage.py createsuperuser
--
-- ============================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;

-- ============================================
-- PASO 1: BORRAR TODAS LAS TABLAS EXISTENTES
-- ============================================

DROP TABLE IF EXISTS `admin_panel_auditlog`;
DROP TABLE IF EXISTS `payments_refund`;
DROP TABLE IF EXISTS `payments_payment_boletos`;
DROP TABLE IF EXISTS `payments_payment`;
DROP TABLE IF EXISTS `raffles_organizersponsorrequest`;
DROP TABLE IF EXISTS `raffles_sponsorshiprequest`;
DROP TABLE IF EXISTS `raffles_winner`;
DROP TABLE IF EXISTS `raffles_ticket`;
DROP TABLE IF EXISTS `raffles_raffle`;
DROP TABLE IF EXISTS `users_notification`;
DROP TABLE IF EXISTS `users_profile`;
DROP TABLE IF EXISTS `users_user_groups`;
DROP TABLE IF EXISTS `users_user_user_permissions`;
DROP TABLE IF EXISTS `users_user`;
DROP TABLE IF EXISTS `django_admin_log`;
DROP TABLE IF EXISTS `django_content_type`;
DROP TABLE IF EXISTS `auth_permission`;
DROP TABLE IF EXISTS `auth_group_permissions`;
DROP TABLE IF EXISTS `auth_group`;
DROP TABLE IF EXISTS `django_session`;
DROP TABLE IF EXISTS `django_migrations`;

-- ============================================
-- PASO 2: CREAR TABLA DE USUARIOS
-- ============================================

CREATE TABLE `users_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL DEFAULT '0',
  `email` varchar(254) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `telefono` varchar(255) NOT NULL,
  `rol` varchar(20) NOT NULL DEFAULT 'participante',
  `avatar` varchar(100) DEFAULT NULL,
  `cuenta_validada` tinyint(1) NOT NULL DEFAULT '1',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `is_staff` tinyint(1) NOT NULL DEFAULT '0',
  `fecha_registro` datetime(6) NOT NULL,
  `ultima_conexion` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `users_user_email_idx` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 3: CREAR TABLA DE PERFILES
-- ============================================

CREATE TABLE `users_profile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `direccion` text NOT NULL,
  `ciudad` varchar(255) NOT NULL,
  `estado` varchar(255) NOT NULL,
  `codigo_postal` varchar(255) NOT NULL,
  `pais` varchar(100) NOT NULL DEFAULT 'México',
  `fecha_nacimiento` date DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `users_profile_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 4: CREAR TABLA DE RIFAS
-- ============================================

CREATE TABLE `raffles_raffle` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) NOT NULL,
  `descripcion` longtext NOT NULL,
  `imagen` varchar(100) DEFAULT NULL,
  `precio_boleto` decimal(10,2) NOT NULL,
  `total_boletos` int NOT NULL,
  `boletos_vendidos` int NOT NULL DEFAULT '0',
  `fecha_inicio` datetime(6) NOT NULL,
  `fecha_sorteo` datetime(6) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'borrador',
  `premio_principal` varchar(200) NOT NULL,
  `descripcion_premio` longtext NOT NULL,
  `imagen_premio` varchar(100) DEFAULT NULL,
  `valor_premio` decimal(12,2) DEFAULT NULL,
  `documento_legal` varchar(100) DEFAULT NULL,
  `permite_multiples_boletos` tinyint(1) NOT NULL DEFAULT '1',
  `max_boletos_por_usuario` int NOT NULL DEFAULT '10',
  `fecha_solicitud` datetime(6) DEFAULT NULL,
  `fecha_revision_aprobacion` datetime(6) DEFAULT NULL,
  `comentarios_revision` longtext,
  `motivo_rechazo` longtext,
  `motivo_pausa` longtext,
  `fecha_pausa` datetime(6) DEFAULT NULL,
  `revision_admin` longtext,
  `fecha_revision` datetime(6) DEFAULT NULL,
  `nueva_fecha_sorteo` datetime(6) DEFAULT NULL,
  `organizador_id` bigint NOT NULL,
  `revisado_por_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `raffles_raffle_organizador_id_fk` (`organizador_id`),
  KEY `raffles_raffle_revisado_por_id_fk` (`revisado_por_id`),
  KEY `raffles_raffle_estado_idx` (`estado`),
  KEY `raffles_raffle_fecha_sorteo_idx` (`fecha_sorteo`),
  CONSTRAINT `raffles_raffle_organizador_id_fk` FOREIGN KEY (`organizador_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `raffles_raffle_revisado_por_id_fk` FOREIGN KEY (`revisado_por_id`) REFERENCES `users_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 5: CREAR TABLA DE BOLETOS
-- ============================================

CREATE TABLE `raffles_ticket` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `numero_boleto` int NOT NULL,
  `fecha_compra` datetime(6) NOT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'reservado',
  `codigo_qr` varchar(100) NOT NULL,
  `rifa_id` bigint NOT NULL,
  `usuario_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_qr` (`codigo_qr`),
  UNIQUE KEY `raffles_ticket_rifa_numero_unique` (`rifa_id`, `numero_boleto`),
  KEY `raffles_ticket_usuario_id_fk` (`usuario_id`),
  KEY `raffles_ticket_estado_idx` (`estado`),
  CONSTRAINT `raffles_ticket_rifa_id_fk` FOREIGN KEY (`rifa_id`) REFERENCES `raffles_raffle` (`id`) ON DELETE CASCADE,
  CONSTRAINT `raffles_ticket_usuario_id_fk` FOREIGN KEY (`usuario_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 6: CREAR TABLA DE PAGOS
-- ============================================

CREATE TABLE `payments_payment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `monto` decimal(10,2) NOT NULL,
  `metodo_pago` varchar(20) NOT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'pendiente',
  `transaction_id` varchar(400) NOT NULL,
  `payment_intent_id` varchar(400) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_completado` datetime(6) DEFAULT NULL,
  `descripcion` longtext NOT NULL,
  `notas_admin` longtext NOT NULL,
  `usuario_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`),
  KEY `payments_payment_usuario_id_fk` (`usuario_id`),
  KEY `payments_payment_estado_idx` (`estado`),
  CONSTRAINT `payments_payment_usuario_id_fk` FOREIGN KEY (`usuario_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 7: CREAR TABLA RELACIÓN PAGO-BOLETOS
-- ============================================

CREATE TABLE `payments_payment_boletos` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `payment_id` bigint NOT NULL,
  `ticket_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `payments_payment_boletos_unique` (`payment_id`, `ticket_id`),
  KEY `payments_payment_boletos_ticket_id_fk` (`ticket_id`),
  CONSTRAINT `payments_payment_boletos_payment_id_fk` FOREIGN KEY (`payment_id`) REFERENCES `payments_payment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `payments_payment_boletos_ticket_id_fk` FOREIGN KEY (`ticket_id`) REFERENCES `raffles_ticket` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 8: CREAR TABLA DE REEMBOLSOS
-- ============================================

CREATE TABLE `payments_refund` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `monto` decimal(10,2) NOT NULL,
  `motivo` varchar(50) NOT NULL DEFAULT 'otro',
  `razon` longtext NOT NULL,
  `fecha_solicitud` datetime(6) NOT NULL,
  `fecha_procesado` datetime(6) DEFAULT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'solicitado',
  `pago_id` bigint NOT NULL,
  `procesado_por_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pago_id` (`pago_id`),
  KEY `payments_refund_procesado_por_id_fk` (`procesado_por_id`),
  CONSTRAINT `payments_refund_pago_id_fk` FOREIGN KEY (`pago_id`) REFERENCES `payments_payment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `payments_refund_procesado_por_id_fk` FOREIGN KEY (`procesado_por_id`) REFERENCES `users_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 9: CREAR TABLA DE NOTIFICACIONES
-- ============================================

CREATE TABLE `users_notification` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tipo` varchar(30) NOT NULL,
  `titulo` varchar(200) NOT NULL,
  `mensaje` longtext NOT NULL,
  `enlace` varchar(500) NOT NULL,
  `leida` tinyint(1) NOT NULL DEFAULT '0',
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_lectura` datetime(6) DEFAULT NULL,
  `usuario_id` bigint NOT NULL,
  `rifa_relacionada_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `users_notification_usuario_id_fk` (`usuario_id`),
  KEY `users_notification_rifa_id_fk` (`rifa_relacionada_id`),
  KEY `users_notification_leida_idx` (`leida`),
  CONSTRAINT `users_notification_usuario_id_fk` FOREIGN KEY (`usuario_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `users_notification_rifa_id_fk` FOREIGN KEY (`rifa_relacionada_id`) REFERENCES `raffles_raffle` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 10: CREAR TABLA DE GANADORES
-- ============================================

CREATE TABLE `raffles_winner` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_sorteo` datetime(6) NOT NULL,
  `verificado` tinyint(1) NOT NULL DEFAULT '0',
  `premio_entregado` tinyint(1) NOT NULL DEFAULT '0',
  `fecha_entrega` datetime(6) DEFAULT NULL,
  `notas` longtext NOT NULL,
  `seed_aleatorio` varchar(64) DEFAULT NULL,
  `timestamp_sorteo` bigint DEFAULT NULL,
  `algoritmo` varchar(50) NOT NULL DEFAULT 'SHA256+Timestamp',
  `hash_verificacion` varchar(64) DEFAULT NULL,
  `participantes_totales` int DEFAULT NULL,
  `acta_digital` longtext,
  `rifa_id` bigint NOT NULL,
  `boleto_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rifa_id` (`rifa_id`),
  UNIQUE KEY `boleto_id` (`boleto_id`),
  CONSTRAINT `raffles_winner_rifa_id_fk` FOREIGN KEY (`rifa_id`) REFERENCES `raffles_raffle` (`id`) ON DELETE CASCADE,
  CONSTRAINT `raffles_winner_boleto_id_fk` FOREIGN KEY (`boleto_id`) REFERENCES `raffles_ticket` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 11: CREAR TABLA DE SOLICITUDES DE PATROCINIO
-- ============================================

CREATE TABLE `raffles_sponsorshiprequest` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_premio_adicional` varchar(200) NOT NULL,
  `descripcion_premio` longtext NOT NULL,
  `valor_premio` decimal(12,2) NOT NULL,
  `imagen_premio` varchar(100) NOT NULL,
  `nombre_marca` varchar(200) NOT NULL,
  `logo_marca` varchar(100) NOT NULL,
  `sitio_web` varchar(200) DEFAULT NULL,
  `mensaje_patrocinio` longtext NOT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'pendiente',
  `fecha_solicitud` datetime(6) NOT NULL,
  `fecha_respuesta` datetime(6) DEFAULT NULL,
  `motivo_rechazo` longtext,
  `rifa_id` bigint NOT NULL,
  `sponsor_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `raffles_sponsorship_rifa_id_fk` (`rifa_id`),
  KEY `raffles_sponsorship_sponsor_id_fk` (`sponsor_id`),
  KEY `raffles_sponsorship_estado_idx` (`estado`),
  CONSTRAINT `raffles_sponsorship_rifa_id_fk` FOREIGN KEY (`rifa_id`) REFERENCES `raffles_raffle` (`id`) ON DELETE CASCADE,
  CONSTRAINT `raffles_sponsorship_sponsor_id_fk` FOREIGN KEY (`sponsor_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 12: CREAR TABLA DE INVITACIONES A SPONSORS
-- ============================================

CREATE TABLE `raffles_organizersponsorrequest` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `mensaje_invitacion` longtext NOT NULL,
  `beneficios_ofrecidos` longtext NOT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'pendiente',
  `fecha_solicitud` datetime(6) NOT NULL,
  `fecha_respuesta` datetime(6) DEFAULT NULL,
  `motivo_rechazo` longtext,
  `propuesta_premio` varchar(200) DEFAULT NULL,
  `propuesta_valor` decimal(12,2) DEFAULT NULL,
  `rifa_id` bigint NOT NULL,
  `sponsor_id` bigint NOT NULL,
  `organizador_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `raffles_orgsponsor_unique` (`rifa_id`, `sponsor_id`),
  KEY `raffles_orgsponsor_sponsor_id_fk` (`sponsor_id`),
  KEY `raffles_orgsponsor_org_id_fk` (`organizador_id`),
  CONSTRAINT `raffles_orgsponsor_rifa_id_fk` FOREIGN KEY (`rifa_id`) REFERENCES `raffles_raffle` (`id`) ON DELETE CASCADE,
  CONSTRAINT `raffles_orgsponsor_sponsor_id_fk` FOREIGN KEY (`sponsor_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `raffles_orgsponsor_org_id_fk` FOREIGN KEY (`organizador_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PASO 13: CREAR TABLAS AUXILIARES DE DJANGO
-- ============================================

CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model` (`app_label`, `model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_codename` (`content_type_id`, `codename`),
  CONSTRAINT `auth_permission_content_type_id_fk` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_permission` (`group_id`, `permission_id`),
  KEY `auth_group_permissions_permission_id_fk` (`permission_id`),
  CONSTRAINT `auth_group_permissions_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE,
  CONSTRAINT `auth_group_permissions_permission_id_fk` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `users_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_groups_user_group` (`user_id`, `group_id`),
  KEY `users_user_groups_group_id_fk` (`group_id`),
  CONSTRAINT `users_user_groups_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `users_user_groups_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `users_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_permissions_user_permission` (`user_id`, `permission_id`),
  KEY `users_user_permissions_permission_id_fk` (`permission_id`),
  CONSTRAINT `users_user_permissions_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `users_user_permissions_permission_id_fk` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_fk` (`content_type_id`),
  KEY `django_admin_log_user_id_fk` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_fk` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE CASCADE,
  CONSTRAINT `django_admin_log_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_idx` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;

-- ============================================
-- ✅ SCRIPT COMPLETADO
-- ============================================
SELECT '✅ Base de datos recreada exitosamente' AS Status;
SELECT 'Ahora ejecuta: python manage.py migrate --fake-initial' AS 'Siguiente Paso';
SELECT 'Luego ejecuta: python manage.py createsuperuser' AS 'Crear Admin';
