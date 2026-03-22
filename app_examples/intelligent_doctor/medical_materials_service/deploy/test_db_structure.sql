-- MySQL dump 10.13  Distrib 8.0.43, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: test
-- ------------------------------------------------------
-- Server version	8.0.11-TiDB-v8.5.3

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
-- Table structure for table `check_files`
--

DROP TABLE IF EXISTS `check_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `check_files` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `image_check_id` char(36) NOT NULL,
  `filename` varchar(200) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `file_size` bigint DEFAULT NULL,
  `file_md5sum` varchar(128) NOT NULL,
  `storage_path` varchar(500) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `upload_time` datetime(3) NOT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_check_files_deleted_at` (`deleted_at`),
  KEY `fk_image_checks_check_files` (`image_check_id`),
  CONSTRAINT `fk_image_checks_check_files` FOREIGN KEY (`image_check_id`) REFERENCES `image_checks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `diagnoses`
--

DROP TABLE IF EXISTS `diagnoses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnoses` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `visit_id` char(36) NOT NULL,
  `disease_name` varchar(100) NOT NULL,
  `is_main` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_diagnoses_deleted_at` (`deleted_at`),
  KEY `fk_visits_diagnoses` (`visit_id`),
  CONSTRAINT `fk_visits_diagnoses` FOREIGN KEY (`visit_id`) REFERENCES `visits` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `image_checks`
--

DROP TABLE IF EXISTS `image_checks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `image_checks` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `visit_check_id` char(36) NOT NULL,
  `conclusion` text DEFAULT NULL,
  `interpreter` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_image_checks_deleted_at` (`deleted_at`),
  UNIQUE KEY `idx_image_checks_visit_check_id` (`visit_check_id`),
  CONSTRAINT `fk_visit_checks_image_check` FOREIGN KEY (`visit_check_id`) REFERENCES `visit_checks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patients` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `user_id` char(36) NOT NULL,
  `medical_record_no` varchar(36) NOT NULL,
  `name` varchar(50) NOT NULL,
  `gender` varchar(2) DEFAULT NULL,
  `birthday` datetime(3) DEFAULT NULL,
  `id_card` varchar(18) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `allergy_history` text DEFAULT NULL,
  `medical_history` text DEFAULT NULL,
  `emergency_contact` varchar(50) DEFAULT NULL,
  `emergency_phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_patients_deleted_at` (`deleted_at`),
  UNIQUE KEY `idx_patients_user_id` (`user_id`),
  UNIQUE KEY `idx_patients_medical_record_no` (`medical_record_no`),
  UNIQUE KEY `idx_patients_id_card` (`id_card`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prescription_drugs`
--

DROP TABLE IF EXISTS `prescription_drugs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prescription_drugs` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `prescription_id` char(36) NOT NULL,
  `drug_name` varchar(100) NOT NULL,
  `specification` varchar(50) DEFAULT NULL,
  `dosage` varchar(20) DEFAULT NULL,
  `frequency` varchar(20) DEFAULT NULL,
  `course` varchar(20) DEFAULT NULL,
  `total_quantity` bigint NOT NULL,
  `administration` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_prescription_drugs_deleted_at` (`deleted_at`),
  KEY `fk_prescriptions_drug_items` (`prescription_id`),
  CONSTRAINT `fk_prescriptions_drug_items` FOREIGN KEY (`prescription_id`) REFERENCES `prescriptions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prescriptions`
--

DROP TABLE IF EXISTS `prescriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prescriptions` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `visit_id` char(36) NOT NULL,
  `prescribe_time` datetime(3) NOT NULL,
  `drug_type` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_prescriptions_deleted_at` (`deleted_at`),
  KEY `fk_visits_prescriptions` (`visit_id`),
  CONSTRAINT `fk_visits_prescriptions` FOREIGN KEY (`visit_id`) REFERENCES `visits` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `routine_check_items`
--

DROP TABLE IF EXISTS `routine_check_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `routine_check_items` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `routine_check_id` char(36) NOT NULL,
  `indicator_code` varchar(30) NOT NULL,
  `indicator_name` varchar(50) NOT NULL,
  `value` varchar(50) NOT NULL,
  `reference_range` varchar(50) DEFAULT NULL,
  `abnormal_flag` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_routine_check_items_deleted_at` (`deleted_at`),
  KEY `fk_routine_checks_items` (`routine_check_id`),
  CONSTRAINT `fk_routine_checks_items` FOREIGN KEY (`routine_check_id`) REFERENCES `routine_checks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `routine_checks`
--

DROP TABLE IF EXISTS `routine_checks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `routine_checks` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `visit_check_id` char(36) NOT NULL,
  `conclusion` text DEFAULT NULL,
  `interpreter` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_routine_checks_deleted_at` (`deleted_at`),
  UNIQUE KEY `idx_routine_checks_visit_check_id` (`visit_check_id`),
  CONSTRAINT `fk_visit_checks_routine_check` FOREIGN KEY (`visit_check_id`) REFERENCES `visit_checks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visit_checks`
--

DROP TABLE IF EXISTS `visit_checks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `visit_checks` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `visit_id` char(36) NOT NULL,
  `check_type` varchar(10) NOT NULL,
  `apply_time` datetime(3) NOT NULL,
  `apply_doctor` varchar(50) DEFAULT NULL,
  `check_time` datetime(3) NOT NULL,
  `report_time` datetime(3) NOT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_visit_checks_deleted_at` (`deleted_at`),
  KEY `fk_visits_visit_checks` (`visit_id`),
  CONSTRAINT `fk_visits_visit_checks` FOREIGN KEY (`visit_id`) REFERENCES `visits` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visits`
--

DROP TABLE IF EXISTS `visits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `visits` (
  `id` char(36) NOT NULL,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `patient_id` char(36) NOT NULL,
  `hospital` char(50) NOT NULL,
  `visit_type` varchar(20) NOT NULL,
  `department` varchar(50) NOT NULL,
  `doctor_id` char(36) DEFAULT NULL,
  `visit_time` datetime(3) NOT NULL,
  `chief_complaint` text NOT NULL,
  `present_illness` text DEFAULT NULL,
  `auxiliary_exam` text DEFAULT NULL,
  `treatment_plan` text DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `idx_visits_deleted_at` (`deleted_at`),
  KEY `fk_patients_vistits` (`patient_id`),
  CONSTRAINT `fk_patients_vistits` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-04 18:57:28
