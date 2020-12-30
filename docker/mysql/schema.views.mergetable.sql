-- Adminer 4.7.7 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;

SET NAMES utf8mb4;

DROP DATABASE IF EXISTS `analytics`;
CREATE DATABASE `analytics` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `analytics`;

DROP TABLE IF EXISTS `Alias`;
CREATE TABLE `Alias` (
  `name` varchar(45) NOT NULL,
  `alias` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `Client_Versions`;
CREATE TABLE `Client_Versions` (
  `uuid` bigint unsigned NOT NULL,
  `Client_uid` varchar(18) NOT NULL,
  `Releases_name` varchar(45) NOT NULL,
  `Flavours_name` varchar(45) NOT NULL,
  `date` date NOT NULL,
  `string_release` varchar(45) NOT NULL,
  `string_flavour` varchar(100) NOT NULL,
  `arch` varchar(10) DEFAULT NULL,
  `mem` int unsigned DEFAULT NULL,
  `vga` varchar(80) DEFAULT NULL,
  `cpu` varchar(80) DEFAULT NULL,
  `ncpu` tinyint unsigned DEFAULT NULL,
  `ltsp` tinyint(1) DEFAULT NULL,
  `mode` char(4) DEFAULT NULL,
  PRIMARY KEY (`uuid`),
  KEY `fk_Client_Versions_Releases1_idx` (`Releases_name`),
  KEY `fk_Client_Versions_Flavours1_idx` (`Flavours_name`),
  KEY `get_clients` (`date`,`Releases_name`,`Flavours_name`,`Client_uid`),
  KEY `get_clients_other` (`date`,`Flavours_name`,`Client_uid`),
  KEY `ltsp_mode` (`ltsp`,`mode`),
  CONSTRAINT `fk_Client_Versions_Flavours1` FOREIGN KEY (`Flavours_name`) REFERENCES `Flavours` (`name`),
  CONSTRAINT `fk_Client_Versions_Releases1` FOREIGN KEY (`Releases_name`) REFERENCES `Releases` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `Config`;
CREATE TABLE `Config` (
  `name` varchar(20) NOT NULL,
  `value` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `Flavours`;
CREATE TABLE `Flavours` (
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `Flavours` (`name`) VALUES
('client'),
('desktop'),
('other'),
('server');

DROP TABLE IF EXISTS `PackagesWhitelist`;
CREATE TABLE `PackagesWhitelist` (
  `name` varchar(45) NOT NULL,
  `status` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `RecvPackages`;
CREATE TABLE `RecvPackages` (
  `uuid` bigint unsigned NOT NULL,
  `string` varchar(45) NOT NULL,
  `date` date NOT NULL,
  `Releases_name` varchar(45) NOT NULL,
  `Flavours_name` varchar(45) NOT NULL,
  `count` int unsigned NOT NULL,
  PRIMARY KEY (`uuid`),
  KEY `fk_RecvPackages_Releases1_idx` (`Releases_name`),
  KEY `fk_RecvPackages_Flavours1_idx` (`Flavours_name`),
  KEY `get_top_apps` (`date`,`Releases_name`,`Flavours_name`,`count`,`string`),
  KEY `get_top_apps_others` (`date`,`Flavours_name`,`count`,`string`),
  CONSTRAINT `fk_RecvPackages_Flavours1` FOREIGN KEY (`Flavours_name`) REFERENCES `Flavours` (`name`),
  CONSTRAINT `fk_RecvPackages_Releases1` FOREIGN KEY (`Releases_name`) REFERENCES `Releases` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `Releases`;
CREATE TABLE `Releases` (
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `Releases` (`name`) VALUES
('15'),
('16'),
('19'),
('21'),
('other');

DROP VIEW IF EXISTS `a`;
CREATE TABLE `a` (`year` int, `month` int, `Client_uid` varchar(18));


DROP VIEW IF EXISTS `ab`;
CREATE TABLE `ab` (`year` int, `month` int, `Client_uid` varchar(18));


DROP VIEW IF EXISTS `abc_plus_part_e`;
CREATE TABLE `abc_plus_part_e` (`year` int, `month` int, `Client_uid` varchar(18));


DROP VIEW IF EXISTS `b`;
CREATE TABLE `b` (`year` int, `month` int, `Client_uid` varchar(18));


DROP VIEW IF EXISTS `bcd`;
CREATE TABLE `bcd` (`year` int, `month` int, `Client_uid` varchar(18));


DROP VIEW IF EXISTS `c`;
CREATE TABLE `c` (`year` int, `month` int, `Client_uid` varchar(18));


DROP VIEW IF EXISTS `cd`;
CREATE TABLE `cd` (`year` int, `month` int, `Client_uid` varchar(18));


DROP VIEW IF EXISTS `compat_m`;
CREATE TABLE `compat_m` (`year` bigint, `month` bigint, `mode` varchar(4));


DROP VIEW IF EXISTS `compat_rf`;
CREATE TABLE `compat_rf` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45));


DROP VIEW IF EXISTS `compat_rfa`;
CREATE TABLE `compat_rfa` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `arch` varchar(6));


DROP VIEW IF EXISTS `compat_t`;
CREATE TABLE `compat_t` (`year` bigint, `month` bigint, `type` varchar(4));


DROP VIEW IF EXISTS `cv`;
CREATE TABLE `cv` (`Client_uid` varchar(18), `date` date, `Releases_name` varchar(45), `Flavours_name` varchar(45), `string_release` varchar(45));


DROP VIEW IF EXISTS `cv_a`;
CREATE TABLE `cv_a` (`Client_uid` varchar(18), `date` date, `Releases_name` varchar(45), `Flavours_name` varchar(45), `arch` varchar(10));


DROP VIEW IF EXISTS `cv_c`;
CREATE TABLE `cv_c` (`Client_uid` varchar(18), `date` date, `Releases_name` varchar(45), `Flavours_name` varchar(45), `ncpu` tinyint unsigned);


DROP VIEW IF EXISTS `cv_l`;
CREATE TABLE `cv_l` (`Client_uid` varchar(18), `date` date, `Releases_name` varchar(45), `Flavours_name` varchar(45), `ltsp` tinyint(1), `mode` char(4));


DROP VIEW IF EXISTS `cv_m`;
CREATE TABLE `cv_m` (`Client_uid` varchar(18), `date` date, `Releases_name` varchar(45), `Flavours_name` varchar(45), `mem` int unsigned);


DROP VIEW IF EXISTS `d`;
CREATE TABLE `d` (`year` int, `month` int, `Client_uid` varchar(18));


DROP VIEW IF EXISTS `dates`;
CREATE TABLE `dates` (`year` bigint, `month` bigint);


DROP VIEW IF EXISTS `na`;
CREATE TABLE `na` (`year` bigint, `month` bigint, `a` bigint);


DROP VIEW IF EXISTS `nb`;
CREATE TABLE `nb` (`year` bigint, `month` bigint, `b` bigint);


DROP VIEW IF EXISTS `nc`;
CREATE TABLE `nc` (`year` bigint, `month` bigint, `c` bigint);


DROP VIEW IF EXISTS `nd`;
CREATE TABLE `nd` (`year` bigint, `month` bigint, `d` bigint);


DROP VIEW IF EXISTS `nhosts`;
CREATE TABLE `nhosts` (`year` bigint, `month` bigint, `total_hosts` decimal(42,0));


DROP VIEW IF EXISTS `nhosts_detail`;
CREATE TABLE `nhosts_detail` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total_hosts` bigint);


DROP VIEW IF EXISTS `resume`;
CREATE TABLE `resume` (`year` bigint, `month` bigint, `total_hosts` decimal(42,0), `single_entry` bigint, `target_hosts` decimal(43,0), `a` bigint, `b` bigint, `c` bigint, `d` bigint, `e` decimal(47,0));


DROP VIEW IF EXISTS `single_entry`;
CREATE TABLE `single_entry` (`year` bigint, `month` bigint, `single_entry` bigint);


DROP VIEW IF EXISTS `target_arch`;
CREATE TABLE `target_arch` (`year` int, `month` int, `rel` varchar(45), `fla` varchar(45), `arch` varchar(10), `total` bigint);


DROP VIEW IF EXISTS `target_cpu_dual`;
CREATE TABLE `target_cpu_dual` (`year` int, `month` int, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `target_cpu_mono`;
CREATE TABLE `target_cpu_mono` (`year` int, `month` int, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `target_cpu_more`;
CREATE TABLE `target_cpu_more` (`year` int, `month` int, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `target_cpunull`;
CREATE TABLE `target_cpunull` (`year` int, `month` int, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `target_mem2G`;
CREATE TABLE `target_mem2G` (`year` int, `month` int, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `target_mem4G`;
CREATE TABLE `target_mem4G` (`year` int, `month` int, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `target_mem8G`;
CREATE TABLE `target_mem8G` (`year` int, `month` int, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `target_memnull`;
CREATE TABLE `target_memnull` (`year` int, `month` int, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `target_mode`;
CREATE TABLE `target_mode` (`year` int, `month` int, `mode` varchar(4), `total` bigint);


DROP VIEW IF EXISTS `target_type`;
CREATE TABLE `target_type` (`year` int, `month` int, `type` varchar(4), `total` bigint);


DROP VIEW IF EXISTS `tmp_resume`;
CREATE TABLE `tmp_resume` (`year` bigint, `month` bigint, `total_hosts` decimal(42,0), `single_entry` bigint, `a` bigint, `b` bigint, `c` bigint, `d` bigint);


DROP VIEW IF EXISTS `v_architectures`;
CREATE TABLE `v_architectures` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `arch` varchar(6), `total` bigint);


DROP VIEW IF EXISTS `v_cpu_dual`;
CREATE TABLE `v_cpu_dual` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `v_cpu_mono`;
CREATE TABLE `v_cpu_mono` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `v_cpu_null`;
CREATE TABLE `v_cpu_null` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `v_cpu_other`;
CREATE TABLE `v_cpu_other` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `v_ltsp_modes`;
CREATE TABLE `v_ltsp_modes` (`year` bigint, `month` bigint, `mode` varchar(4), `total` bigint);


DROP VIEW IF EXISTS `v_ltsp_types`;
CREATE TABLE `v_ltsp_types` (`year` bigint, `month` bigint, `type` varchar(4), `total` bigint);


DROP VIEW IF EXISTS `v_mem_2g`;
CREATE TABLE `v_mem_2g` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `v_mem_4g`;
CREATE TABLE `v_mem_4g` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `v_mem_8g`;
CREATE TABLE `v_mem_8g` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `v_mem_null`;
CREATE TABLE `v_mem_null` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total` bigint);


DROP VIEW IF EXISTS `v_nhosts`;
CREATE TABLE `v_nhosts` (`year` bigint, `month` bigint, `rel` varchar(45), `fla` varchar(45), `total_hosts` bigint);


DROP TABLE IF EXISTS `a`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `a` AS select `ab`.`year` AS `year`,`ab`.`month` AS `month`,`ab`.`Client_uid` AS `Client_uid` from (`ab` left join `bcd` on(((`ab`.`year` = `bcd`.`year`) and (`ab`.`month` = `bcd`.`month`) and (`ab`.`Client_uid` = `bcd`.`Client_uid`)))) where (`bcd`.`Client_uid` is null);

DROP TABLE IF EXISTS `ab`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `ab` AS select `t`.`year` AS `year`,`t`.`month` AS `month`,`t`.`Client_uid` AS `Client_uid` from (select distinct `cv`.`Client_uid` AS `Client_uid`,`cv`.`Releases_name` AS `Releases_name`,year(`cv`.`date`) AS `year`,month(`cv`.`date`) AS `month` from `cv`) `t` group by `t`.`year`,`t`.`month`,`t`.`Client_uid` having (count(0) > 1);

DROP TABLE IF EXISTS `abc_plus_part_e`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `abc_plus_part_e` AS select `t`.`year` AS `year`,`t`.`month` AS `month`,`t`.`Client_uid` AS `Client_uid` from (select distinct `cv`.`Client_uid` AS `Client_uid`,`cv`.`string_release` AS `string_release`,year(`cv`.`date`) AS `year`,month(`cv`.`date`) AS `month` from `cv`) `t` group by `t`.`year`,`t`.`month`,`t`.`Client_uid` having (count(0) > 1);

DROP TABLE IF EXISTS `b`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `b` AS select `ab`.`year` AS `year`,`ab`.`month` AS `month`,`ab`.`Client_uid` AS `Client_uid` from (`ab` join `bcd` on(((`ab`.`year` = `bcd`.`year`) and (`ab`.`month` = `bcd`.`month`) and (`ab`.`Client_uid` = `bcd`.`Client_uid`))));

DROP TABLE IF EXISTS `bcd`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `bcd` AS select `t`.`year` AS `year`,`t`.`month` AS `month`,`t`.`Client_uid` AS `Client_uid` from (select distinct `cv`.`Client_uid` AS `Client_uid`,`cv`.`Flavours_name` AS `Flavours_name`,year(`cv`.`date`) AS `year`,month(`cv`.`date`) AS `month` from `cv`) `t` group by `t`.`year`,`t`.`month`,`t`.`Client_uid` having (count(0) > 1);

DROP TABLE IF EXISTS `c`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `c` AS select `cd`.`year` AS `year`,`cd`.`month` AS `month`,`cd`.`Client_uid` AS `Client_uid` from (`cd` left join `d` on(((`cd`.`year` = `d`.`year`) and (`cd`.`month` = `d`.`month`) and (`cd`.`Client_uid` = `d`.`Client_uid`)))) where (`d`.`Client_uid` is null);

DROP TABLE IF EXISTS `cd`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `cd` AS select `bcd`.`year` AS `year`,`bcd`.`month` AS `month`,`bcd`.`Client_uid` AS `Client_uid` from (`bcd` left join `ab` on(((`bcd`.`year` = `ab`.`year`) and (`bcd`.`month` = `ab`.`month`) and (`bcd`.`Client_uid` = `ab`.`Client_uid`)))) where (`ab`.`Client_uid` is null);

DROP TABLE IF EXISTS `compat_m`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `compat_m` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month`,`types`.`mode` AS `mode` from (`dates` join (select 'THIN' AS `mode` union all select 'SEMI' AS `SEMI` union all select 'FAT' AS `FAT` union all select 'UNKN' AS `UNKN`) `types`);

DROP TABLE IF EXISTS `compat_rf`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `compat_rf` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month`,`rels`.`rel` AS `rel`,`flas`.`fla` AS `fla` from ((`dates` join (select `Releases`.`name` AS `rel` from `Releases` where (`Releases`.`name` <> 'other')) `rels`) join (select `Flavours`.`name` AS `fla` from `Flavours`) `flas`);

DROP TABLE IF EXISTS `compat_rfa`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `compat_rfa` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,`arches`.`arch` AS `arch` from (`compat_rf` join (select 'x86_64' AS `arch` union all select 'i686' AS `i686` union all select 'UNKN' AS `UNKN`) `arches`);

DROP TABLE IF EXISTS `compat_t`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `compat_t` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month`,`types`.`type` AS `type` from (`dates` join (select 0 AS `type` union all select 1 AS `1` union all select 'UNKN' AS `UNKN`) `types`);

DROP TABLE IF EXISTS `cv`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `cv` AS select `Client_Versions`.`Client_uid` AS `Client_uid`,`Client_Versions`.`date` AS `date`,`Client_Versions`.`Releases_name` AS `Releases_name`,`Client_Versions`.`Flavours_name` AS `Flavours_name`,`Client_Versions`.`string_release` AS `string_release` from `Client_Versions`;

DROP TABLE IF EXISTS `cv_a`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `cv_a` AS select `Client_Versions`.`Client_uid` AS `Client_uid`,`Client_Versions`.`date` AS `date`,`Client_Versions`.`Releases_name` AS `Releases_name`,`Client_Versions`.`Flavours_name` AS `Flavours_name`,`Client_Versions`.`arch` AS `arch` from `Client_Versions`;

DROP TABLE IF EXISTS `cv_c`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `cv_c` AS select `Client_Versions`.`Client_uid` AS `Client_uid`,`Client_Versions`.`date` AS `date`,`Client_Versions`.`Releases_name` AS `Releases_name`,`Client_Versions`.`Flavours_name` AS `Flavours_name`,`Client_Versions`.`ncpu` AS `ncpu` from `Client_Versions`;

DROP TABLE IF EXISTS `cv_l`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `cv_l` AS select `Client_Versions`.`Client_uid` AS `Client_uid`,`Client_Versions`.`date` AS `date`,`Client_Versions`.`Releases_name` AS `Releases_name`,`Client_Versions`.`Flavours_name` AS `Flavours_name`,`Client_Versions`.`ltsp` AS `ltsp`,`Client_Versions`.`mode` AS `mode` from `Client_Versions`;

DROP TABLE IF EXISTS `cv_m`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `cv_m` AS select `Client_Versions`.`Client_uid` AS `Client_uid`,`Client_Versions`.`date` AS `date`,`Client_Versions`.`Releases_name` AS `Releases_name`,`Client_Versions`.`Flavours_name` AS `Flavours_name`,`Client_Versions`.`mem` AS `mem` from `Client_Versions`;

DROP TABLE IF EXISTS `d`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `d` AS select `cd`.`year` AS `year`,`cd`.`month` AS `month`,`cd`.`Client_uid` AS `Client_uid` from (`cd` left join `abc_plus_part_e` on(((`cd`.`year` = `abc_plus_part_e`.`year`) and (`cd`.`month` = `abc_plus_part_e`.`month`) and (`cd`.`Client_uid` = `abc_plus_part_e`.`Client_uid`)))) where (`abc_plus_part_e`.`Client_uid` is null);

DROP TABLE IF EXISTS `dates`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `dates` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month` from (select `compat`.`year` AS `year`,`compat`.`month` AS `month` from (select `dates`.`year` AS `year`,`dates`.`month` AS `month` from (select `years`.`year` AS `year`,`months`.`month` AS `month` from ((select year(now()) AS `year` union all select year((now() - interval 1 year)) AS `year(date_sub(now(),interval 1 year))`) `years` join (select 1 AS `month` union all select 2 AS `2` union all select 3 AS `3` union all select 4 AS `4` union all select 5 AS `5` union all select 6 AS `6` union all select 7 AS `7` union all select 8 AS `8` union all select 9 AS `9` union all select 10 AS `10` union all select 11 AS `11` union all select 12 AS `12`) `months`)) `dates` where ((str_to_date(concat(`dates`.`year`,'-',`dates`.`month`,'-01'),'%Y-%m-%d') >= (now() - interval 1 year)) and (str_to_date(concat(`dates`.`year`,'-',`dates`.`month`,'-01'),'%Y-%m-%d') < now()))) `compat`) `dates` order by `dates`.`year`,`dates`.`month`;

DROP TABLE IF EXISTS `na`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `na` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month`,ifnull(`t`.`a`,0) AS `a` from (`dates` left join (select `a`.`year` AS `year`,`a`.`month` AS `month`,count(0) AS `a` from `a` group by `a`.`year`,`a`.`month`) `t` on(((`dates`.`year` = `t`.`year`) and (`dates`.`month` = `t`.`month`))));

DROP TABLE IF EXISTS `nb`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `nb` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month`,ifnull(`t`.`b`,0) AS `b` from (`dates` left join (select `b`.`year` AS `year`,`b`.`month` AS `month`,count(0) AS `b` from `b` group by `b`.`year`,`b`.`month`) `t` on(((`dates`.`year` = `t`.`year`) and (`dates`.`month` = `t`.`month`))));

DROP TABLE IF EXISTS `nc`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `nc` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month`,ifnull(`t`.`c`,0) AS `c` from (`dates` left join (select `c`.`year` AS `year`,`c`.`month` AS `month`,count(0) AS `c` from `c` group by `c`.`year`,`c`.`month`) `t` on(((`dates`.`year` = `t`.`year`) and (`dates`.`month` = `t`.`month`))));

DROP TABLE IF EXISTS `nd`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `nd` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month`,ifnull(`t`.`d`,0) AS `d` from (`dates` left join (select `d`.`year` AS `year`,`d`.`month` AS `month`,count(0) AS `d` from `d` group by `d`.`year`,`d`.`month`) `t` on(((`dates`.`year` = `t`.`year`) and (`dates`.`month` = `t`.`month`))));

DROP TABLE IF EXISTS `nhosts`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `nhosts` AS select `nhosts_detail`.`year` AS `year`,`nhosts_detail`.`month` AS `month`,sum(`nhosts_detail`.`total_hosts`) AS `total_hosts` from `nhosts_detail` group by `nhosts_detail`.`year`,`nhosts_detail`.`month`;

DROP TABLE IF EXISTS `nhosts_detail`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `nhosts_detail` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,`detailed`.`total_hosts` AS `total_hosts` from (`compat_rf` left join (select `unique_last_clients`.`year` AS `year`,`unique_last_clients`.`month` AS `month`,`unique_last_clients`.`rel` AS `rel`,`unique_last_clients`.`fla` AS `fla`,ifnull(count(0),0) AS `total_hosts` from (select year(`t`.`date`) AS `year`,month(`t`.`date`) AS `month`,`t`.`Releases_name` AS `rel`,`t`.`Flavours_name` AS `fla`,`t`.`Client_uid` AS `Client_uid` from (select `cv`.`Client_uid` AS `Client_uid`,`cv`.`Releases_name` AS `Releases_name`,`cv`.`Flavours_name` AS `Flavours_name`,`cv`.`date` AS `date` from `cv` order by `cv`.`date` desc) `t` group by year(`t`.`date`),month(`t`.`date`),`t`.`Releases_name`,`t`.`Flavours_name`,`t`.`Client_uid`) `unique_last_clients` group by `unique_last_clients`.`year`,`unique_last_clients`.`month`,`unique_last_clients`.`rel`,`unique_last_clients`.`fla`) `detailed` on(((`compat_rf`.`year` = `detailed`.`year`) and (`compat_rf`.`month` = `detailed`.`month`) and (`compat_rf`.`rel` = `detailed`.`rel`) and (`compat_rf`.`fla` = `detailed`.`fla`))));

DROP TABLE IF EXISTS `resume`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `resume` AS select `tmp_resume`.`year` AS `year`,`tmp_resume`.`month` AS `month`,`tmp_resume`.`total_hosts` AS `total_hosts`,`tmp_resume`.`single_entry` AS `single_entry`,(`tmp_resume`.`total_hosts` - `tmp_resume`.`single_entry`) AS `target_hosts`,`tmp_resume`.`a` AS `a`,`tmp_resume`.`b` AS `b`,`tmp_resume`.`c` AS `c`,`tmp_resume`.`d` AS `d`,(((((`tmp_resume`.`total_hosts` - `tmp_resume`.`single_entry`) - `tmp_resume`.`a`) - `tmp_resume`.`b`) - `tmp_resume`.`c`) - `tmp_resume`.`d`) AS `e` from `tmp_resume`;

DROP TABLE IF EXISTS `single_entry`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `single_entry` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month`,ifnull(`singles`.`single_entry`,0) AS `single_entry` from (`dates` left join (select `a`.`year` AS `year`,`a`.`month` AS `month`,count(0) AS `single_entry` from (select year(`cv`.`date`) AS `year`,month(`cv`.`date`) AS `month` from `cv` group by year(`cv`.`date`),month(`cv`.`date`),`cv`.`Client_uid` having (count(0) = 1)) `a` group by `a`.`year`,`a`.`month`) `singles` on(((`dates`.`year` = `singles`.`year`) and (`dates`.`month` = `singles`.`month`))));

DROP TABLE IF EXISTS `target_arch`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_arch` AS select year(`cv_a`.`date`) AS `year`,month(`cv_a`.`date`) AS `month`,`cv_a`.`Releases_name` AS `rel`,`cv_a`.`Flavours_name` AS `fla`,ifnull(if((`cv_a`.`arch` like 'NULL'),NULL,`cv_a`.`arch`),'UNKN') AS `arch`,count(distinct `cv_a`.`Client_uid`) AS `total` from `cv_a` group by `year`,`month`,`cv_a`.`Releases_name`,`cv_a`.`Flavours_name`,`cv_a`.`arch`;

DROP TABLE IF EXISTS `target_cpu_dual`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_cpu_dual` AS select year(`cv_c`.`date`) AS `year`,month(`cv_c`.`date`) AS `month`,`cv_c`.`Releases_name` AS `rel`,`cv_c`.`Flavours_name` AS `fla`,count(distinct `cv_c`.`Client_uid`) AS `total` from `cv_c` where ((`cv_c`.`ncpu` > 1) and (`cv_c`.`ncpu` < 5) and (`cv_c`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`rel`,`fla`;

DROP TABLE IF EXISTS `target_cpu_mono`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_cpu_mono` AS select year(`cv_c`.`date`) AS `year`,month(`cv_c`.`date`) AS `month`,`cv_c`.`Releases_name` AS `rel`,`cv_c`.`Flavours_name` AS `fla`,count(distinct `cv_c`.`Client_uid`) AS `total` from `cv_c` where ((`cv_c`.`ncpu` < 2) and (`cv_c`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`rel`,`fla`;

DROP TABLE IF EXISTS `target_cpu_more`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_cpu_more` AS select year(`cv_c`.`date`) AS `year`,month(`cv_c`.`date`) AS `month`,`cv_c`.`Releases_name` AS `rel`,`cv_c`.`Flavours_name` AS `fla`,count(distinct `cv_c`.`Client_uid`) AS `total` from `cv_c` where ((`cv_c`.`ncpu` > 4) and (`cv_c`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`rel`,`fla`;

DROP TABLE IF EXISTS `target_cpunull`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_cpunull` AS select year(`cv_c`.`date`) AS `year`,month(`cv_c`.`date`) AS `month`,`cv_c`.`Releases_name` AS `rel`,`cv_c`.`Flavours_name` AS `fla`,count(distinct `cv_c`.`Client_uid`) AS `total` from `cv_c` where ((`cv_c`.`ncpu` is null) and (`cv_c`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`rel`,`fla`;

DROP TABLE IF EXISTS `target_mem2G`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_mem2G` AS select year(`cv_m`.`date`) AS `year`,month(`cv_m`.`date`) AS `month`,`cv_m`.`Releases_name` AS `rel`,`cv_m`.`Flavours_name` AS `fla`,count(distinct `cv_m`.`Client_uid`) AS `total` from `cv_m` where ((`cv_m`.`mem` < 2048000) and (`cv_m`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`rel`,`fla`;

DROP TABLE IF EXISTS `target_mem4G`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_mem4G` AS select year(`cv_m`.`date`) AS `year`,month(`cv_m`.`date`) AS `month`,`cv_m`.`Releases_name` AS `rel`,`cv_m`.`Flavours_name` AS `fla`,count(distinct `cv_m`.`Client_uid`) AS `total` from `cv_m` where ((`cv_m`.`mem` > 2048000) and (`cv_m`.`mem` < 4096000) and (`cv_m`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`rel`,`fla`;

DROP TABLE IF EXISTS `target_mem8G`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_mem8G` AS select year(`cv_m`.`date`) AS `year`,month(`cv_m`.`date`) AS `month`,`cv_m`.`Releases_name` AS `rel`,`cv_m`.`Flavours_name` AS `fla`,count(distinct `cv_m`.`Client_uid`) AS `total` from `cv_m` where ((`cv_m`.`mem` > 4096000) and (`cv_m`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`rel`,`fla`;

DROP TABLE IF EXISTS `target_memnull`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_memnull` AS select year(`cv_m`.`date`) AS `year`,month(`cv_m`.`date`) AS `month`,`cv_m`.`Releases_name` AS `rel`,`cv_m`.`Flavours_name` AS `fla`,count(distinct `cv_m`.`Client_uid`) AS `total` from `cv_m` where ((`cv_m`.`mem` is null) and (`cv_m`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`rel`,`fla`;

DROP TABLE IF EXISTS `target_mode`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_mode` AS select year(`cv_l`.`date`) AS `year`,month(`cv_l`.`date`) AS `month`,ifnull(`cv_l`.`mode`,'UNKN') AS `mode`,count(distinct `cv_l`.`Client_uid`) AS `total` from `cv_l` where ((`cv_l`.`Flavours_name` = 'client') and (`cv_l`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`cv_l`.`mode`;

DROP TABLE IF EXISTS `target_type`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `target_type` AS select year(`cv_l`.`date`) AS `year`,month(`cv_l`.`date`) AS `month`,ifnull(`cv_l`.`ltsp`,'UNKN') AS `type`,count(distinct `cv_l`.`Client_uid`) AS `total` from `cv_l` where ((`cv_l`.`Flavours_name` = 'client') and (`cv_l`.`date` >= (now() - interval 1 year))) group by `year`,`month`,`cv_l`.`ltsp`;

DROP TABLE IF EXISTS `tmp_resume`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `tmp_resume` AS select `dates`.`year` AS `year`,`dates`.`month` AS `month`,`nhosts`.`total_hosts` AS `total_hosts`,`single_entry`.`single_entry` AS `single_entry`,`na`.`a` AS `a`,`nb`.`b` AS `b`,`nc`.`c` AS `c`,`nd`.`d` AS `d` from ((((((`dates` left join `nhosts` on(((`dates`.`year` = `nhosts`.`year`) and (`dates`.`month` = `nhosts`.`month`)))) join `single_entry` on(((`dates`.`year` = `single_entry`.`year`) and (`dates`.`month` = `single_entry`.`month`)))) join `na` on(((`dates`.`year` = `na`.`year`) and (`dates`.`month` = `na`.`month`)))) join `nb` on(((`dates`.`year` = `nb`.`year`) and (`dates`.`month` = `nb`.`month`)))) join `nc` on(((`dates`.`year` = `nc`.`year`) and (`dates`.`month` = `nc`.`month`)))) join `nd` on(((`dates`.`year` = `nd`.`year`) and (`dates`.`month` = `nd`.`month`))));

DROP TABLE IF EXISTS `v_architectures`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_architectures` AS select `compat_rfa`.`year` AS `year`,`compat_rfa`.`month` AS `month`,`compat_rfa`.`rel` AS `rel`,`compat_rfa`.`fla` AS `fla`,`compat_rfa`.`arch` AS `arch`,ifnull(`target_arch`.`total`,0) AS `total` from (`compat_rfa` left join `target_arch` on(((`compat_rfa`.`year` = `target_arch`.`year`) and (`compat_rfa`.`month` = `target_arch`.`month`) and (`compat_rfa`.`rel` = `target_arch`.`rel`) and (`compat_rfa`.`fla` = `target_arch`.`fla`) and (convert(`compat_rfa`.`arch` using utf8) = `target_arch`.`arch`)))) order by `compat_rfa`.`year` desc,`compat_rfa`.`month` desc,`compat_rfa`.`rel`,`compat_rfa`.`fla`,`compat_rfa`.`arch`;

DROP TABLE IF EXISTS `v_cpu_dual`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_cpu_dual` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,ifnull(`target_cpu_dual`.`total`,0) AS `total` from (`compat_rf` left join `target_cpu_dual` on(((`compat_rf`.`year` = `target_cpu_dual`.`year`) and (`compat_rf`.`month` = `target_cpu_dual`.`month`) and (`compat_rf`.`rel` = `target_cpu_dual`.`rel`) and (`compat_rf`.`fla` = `target_cpu_dual`.`fla`)))) order by `compat_rf`.`year` desc,`compat_rf`.`month` desc,`compat_rf`.`rel`,`compat_rf`.`fla`;

DROP TABLE IF EXISTS `v_cpu_mono`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_cpu_mono` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,ifnull(`target_cpu_mono`.`total`,0) AS `total` from (`compat_rf` left join `target_cpu_mono` on(((`compat_rf`.`year` = `target_cpu_mono`.`year`) and (`compat_rf`.`month` = `target_cpu_mono`.`month`) and (`compat_rf`.`rel` = `target_cpu_mono`.`rel`) and (`compat_rf`.`fla` = `target_cpu_mono`.`fla`)))) order by `compat_rf`.`year` desc,`compat_rf`.`month` desc,`compat_rf`.`rel`,`compat_rf`.`fla`;

DROP TABLE IF EXISTS `v_cpu_null`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_cpu_null` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,ifnull(`target_cpunull`.`total`,0) AS `total` from (`compat_rf` left join `target_cpunull` on(((`compat_rf`.`year` = `target_cpunull`.`year`) and (`compat_rf`.`month` = `target_cpunull`.`month`) and (`compat_rf`.`rel` = `target_cpunull`.`rel`) and (`compat_rf`.`fla` = `target_cpunull`.`fla`)))) order by `compat_rf`.`year` desc,`compat_rf`.`month` desc,`compat_rf`.`rel`,`compat_rf`.`fla`;

DROP TABLE IF EXISTS `v_cpu_other`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_cpu_other` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,ifnull(`target_cpu_more`.`total`,0) AS `total` from (`compat_rf` left join `target_cpu_more` on(((`compat_rf`.`year` = `target_cpu_more`.`year`) and (`compat_rf`.`month` = `target_cpu_more`.`month`) and (`compat_rf`.`rel` = `target_cpu_more`.`rel`) and (`compat_rf`.`fla` = `target_cpu_more`.`fla`)))) order by `compat_rf`.`year` desc,`compat_rf`.`month` desc,`compat_rf`.`rel`,`compat_rf`.`fla`;

DROP TABLE IF EXISTS `v_ltsp_modes`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_ltsp_modes` AS select `compat_m`.`year` AS `year`,`compat_m`.`month` AS `month`,`compat_m`.`mode` AS `mode`,ifnull(`target_mode`.`total`,0) AS `total` from (`compat_m` left join `target_mode` on(((`compat_m`.`year` = `target_mode`.`year`) and (`compat_m`.`month` = `target_mode`.`month`) and (convert(`compat_m`.`mode` using utf8) = `target_mode`.`mode`)))) order by `compat_m`.`year` desc,`compat_m`.`month` desc,`compat_m`.`mode`;

DROP TABLE IF EXISTS `v_ltsp_types`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_ltsp_types` AS select `compat_t`.`year` AS `year`,`compat_t`.`month` AS `month`,`compat_t`.`type` AS `type`,ifnull(`target_type`.`total`,0) AS `total` from (`compat_t` left join `target_type` on(((`compat_t`.`year` = `target_type`.`year`) and (`compat_t`.`month` = `target_type`.`month`) and (`compat_t`.`type` = `target_type`.`type`)))) order by `compat_t`.`year` desc,`compat_t`.`month` desc,`compat_t`.`type`;

DROP TABLE IF EXISTS `v_mem_2g`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_mem_2g` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,ifnull(`target_mem2G`.`total`,0) AS `total` from (`compat_rf` left join `target_mem2G` on(((`compat_rf`.`year` = `target_mem2G`.`year`) and (`compat_rf`.`month` = `target_mem2G`.`month`) and (`compat_rf`.`rel` = `target_mem2G`.`rel`) and (`compat_rf`.`fla` = `target_mem2G`.`fla`)))) order by `compat_rf`.`year` desc,`compat_rf`.`month` desc,`compat_rf`.`rel`,`compat_rf`.`fla`;

DROP TABLE IF EXISTS `v_mem_4g`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_mem_4g` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,ifnull(`target_mem4G`.`total`,0) AS `total` from (`compat_rf` left join `target_mem4G` on(((`compat_rf`.`year` = `target_mem4G`.`year`) and (`compat_rf`.`month` = `target_mem4G`.`month`) and (`compat_rf`.`rel` = `target_mem4G`.`rel`) and (`compat_rf`.`fla` = `target_mem4G`.`fla`)))) order by `compat_rf`.`year` desc,`compat_rf`.`month` desc,`compat_rf`.`rel`,`compat_rf`.`fla`;

DROP TABLE IF EXISTS `v_mem_8g`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_mem_8g` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,ifnull(`target_mem8G`.`total`,0) AS `total` from (`compat_rf` left join `target_mem8G` on(((`compat_rf`.`year` = `target_mem8G`.`year`) and (`compat_rf`.`month` = `target_mem8G`.`month`) and (`compat_rf`.`rel` = `target_mem8G`.`rel`) and (`compat_rf`.`fla` = `target_mem8G`.`fla`)))) order by `compat_rf`.`year` desc,`compat_rf`.`month` desc,`compat_rf`.`rel`,`compat_rf`.`fla`;

DROP TABLE IF EXISTS `v_mem_null`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_mem_null` AS select `compat_rf`.`year` AS `year`,`compat_rf`.`month` AS `month`,`compat_rf`.`rel` AS `rel`,`compat_rf`.`fla` AS `fla`,ifnull(`target_memnull`.`total`,0) AS `total` from (`compat_rf` left join `target_memnull` on(((`compat_rf`.`year` = `target_memnull`.`year`) and (`compat_rf`.`month` = `target_memnull`.`month`) and (`compat_rf`.`rel` = `target_memnull`.`rel`) and (`compat_rf`.`fla` = `target_memnull`.`fla`)))) order by `compat_rf`.`year` desc,`compat_rf`.`month` desc,`compat_rf`.`rel`,`compat_rf`.`fla`;

DROP TABLE IF EXISTS `v_nhosts`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_nhosts` AS select `nhosts_detail`.`year` AS `year`,`nhosts_detail`.`month` AS `month`,`nhosts_detail`.`rel` AS `rel`,`nhosts_detail`.`fla` AS `fla`,`nhosts_detail`.`total_hosts` AS `total_hosts` from `nhosts_detail` order by `nhosts_detail`.`year` desc,`nhosts_detail`.`month` desc;

-- 2020-12-05 20:22:53
