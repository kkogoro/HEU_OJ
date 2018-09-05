-- MySQL dump 10.13  Distrib 5.7.19, for Linux (x86_64)
--
-- Host: localhost    Database: online_judge2
-- ------------------------------------------------------
-- Server version	5.7.19

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `online_judge2`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `online_judge2` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;

USE `online_judge2`;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blog`
--

DROP TABLE IF EXISTS `blog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8_unicode_ci,
  `author_username` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `public` tinyint(1) DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_username` (`author_username`),
  CONSTRAINT `blog_ibfk_1` FOREIGN KEY (`author_username`) REFERENCES `users` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blog_comment`
--

DROP TABLE IF EXISTS `blog_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blog_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` text COLLATE utf8_unicode_ci,
  `author_username` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `blog_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_username` (`author_username`),
  KEY `blog_id` (`blog_id`),
  KEY `ix_blog_comment_time` (`time`),
  CONSTRAINT `blog_comment_ibfk_1` FOREIGN KEY (`author_username`) REFERENCES `users` (`username`),
  CONSTRAINT `blog_comment_ibfk_2` FOREIGN KEY (`blog_id`) REFERENCES `blog` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `challenge`
--

DROP TABLE IF EXISTS `challenge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `challenge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `challenge_name` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `challenge_level` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `challenge_round`
--

DROP TABLE IF EXISTS `challenge_round`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `challenge_round` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `round_name` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `challenge_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `challenge_id` (`challenge_id`),
  CONSTRAINT `challenge_round_ibfk_1` FOREIGN KEY (`challenge_id`) REFERENCES `challenge` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `challenge_round_problem`
--

DROP TABLE IF EXISTS `challenge_round_problem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `challenge_round_problem` (
  `problem_id` int(11) NOT NULL,
  `round_id` int(11) NOT NULL,
  `problem_index` int(11) DEFAULT NULL,
  `problem_alias` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`problem_id`,`round_id`),
  KEY `round_id` (`round_id`),
  CONSTRAINT `challenge_round_problem_ibfk_1` FOREIGN KEY (`problem_id`) REFERENCES `problems` (`id`),
  CONSTRAINT `challenge_round_problem_ibfk_2` FOREIGN KEY (`round_id`) REFERENCES `challenge_round` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `challenge_user_level`
--

