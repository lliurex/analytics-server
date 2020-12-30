SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";
CREATE DATABASE IF NOT EXISTS `analytics` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `analytics`;

DROP TABLE IF EXISTS `Alias`;
CREATE TABLE IF NOT EXISTS `Alias` (
  `name` varchar(45) NOT NULL,
  `alias` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `Client_Versions`;
CREATE TABLE IF NOT EXISTS `Client_Versions` (
  `uuid` bigint(20) unsigned NOT NULL,
  `Client_uid` varchar(18) NOT NULL,
  `Releases_name` varchar(45) NOT NULL,
  `Flavours_name` varchar(45) NOT NULL,
  `date` date NOT NULL,
  `string_release` varchar(45) NOT NULL,
  `string_flavour` varchar(100) NOT NULL,
  `arch` VARCHAR(10) NULL DEFAULT NULL,
  `mem` INT UNSIGNED NULL DEFAULT NULL,
  `vga` VARCHAR(80) NULL DEFAULT NULL,
  `cpu` VARCHAR(80) NULL DEFAULT NULL,
  `ncpu` TINYINT UNSIGNED NULL DEFAULT NULL,
  `ltsp` BOOLEAN NULL DEFAULT NULL,
  `mode` CHAR(4) NULL DEFAULT NULL,
  PRIMARY KEY (`uuid`),
  KEY `fk_Client_Versions_Releases1_idx` (`Releases_name`),
  KEY `fk_Client_Versions_Flavours1_idx` (`Flavours_name`),
  KEY `get_clients` (`date`,`Releases_name`,`Flavours_name`,`Client_uid`),
  KEY `get_clients_other` (`date`,`Flavours_name`,`Client_uid`),
  KEY `ltsp_mode` (`ltsp`, `mode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `Config`;
CREATE TABLE IF NOT EXISTS `Config` (
  `name` varchar(20) NOT NULL,
  `value` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `Flavours`;
CREATE TABLE IF NOT EXISTS `Flavours` (
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `PackagesWhitelist`;
CREATE TABLE IF NOT EXISTS `PackagesWhitelist` (
  `name` varchar(45) NOT NULL,
  `status` BOOLEAN NULL DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `RecvPackages`;
CREATE TABLE IF NOT EXISTS `RecvPackages` (
  `uuid` bigint(20) unsigned NOT NULL,
  `string` varchar(45) NOT NULL,
  `date` date NOT NULL,
  `Releases_name` varchar(45) NOT NULL,
  `Flavours_name` varchar(45) NOT NULL,
  `count` int(10) unsigned NOT NULL,
  PRIMARY KEY (`uuid`),
  KEY `fk_RecvPackages_Releases1_idx` (`Releases_name`),
  KEY `fk_RecvPackages_Flavours1_idx` (`Flavours_name`),
  KEY `get_top_apps` (`date`,`Releases_name`,`Flavours_name`,`count`,`string`),
  KEY `get_top_apps_others` (`date`,`Flavours_name`,`count`,`string`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `Releases`;
CREATE TABLE IF NOT EXISTS `Releases` (
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- DROP TABLE IF EXISTS `tmp_clients`;
-- CREATE TABLE IF NOT EXISTS `tmp_clients` (
--   `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
--   `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
--   `user` char(18) DEFAULT NULL,
--   `version` varchar(96) DEFAULT NULL,
--   `sabor` varchar(96) DEFAULT NULL,
--   `status` tinyint(1) NOT NULL,
--   PRIMARY KEY (`id`,`status`)
-- ) ENGINE=MEMORY  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- DROP TABLE IF EXISTS `tmp_packages`;
-- CREATE TABLE IF NOT EXISTS `tmp_packages` (
--   `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
--   `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
--   `client` int(11) NOT NULL,
--   `app` varchar(45) NOT NULL,
--   `value` mediumint(8) unsigned NOT NULL,
--   PRIMARY KEY (`id`),
--   KEY `select_apps` (`client`)
-- ) ENGINE=MEMORY  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;


ALTER TABLE `Client_Versions`
  ADD CONSTRAINT `fk_Client_Versions_Flavours1` FOREIGN KEY (`Flavours_name`) REFERENCES `Flavours` (`name`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_Client_Versions_Releases1` FOREIGN KEY (`Releases_name`) REFERENCES `Releases` (`name`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `RecvPackages`
  ADD CONSTRAINT `fk_RecvPackages_Flavours1` FOREIGN KEY (`Flavours_name`) REFERENCES `Flavours` (`name`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_RecvPackages_Releases1` FOREIGN KEY (`Releases_name`) REFERENCES `Releases` (`name`) ON DELETE NO ACTION ON UPDATE NO ACTION;

INSERT INTO `Flavours` (`name`) VALUES
('client'),
('desktop'),
('other'),
('server');

INSERT INTO `Releases` (`name`) VALUES
('15'),
('16'),
('19'),
('21'),
('other');

COMMIT;

-- use analytics;

-- start transaction;

-- ALTER TABLE `tmp_clients` ADD `arch` VARCHAR(10) NULL DEFAULT NULL AFTER `status`, ADD `mem` INT UNSIGNED NULL DEFAULT NULL AFTER `arch`, ADD `vga` VARCHAR(80) NULL DEFAULT NULL AFTER `mem`, ADD `cpu` VARCHAR(80) NULL DEFAULT NULL AFTER `vga`, ADD `ncpu` TINYINT UNSIGNED NULL DEFAULT NULL AFTER `cpu`;

-- ALTER TABLE `Client_Versions` ADD `arch` VARCHAR(10) NULL DEFAULT NULL AFTER `string_flavour`, ADD `mem` INT UNSIGNED NULL DEFAULT NULL AFTER `arch`, ADD `vga` VARCHAR(80) NULL DEFAULT NULL AFTER `mem`, ADD `cpu` VARCHAR(80) NULL DEFAULT NULL AFTER `vga`, ADD `ncpu` TINYINT UNSIGNED NULL DEFAULT NULL AFTER `cpu`;

-- ALTER TABLE `PackagesWhitelist` ADD `status` BOOLEAN NULL DEFAULT NULL AFTER `name`;

-- commit;

-- use analytics;

-- start transaction;

-- ALTER TABLE `tmp_clients` ADD `ltsp` BOOLEAN NULL DEFAULT NULL AFTER `ncpu`, ADD `mode` CHAR(4) NULL DEFAULT NULL AFTER `ltsp`;

-- ALTER TABLE `Client_Versions` ADD `ltsp` BOOLEAN NULL DEFAULT NULL AFTER `ncpu`, ADD `mode` CHAR(4) NULL DEFAULT NULL AFTER `ltsp`;

-- ALTER TABLE `Client_Versions` ADD INDEX `ltsp_mode` (`ltsp`, `mode`);

-- commit;