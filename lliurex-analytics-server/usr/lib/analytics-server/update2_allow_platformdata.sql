use analytics;

start transaction;

ALTER TABLE `tmp_clients` ADD `ltsp` BOOLEAN NULL DEFAULT NULL AFTER `ncpu`, ADD `mode` CHAR(4) NULL DEFAULT NULL AFTER `ltsp`;

ALTER TABLE `Client_Versions` ADD `ltsp` BOOLEAN NULL DEFAULT NULL AFTER `ncpu`, ADD `mode` CHAR(4) NULL DEFAULT NULL AFTER `ltsp`;

ALTER TABLE `Client_Versions` ADD INDEX `ltsp_mode` (`ltsp`, `mode`);

commit;