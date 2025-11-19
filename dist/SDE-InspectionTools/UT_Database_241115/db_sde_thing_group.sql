-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: 172.16.0.227    Database: db_sde
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `thing_group`
--

DROP TABLE IF EXISTS `thing_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `thing_group` (
  `thinggroup_id` int NOT NULL AUTO_INCREMENT,
  `thinggroup_name` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `thing_group_type` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`thinggroup_id`)
) ENGINE=InnoDB AUTO_INCREMENT=125 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `thing_group`
--

LOCK TABLES `thing_group` WRITE;
/*!40000 ALTER TABLE `thing_group` DISABLE KEYS */;
INSERT INTO `thing_group` VALUES (1,'SC_Asset_AAQ_BPI','prod','2023-08-19 08:26:41'),(2,'Noble_AAQ_Smart_Display_BPI','staging','2023-08-19 08:27:36'),(3,'SC_Asset_AAF_Granada','dev','2023-08-19 08:29:45'),(4,'SC_Asset_AAQ','staging','2023-08-19 08:30:01'),(5,'Noble_AAQ_Smart_Display_BPI_eMMC','prod','2023-08-19 08:30:15'),(7,'AAQ_TUYA_BPI_eMMC','prod','2024-06-05 13:14:00'),(9,'solar_uno_replacement_test','prod','2024-08-08 12:59:00'),(11,'MIND_B2C','prod','2023-02-14 09:36:00'),(12,'AAQ_TUYA','prod','2023-01-22 14:36:00'),(13,'SolAAFQv2','prod','2024-04-26 11:32:00'),(15,'AAQ_RPI','prod','2024-08-22 04:37:00'),(16,'AAQ_SMART_DISPLAY_RPI','prod','2024-06-11 09:40:00'),(17,'SC_Asset_AAQ_BPI_eMMC','prod','2023-08-19 08:30:54'),(19,'AP_Second_Lot','prod','2024-02-14 16:00:00'),(20,'Noble_AAQ_Smart_Display','prod','2024-03-15 15:30:00'),(22,'AAQ_BPI_eMMC','prod','2024-06-11 09:40:00'),(23,'AAQ_SMART_DISPLAY_BPI_eMMC','prod','2024-06-11 09:40:00'),(25,'TUYA_BPI','prod','2024-06-11 09:40:00'),(26,'AAQ_TUYA_SMART_DISPLAY_BPI_eMMC','prod','2024-06-11 09:40:00');
/*!40000 ALTER TABLE `thing_group` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-15 11:12:15
