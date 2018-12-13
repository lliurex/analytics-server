SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

CREATE DATABASE IF NOT EXISTS `analytics` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `analytics`;

CREATE TABLE IF NOT EXISTS `alias` (
  `name` varchar(50) NOT NULL,
  `alias` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `clients` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `user` varchar(18) NOT NULL,
  `lastlogin` datetime NOT NULL,
  `version` char(20) NOT NULL,
  `sabor` char(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_version_sabor_4_update` (`user`,`version`,`sabor`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `historico` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(150) NOT NULL,
  `count` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `version` char(20) NOT NULL,
  `sabor` char(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fecha` (`fecha`),
  KEY `version_sabor` (`version`,`sabor`),
  KEY `app` (`app`),
  KEY `sabor` (`sabor`),
  KEY `version` (`version`),
  KEY `app_count` (`app`,`count`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `historico_clients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `version` char(20) NOT NULL,
  `sabor` char(50) NOT NULL,
  `fecha` date NOT NULL,
  `nclients` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `packages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(150) NOT NULL,
  `count` int(10) NOT NULL,
  `version` char(20) NOT NULL,
  `sabor` char(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_app_version_sabor_4_update` (`app`,`version`,`sabor`),
  KEY `app` (`app`),
  KEY `version_sabor` (`version`,`sabor`),
  KEY `sabor` (`sabor`),
  KEY `version` (`version`),
  KEY `app_count` (`app`,`count`),
  KEY `app_version_sabor` (`app`,`version`,`sabor`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
