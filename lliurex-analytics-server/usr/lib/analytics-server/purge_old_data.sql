use analytics;
start transaction;
DELIMITER $$

DROP PROCEDURE IF EXISTS drop_index_if_exists $$
CREATE PROCEDURE drop_index_if_exists(in theTable varchar(128), in theIndexName varchar(128) )
BEGIN
 IF((SELECT COUNT(*) AS index_exists FROM information_schema.statistics WHERE TABLE_SCHEMA = DATABASE() and table_name =
theTable AND index_name = theIndexName) > 0) THEN
   SET @s = CONCAT('DROP INDEX ' , theIndexName , ' ON ' , theTable);
   PREPARE stmt FROM @s;
   EXECUTE stmt;
 END IF;
END $$

DROP PROCEDURE IF EXISTS drop_primary_index_if_exists $$
CREATE PROCEDURE drop_primary_index_if_exists(in theTable varchar(128))
BEGIN
 IF((SELECT COUNT(*) AS index_exists FROM information_schema.statistics WHERE TABLE_SCHEMA = DATABASE() and table_name =
theTable AND index_name = 'PRIMARY') > 0) THEN
   SET @s = CONCAT('ALTER TABLE ', theTable, ' DROP PRIMARY KEY ');
   PREPARE stmt FROM @s;
   EXECUTE stmt;
 END IF;
END $$

DELIMITER ;
commit;
start transaction;

# PURGE OLD DATA (1 year older)
# CREATE TABLES
create table if not exists RecvPackages_historical like RecvPackages;
create table if not exists Client_Versions_historical like Client_Versions;
create table if not exists RecvPackages_purged like RecvPackages;

call drop_primary_index_if_exists('RecvPackages_historical');
call drop_index_if_exists('RecvPackages_historical','fk_RecvPackages_Releases1_idx');
call drop_index_if_exists('RecvPackages_historical','fk_RecvPackages_Flavours1_idx');
call drop_index_if_exists('RecvPackages_historical','get_top_apps');
call drop_index_if_exists('RecvPackages_historical','get_top_apps_others');

call drop_primary_index_if_exists('Client_Versions_historical');
call drop_index_if_exists('Client_Versions_historical','fk_Client_Versions_Releases1_idx');
call drop_index_if_exists('Client_Versions_historical','fk_Client_Versions_Flavours1_idx');
call drop_index_if_exists('Client_Versions_historical','get_clients');
call drop_index_if_exists('Client_Versions_historical','get_clients_other');
call drop_index_if_exists('Client_Versions_historical','ltsp_mode');

call drop_primary_index_if_exists('RecvPackages_purged');
call drop_index_if_exists('RecvPackages_purged','fk_RecvPackages_Releases1_idx');
call drop_index_if_exists('RecvPackages_purged','fk_RecvPackages_Flavours1_idx');
call drop_index_if_exists('RecvPackages_purged','get_top_apps');
call drop_index_if_exists('RecvPackages_purged','get_top_apps_others');

DROP PROCEDURE IF EXISTS drop_index_if_exists;
DROP PROCEDURE IF EXISTS drop_primary_index_if_exists;

# BACKUP & REMOVE DATA
insert into RecvPackages_historical select * from RecvPackages where date < date_sub(date_sub(now(),interval 1 month),interval 1 year) on duplicate key update uuid=values(uuid);
delete from RecvPackages where date < date_sub(date_sub(now(),interval 1 month),interval 1 year);
insert into Client_Versions_historical select * from Client_Versions where date < date_sub(date_sub(now(),interval 1 month),interval 1 year) on duplicate key update uuid=values(uuid);
delete from Client_Versions where date < date_sub(date_sub(now(),interval 1 month),interval 1 year);

# PURGE NOT DESIRED ITEMS INTO WHITELIST
insert into RecvPackages_purged select * from RecvPackages where string in (select name from PackagesWhitelist where status = 0);
delete from RecvPackages where string in (select name from PackagesWhitelist where status = 0);
delete from PackagesWhitelist where status=0;

commit;

# PURGE GENERIC EXTENSIONS AND INVALID NAMES
start transaction;
# GENERIC INVALID NAMES
delete from RecvPackages WHERE lower(string) not REGEXP '^[a-z0-9][a-z0-9_.+\-]+$';
# INVALID ENDED EXTENSIONS
delete from RecvPackages WHERE lower(string) REGEXP '[.](png|zip|jpg|php|txt|desktop|sql|sb2|ts|bz2|docbook|mo|iso|json|swf|xcf|md|egg-info|skm|js|html|bmp|svg|install|zero|dll|so|app|exe|gif|doc|cpp|h|css|java|xsl|xml|ui|ko|notebook|ogg|mp3|mp4|avi|mpg|c|pdf|o|ps|a|gz|bz|ini)$';
# INVALID STARTING NAMES
delete from RecvPackages WHERE lower(string) REGEXP '^(SMART_|Xvf|drivelist|geany_run)';
commit;