DROP TABLE IF EXISTS `challenge_user_level`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `challenge_user_level` (
  `user_id` int(11) NOT NULL,
  `challenge_id` int(11) NOT NULL,
  `round_pass` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`,`challenge_id`),
  KEY `challenge_id` (`challenge_id`),
  CONSTRAINT `challenge_user_level_ibfk_1` FOREIGN KEY (`challenge_id`) REFERENCES `challenge` (`id`),
  CONSTRAINT `challenge_user_level_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `compile_info`
--

DROP TABLE IF EXISTS `compile_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `compile_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `submission_id` int(11) DEFAULT NULL,
  `info` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `submission_id` (`submission_id`),
  CONSTRAINT `compile_info_ibfk_1` FOREIGN KEY (`submission_id`) REFERENCES `submission_status` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2519 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `config`
--

DROP TABLE IF EXISTS `config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `config` (
  `key` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `value` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `contest_problem`
--

DROP TABLE IF EXISTS `contest_problem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contest_problem` (
  `problem_id` int(11) NOT NULL,
  `contest_id` int(11) NOT NULL,
  `problem_index` int(11) DEFAULT NULL,
  `problem_alias` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`problem_id`,`contest_id`),
  KEY `contest_id` (`contest_id`),
  CONSTRAINT `contest_problem_ibfk_1` FOREIGN KEY (`contest_id`) REFERENCES `contests` (`id`),
  CONSTRAINT `contest_problem_ibfk_2` FOREIGN KEY (`problem_id`) REFERENCES `problems` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `contest_user`
--

DROP TABLE IF EXISTS `contest_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contest_user` (
  `user_id` int(11) NOT NULL,
  `contest_id` int(11) NOT NULL,
  `realname` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `address` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `school_id` int(11) DEFAULT NULL,
  `student_num` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `phone_num` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `user_confirmed` tinyint(1) DEFAULT NULL,
  `register_time` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`,`contest_id`),
  KEY `contest_id` (`contest_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `contest_user_ibfk_1` FOREIGN KEY (`contest_id`) REFERENCES `contests` (`id`),
  CONSTRAINT `contest_user_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `school_list` (`id`),
  CONSTRAINT `contest_user_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `contests`
--

DROP TABLE IF EXISTS `contests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contest_name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `school_id` int(11) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `verify` tinyint(1) DEFAULT NULL,
  `password` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `style` int(11) DEFAULT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `announce` text COLLATE utf8_unicode_ci,
  `notification` text COLLATE utf8_unicode_ci,
  `manager_username` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `visible` tinyint(1) DEFAULT NULL,
  `rank_frozen` tinyint(1) DEFAULT NULL,
  `last_generate_rank` datetime DEFAULT NULL,
  `type` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `manager_username` (`manager_username`),
  KEY `school_id` (`school_id`),
  KEY `ix_contests_contest_name` (`contest_name`),
  CONSTRAINT `contests_ibfk_1` FOREIGN KEY (`manager_username`) REFERENCES `users` (`username`),
  CONSTRAINT `contests_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `school_list` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `follows`
--

DROP TABLE IF EXISTS `follows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `follows` (
  `follower_id` int(11) NOT NULL,
  `followed_id` int(11) NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`follower_id`,`followed_id`),
  KEY `followed_id` (`followed_id`),
  CONSTRAINT `follows_ibfk_1` FOREIGN KEY (`followed_id`) REFERENCES `users` (`id`),
  CONSTRAINT `follows_ibfk_2` FOREIGN KEY (`follower_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `logs`
--

DROP TABLE IF EXISTS `logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `operator_name` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `operation` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `operator_name` (`operator_name`),
  CONSTRAINT `logs_ibfk_1` FOREIGN KEY (`operator_name`) REFERENCES `users` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=485 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oicontest`
--

DROP TABLE IF EXISTS `oicontest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oicontest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contest_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `problem_id` int(11) DEFAULT NULL,
  `language` int(11) DEFAULT NULL,
  `code` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `contest_id` (`contest_id`),
  KEY `problem_id` (`problem_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `oicontest_ibfk_1` FOREIGN KEY (`contest_id`) REFERENCES `contests` (`id`),
  CONSTRAINT `oicontest_ibfk_2` FOREIGN KEY (`problem_id`) REFERENCES `problems` (`id`),
  CONSTRAINT `oicontest_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `contest_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `problems`
--

DROP TABLE IF EXISTS `problems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `problems` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `school_id` int(11) DEFAULT NULL,
  `title` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time_limit` int(11) DEFAULT NULL,
  `memory_limit` int(11) DEFAULT NULL,
  `special_judge` tinyint(1) DEFAULT NULL,
  `type` tinyint(1) DEFAULT NULL,
  `submission_num` int(11) DEFAULT NULL,
  `accept_num` int(11) DEFAULT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `input` text COLLATE utf8_unicode_ci,
  `output` text COLLATE utf8_unicode_ci,
  `sample_input` text COLLATE utf8_unicode_ci,
  `sample_output` text COLLATE utf8_unicode_ci,
  `source_name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `hint` text COLLATE utf8_unicode_ci,
  `author` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `visible` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `school_id` (`school_id`),
  KEY `ix_problems_title` (`title`),
  CONSTRAINT `problems_ibfk_1` FOREIGN KEY (`school_id`) REFERENCES `school_list` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `default` tinyint(1) DEFAULT NULL,
  `permission` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_roles_default` (`default`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `round_user_level`
--

DROP TABLE IF EXISTS `round_user_level`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `round_user_level` (
  `user_id` int(11) NOT NULL,
  `round_id` int(11) NOT NULL,
  `problem_pass` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`,`round_id`),
  KEY `round_id` (`round_id`),
  CONSTRAINT `round_user_level_ibfk_1` FOREIGN KEY (`round_id`) REFERENCES `challenge_round` (`id`),
  CONSTRAINT `round_user_level_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `school_list`
--

DROP TABLE IF EXISTS `school_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `school_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `school_name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `submission_status`
--

DROP TABLE IF EXISTS `submission_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `submission_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `submit_time` datetime DEFAULT NULL,
  `problem_id` int(11) DEFAULT NULL,
  `status` float DEFAULT NULL,
  `exec_time` int(11) DEFAULT NULL,
  `exec_memory` int(11) DEFAULT NULL,
  `code_length` int(11) DEFAULT NULL,
  `language` int(11) DEFAULT NULL,
  `code` text COLLATE utf8_unicode_ci,
  `author_username` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `visible` tinyint(1) DEFAULT NULL,
  `contest_id` int(11) DEFAULT NULL,
  `challenge_id` int(11) DEFAULT NULL,
  `balloon_sent` tinyint(1) DEFAULT NULL,
  `submit_ip` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `child_status` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `author_username` (`author_username`),
  KEY `challenge_id` (`challenge_id`),
  KEY `contest_id` (`contest_id`),
  KEY `problem_id` (`problem_id`),
  KEY `ix_submission_status_status` (`status`),
  CONSTRAINT `submission_status_ibfk_1` FOREIGN KEY (`author_username`) REFERENCES `users` (`username`),
  CONSTRAINT `submission_status_ibfk_2` FOREIGN KEY (`challenge_id`) REFERENCES `challenge_round` (`id`),
  CONSTRAINT `submission_status_ibfk_3` FOREIGN KEY (`contest_id`) REFERENCES `contests` (`id`),
  CONSTRAINT `submission_status_ibfk_4` FOREIGN KEY (`problem_id`) REFERENCES `problems` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2596 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tag_problem`
--

DROP TABLE IF EXISTS `tag_problem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tag_problem` (
  `tag_id` int(11) NOT NULL,
  `problem_id` int(11) NOT NULL,
  PRIMARY KEY (`tag_id`,`problem_id`),
  KEY `problem_id` (`problem_id`),
  CONSTRAINT `tag_problem_ibfk_1` FOREIGN KEY (`problem_id`) REFERENCES `problems` (`id`),
  CONSTRAINT `tag_problem_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag_name` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag_name` (`tag_name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `topic`
--

DROP TABLE IF EXISTS `topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `topic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8_unicode_ci,
  `author_username` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `public` tinyint(1) DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `contest_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_username` (`author_username`),
  KEY `contest_id` (`contest_id`),
  CONSTRAINT `topic_ibfk_1` FOREIGN KEY (`author_username`) REFERENCES `users` (`username`),
  CONSTRAINT `topic_ibfk_2` FOREIGN KEY (`contest_id`) REFERENCES `contests` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `topic_comment`
--

DROP TABLE IF EXISTS `topic_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `topic_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` text COLLATE utf8_unicode_ci,
  `author_username` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `topic_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_username` (`author_username`),
  KEY `topic_id` (`topic_id`),
  CONSTRAINT `topic_comment_ibfk_1` FOREIGN KEY (`author_username`) REFERENCES `users` (`username`),
  CONSTRAINT `topic_comment_ibfk_2` FOREIGN KEY (`topic_id`) REFERENCES `topic` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `username` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `nickname` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `realname` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  `password_hash` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  `gender` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `major` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `degree` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `country` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `address` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `school_id` int(11) DEFAULT NULL,
  `student_num` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `phone_num` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `about_me` text COLLATE utf8_unicode_ci,
  `member_since` datetime DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `rating` int(11) DEFAULT NULL,
  `photo` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `current_level` int(11) DEFAULT NULL,
  `info_protection` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `role_id` (`role_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `school_list` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-07-30 18:46:09
