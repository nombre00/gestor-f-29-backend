-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: gestorf29
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id` int NOT NULL AUTO_INCREMENT,
  `empresa_id` int NOT NULL,
  `asignado_a_usuario_id` int NOT NULL,
  `rut` varchar(12) NOT NULL,
  `razon_social` varchar(255) NOT NULL,
  `nombre_comercial` varchar(255) DEFAULT NULL,
  `giro` varchar(255) DEFAULT NULL,
  `actividad_economica` varchar(255) DEFAULT NULL,
  `direccion` varchar(500) DEFAULT NULL,
  `comuna` varchar(100) DEFAULT NULL,
  `ciudad` varchar(100) DEFAULT NULL,
  `contacto_nombre` varchar(255) DEFAULT NULL,
  `contacto_email` varchar(255) DEFAULT NULL,
  `contacto_telefono` varchar(20) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_rut_empresa` (`empresa_id`,`rut`),
  KEY `ix_cliente_rut` (`rut`),
  KEY `ix_cliente_asignado_a_usuario_id` (`asignado_a_usuario_id`),
  KEY `ix_cliente_empresa_id` (`empresa_id`),
  KEY `idx_empresa_activo` (`empresa_id`,`activo`),
  CONSTRAINT `cliente_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cliente_ibfk_2` FOREIGN KEY (`asignado_a_usuario_id`) REFERENCES `usuario` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empresa`
--

DROP TABLE IF EXISTS `empresa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empresa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rut` varchar(12) NOT NULL,
  `razon_social` varchar(255) NOT NULL,
  `nombre_comercial` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `activa` tinyint(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_empresa_rut` (`rut`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empresa`
--

LOCK TABLES `empresa` WRITE;
/*!40000 ALTER TABLE `empresa` DISABLE KEYS */;
INSERT INTO `empresa` VALUES (1,'76.074.027-6','Viña Center LTDA','Viña Center LTDA','contabilidadjpg56@gmail.com','+56998409235',1,'2026-03-03 20:49:44','2026-03-03 20:49:44');
/*!40000 ALTER TABLE `empresa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invitacion`
--

DROP TABLE IF EXISTS `invitacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invitacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `empresa_id` int NOT NULL,
  `email` varchar(255) NOT NULL,
  `token` varchar(255) NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `apellido` varchar(255) DEFAULT NULL,
  `rol` varchar(50) NOT NULL,
  `invitado_por_usuario_id` int DEFAULT NULL,
  `usado` tinyint(1) NOT NULL,
  `expires_at` timestamp NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_invitacion_token` (`token`),
  KEY `invitado_por_usuario_id` (`invitado_por_usuario_id`),
  KEY `ix_invitacion_empresa_id` (`empresa_id`),
  KEY `ix_invitacion_email` (`email`),
  CONSTRAINT `invitacion_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE,
  CONSTRAINT `invitacion_ibfk_2` FOREIGN KEY (`invitado_por_usuario_id`) REFERENCES `usuario` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invitacion`
--

LOCK TABLES `invitacion` WRITE;
/*!40000 ALTER TABLE `invitacion` DISABLE KEYS */;
INSERT INTO `invitacion` VALUES (1,1,'leo.salgado@duocuc.cl','ODATSCNwTiD5xQEzHD0KQHgagxqZQ8qXxbo6lxKHg1g','leo','salgado','admin',1,1,'2026-03-10 20:50:56','2026-03-03 20:50:55','2026-03-03 20:51:30');
/*!40000 ALTER TABLE `invitacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resumen_anual`
--

DROP TABLE IF EXISTS `resumen_anual`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resumen_anual` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int NOT NULL,
  `año` varchar(4) NOT NULL,
  `estado` enum('BORRADOR','REVISADO') NOT NULL,
  `creado_por_usuario_id` int NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `periodos_incluidos_json` json DEFAULT NULL,
  `detalles_json` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_cliente_año` (`cliente_id`,`año`),
  KEY `creado_por_usuario_id` (`creado_por_usuario_id`),
  KEY `ix_resumen_anual_cliente_id` (`cliente_id`),
  KEY `ix_resumen_anual_año` (`año`),
  CONSTRAINT `resumen_anual_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`id`) ON DELETE CASCADE,
  CONSTRAINT `resumen_anual_ibfk_2` FOREIGN KEY (`creado_por_usuario_id`) REFERENCES `usuario` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resumen_anual`
--

LOCK TABLES `resumen_anual` WRITE;
/*!40000 ALTER TABLE `resumen_anual` DISABLE KEYS */;
/*!40000 ALTER TABLE `resumen_anual` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resumen_f29`
--

DROP TABLE IF EXISTS `resumen_f29`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resumen_f29` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int NOT NULL,
  `periodo` varchar(7) NOT NULL,
  `debito_fiscal` decimal(15,2) DEFAULT NULL,
  `credito_fiscal` decimal(15,2) DEFAULT NULL,
  `remanente_mes_anterior` decimal(15,2) DEFAULT NULL,
  `iva_a_pagar` decimal(15,2) DEFAULT NULL,
  `remanente` decimal(15,2) DEFAULT NULL,
  `total_ventas_netas` decimal(15,2) DEFAULT NULL,
  `total_compras_netas` decimal(15,2) DEFAULT NULL,
  `total_iva_ventas` decimal(15,2) DEFAULT NULL,
  `total_iva_compras` decimal(15,2) DEFAULT NULL,
  `total_retenciones` decimal(15,2) DEFAULT NULL,
  `ppm` decimal(15,2) DEFAULT NULL,
  `total_a_pagar` decimal(15,2) DEFAULT NULL,
  `estado` enum('BORRADOR','REVISADO') NOT NULL,
  `creado_por_usuario_id` int NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `detalles_json` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_cliente_periodo` (`cliente_id`,`periodo`),
  KEY `creado_por_usuario_id` (`creado_por_usuario_id`),
  KEY `ix_resumen_f29_periodo` (`periodo`),
  KEY `ix_resumen_f29_cliente_id` (`cliente_id`),
  CONSTRAINT `resumen_f29_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`id`) ON DELETE CASCADE,
  CONSTRAINT `resumen_f29_ibfk_2` FOREIGN KEY (`creado_por_usuario_id`) REFERENCES `usuario` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resumen_f29`
--

LOCK TABLES `resumen_f29` WRITE;
/*!40000 ALTER TABLE `resumen_f29` DISABLE KEYS */;
/*!40000 ALTER TABLE `resumen_f29` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `empresa_id` int NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `apellido` varchar(255) DEFAULT NULL,
  `rol` enum('SUPER','ADMIN','CONTADOR') NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `ultimo_acceso` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_usuario_empresa_id` (`empresa_id`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresa` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,1,'admin@ejemplo.cl','$2b$12$qGe3DSNwvrAhv1p5OwwPP.2B6Qhb3YmEnVMv2rpCxYaQ0luVRHyb2','admin','admin','ADMIN',0,'2026-03-03 20:50:23','2026-03-03 20:49:44','2026-03-03 20:51:49'),(2,1,'leo.salgado@duocuc.cl','$2b$12$jm49FCEV/NTJHzOR3tkjfuyqXHDr0AkVU8rs6j8xgUj6FRky2d9Xq','leo','salgado','ADMIN',1,'2026-03-03 20:51:42','2026-03-03 20:51:30','2026-03-03 20:51:42');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'gestorf29'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-03 21:02:31
