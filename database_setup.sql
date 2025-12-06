CREATE DATABASE  IF NOT EXISTS `bookstore_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `bookstore_db`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: bookstore_db
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `book_id` int NOT NULL AUTO_INCREMENT,
  `title` text COLLATE utf8mb4_general_ci NOT NULL,
  `author` text COLLATE utf8mb4_general_ci NOT NULL,
  `price_buy` double NOT NULL,
  `price_rent` double NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`book_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (1,'Harry Potter and The Sorcerer\'s Stone','J.K Rowling',10.98,1,1),(2,'The Hobbit','J.R.R. Tolkien',12.5,2.5,0),(3,'1984','George Orwell',8.75,1.5,1),(4,'Moby Dick','Herman Melville',13.5,2.75,2),(5,'The Hunger Games','Suzanne Collins',10,1.99,0),(6,'To Kill A MockingBird','Harper Lee',9.99,1.75,0),(7,'The Fellowship of the Ring','J.R.R. Tolkien',14.5,2.99,1),(8,'The Lost World','Arthur Conan Doyle',8.99,1.75,9),(9,'The Lost World','Arthur Conan Doyle',8.99,1.75,0),(10,'Forest','Sir Jackass',5.99,10.99,2),(11,'The Great Gatsby','F. Scott Fitzgerald',3.5,1.5,3),(12,'The Great Gatsby','F.Scott Fitzgeral',2,3,0),(13,'To Kill a MockingBird','Harper Lee',9.99,1.75,5),(14,'1984','Herman Melville',10,1,0),(15,'Hatchet','Gary Paulsen',8.99,2.99,5);
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `order_item_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `book_id` int NOT NULL,
  `item_type` text COLLATE utf8mb4_general_ci NOT NULL,
  `unit_price` double NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`order_item_id`),
  KEY `order_items_FK_0_0` (`book_id`),
  KEY `order_items_FK_1_0` (`order_id`),
  CONSTRAINT `order_items_FK_0_0` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`),
  CONSTRAINT `order_items_FK_1_0` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,4,'rent',2.75,1),(2,1,3,'buy',8.75,1),(3,1,5,'rent',1.99,1),(4,2,8,'buy',8.99,1),(5,2,9,'rent',1.75,1),(6,3,4,'buy',13.5,1),(7,4,4,'buy',13.5,1),(8,4,11,'buy',3.5,1),(9,4,6,'rent',1.75,1),(10,5,11,'buy',3.5,1),(11,5,11,'buy',3.5,1),(12,5,11,'rent',1.5,1),(13,6,11,'buy',3.5,1),(14,6,11,'buy',3.5,1),(15,6,12,'rent',3,1),(16,7,11,'buy',3.5,1),(17,8,10,'buy',5.99,1),(18,9,10,'buy',5.99,1),(19,10,4,'buy',13.5,1),(20,10,3,'rent',1.5,1),(21,10,4,'buy',13.5,1),(22,10,14,'buy',10,1),(23,11,4,'rent',2.75,1),(24,12,4,'rent',2.75,1),(25,13,4,'rent',2.75,1),(26,14,10,'buy',5.99,1),(27,15,8,'buy',8.99,1),(28,16,3,'buy',8.75,1),(29,17,10,'buy',5.99,1),(30,18,4,'buy',13.5,1),(31,19,4,'buy',13.5,1),(32,19,4,'buy',13.5,1),(33,19,2,'rent',2.5,1),(34,20,3,'buy',8.75,1),(35,20,3,'buy',8.75,1),(36,20,15,'rent',2.99,1);
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `status` text COLLATE utf8mb4_general_ci NOT NULL DEFAULT (_utf8mb4'Pending'),
  `payed` double NOT NULL DEFAULT '0',
  `created_at` text COLLATE utf8mb4_general_ci NOT NULL DEFAULT (now()),
  PRIMARY KEY (`order_id`),
  KEY `orders_FK_0_0` (`user_id`),
  CONSTRAINT `orders_FK_0_0` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,1,'Returned',1,'2025-11-28 20:09:55'),(2,1,'Pending Rental Payment',0,'2025-11-28 20:20:17'),(3,9,'Paid',1,'2025-11-30 06:49:56'),(4,1,'Pending Rental Payment',0,'2025-12-03 16:53:30'),(5,1,'Pending Rental Payment',0,'2025-12-03 17:24:01'),(6,14,'Returned',1,'2025-12-04 01:50:06'),(7,1,'Paid',1,'2025-12-04 01:51:54'),(8,17,'Paid',1,'2025-12-04 03:44:17'),(9,18,'Paid',1,'2025-12-04 03:45:23'),(10,1,'Pending Rental Payment',1,'2025-12-04 04:13:17'),(11,1,'Pending Rental Payment',0,'2025-12-04 21:24:16'),(12,1,'Pending Rental Payment',0,'2025-12-04 21:32:59'),(13,1,'Pending Rental Payment',0,'2025-12-04 21:38:46'),(14,1,'Paid',1,'2025-12-04 21:43:37'),(15,1,'Paid',1,'2025-12-04 22:12:50'),(16,1,'Paid',1,'2025-12-04 22:18:18'),(17,1,'Paid',1,'2025-12-04 22:19:35'),(18,1,'Paid',1,'2025-12-04 22:30:45'),(19,1,'Pending Rental Payment',0,'2025-12-04 22:37:13'),(20,1,'Pending Rental Payment',0,'2025-12-04 22:42:17');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` text COLLATE utf8mb4_general_ci NOT NULL,
  `password_hash` text COLLATE utf8mb4_general_ci NOT NULL,
  `email` text COLLATE utf8mb4_general_ci NOT NULL,
  `role` text COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `sqlite_autoindex_users_2` (`email`(255))
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Toony','$2b$12$NUFsVuTgL7hOfRMKkhL0lORcd2QoYg7fwidHvdYxm98TPWM54qLTG','toony@tamu.edu','customer'),(2,'Philip','$2b$12$00MLhhazPBQBGwpihxoxtOhukuw3KywcDN/pBi9KhL4B0hynmMDF.','seal@tamu.edu','customer'),(3,'hello','$2b$12$R73YHqze/Gd6lXWAQTd.mOxedJKZz0QMu/8n1Ym5E6aopHOtQ.c9.','asdf@tamu.edu','customer'),(4,'Alex Bob','$2b$12$skMQoyOUYUOvkuGWee65Aub2rA9PfBVHkCaARDNlvg60fLH81aqAi','123@gmail.com','customer'),(5,'1234','$2b$12$6asgDwX0C4O7ijLoNXlEPOK9gtfu1G2uJzzcatCSdPRIPtPSh18JO','1234','customer'),(6,'avibansal','$2b$12$K/5cbaHTol74mKT2E5zfSOMwkisiLU7Z8jeSEPzkocx9NGOAooNBG','avi_bansal@tamu.edu','customer'),(7,'toony','$2b$12$ShYMKazlXn9yLFxyanAKHOz0j6.nM9Dfiounu9iMRwjwCsYevnHNi','toonphilp12@gmail.com','manager'),(8,'ballsofsteel','$2b$12$ptFxC1WqXk6kQAZdSwgf..7VnjFKiGFT1UpY2m5d4w4nMnlFrru6e','jkd','customer'),(9,'penispuncher32','$2b$12$XUHs5u7lPrXr1C02sUmlcuI9U8UQlYPvOtblkGuH1xpfsrhyRDnG2','asdf123@gmail.com','customer'),(10,'testaccount','$2b$12$.mEPh8gNZjuyQJEb09Zpt.epMzc3B8Ksf96O3MlUioSR5pTL38NQu','testaccount@tamu.edu','customer'),(11,'testing','$2b$12$Pm6RqYVkfgLkrKblA1yJ1ewYZymE5ZjvYJ7zmgXOhU5D1DOvUxQW6','testing@gmail.com','customer'),(12,'test','$2b$12$e95uMkRE7eM7pL/00/hkdOle7RQpiFoEPgcr0BzgduOYNXH8lO9ue','test1234@gmail.com','customer'),(13,'1','$2b$12$hAb6tB2tdbAvglatYiyieOK9Iw70rivZ/q0aeQjhe9QLizhwg/2HO','1@gmail.com','customer'),(14,'2','$2b$12$DYX9brxaHkwaLvtAX9QfzOr5PRhGa0P2kLFD0pvms2Nm0Q/bbJium','2@gmail.com','customer'),(15,'3','$2b$12$ILEmDi1/sD.hy2/mGsTR/O3nWL0Qu8RE5S5pModPrTYQRCk4ZW9eG','3@gmail.com','customer'),(16,'4','$2b$12$.heEPsci4MxjdQkMX7u5eO7BW4WipJI48WU/IQkUZgGaqJEGDoIhy','4@gmail.com','customer'),(17,'5','$2b$12$WW9sgbXoPPIiCK8xowKfJ.FIkudoUM5zxhjXyF7ycFvTdylWIxt7W','5@gmail.com','customer'),(18,'Toony1','$2b$12$hQQAhZdZE5SPnyq0OwEOaewUvkTa1UUsFvEoABFGC64l66so8kmJm','toonphilp@gmail.com','customer');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-05 18:57:49
