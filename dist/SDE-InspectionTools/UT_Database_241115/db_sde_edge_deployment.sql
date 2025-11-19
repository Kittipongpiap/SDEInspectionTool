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
-- Table structure for table `edge_deployment`
--

DROP TABLE IF EXISTS `edge_deployment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `edge_deployment` (
  `port_no` int NOT NULL COMMENT 'show working  port status.',
  `ip_address` varchar(15) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `edge_id` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `edgetype_id` int NOT NULL,
  `package_id` int NOT NULL,
  `thinggroup_id` int NOT NULL,
  `tuyauniq_id` int DEFAULT NULL,
  `note_id` int NOT NULL,
  `label_print` char(1) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `thinggroup_add` char(1) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `status` char(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `developer_id` int NOT NULL,
  `project_id` int NOT NULL,
  `business_unit_id` int NOT NULL,
  `datetime_start` datetime NOT NULL,
  `datetime_end` datetime DEFAULT NULL,
  `add_thinggroup_failed` int DEFAULT '0',
  PRIMARY KEY (`edge_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `edge_deployment`
--

LOCK TABLES `edge_deployment` WRITE;
/*!40000 ALTER TABLE `edge_deployment` DISABLE KEYS */;
INSERT INTO `edge_deployment` VALUES (6,'192.168.106.2','c4-3c-b0-ce-44-9c',2,2,22,0,1112,'1','1','SUCCEEDED',5,3,2,'2024-11-13 14:09:27','2024-11-13 14:52:31',0),(2,'192.168.102.2','c4-3c-b0-ce-44-e2',2,2,22,0,1108,'1','1','SUCCEEDED',5,3,2,'2024-11-13 14:07:37','2024-11-13 15:01:48',0),(3,'192.168.103.2','c4-3c-b0-ce-f1-d4',2,2,22,0,1109,'1','1','SUCCEEDED',5,3,2,'2024-11-13 14:08:05','2024-11-13 14:48:10',0),(4,'192.168.104.2','c4-3c-b0-e7-ff-cb',2,2,22,0,1110,'1','1','SUCCEEDED',5,3,2,'2024-11-13 14:08:32','2024-11-13 14:48:11',0),(5,'192.168.105.2','c4-3c-b0-e9-11-98',2,2,22,0,1111,'1','1','SUCCEEDED',5,3,2,'2024-11-13 14:09:00','2024-11-13 14:28:49',0),(1,'192.168.101.2','c4-3c-b0-e9-19-50',2,2,22,0,1107,'1','1','SUCCEEDED',5,3,2,'2024-11-13 14:07:07','2024-11-13 14:49:15',0);
/*!40000 ALTER TABLE `edge_deployment` ENABLE KEYS */;
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
