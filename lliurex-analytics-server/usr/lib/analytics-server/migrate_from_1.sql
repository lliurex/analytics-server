start transaction;

rename table analytics.clients to analytics.clients_bkp;
rename table analytics.historico to analytics.historico_bkp;
rename table analytics.packages to analytics.packages_bkp;

commit;

source /usr/lib/analytics-server/analytics2.sql;

start transaction;

insert into analytics.Client_Versions select CONV(SUBSTRING(CAST(SHA(CONCAT(month(lastlogin),'-',year(lastlogin),'-',user,'-',version,'-',sabor)) AS CHAR), 1, 16), 16, 10) as uuid,user as Client_uid,'15' as Releases_name, 'desktop' as Flavours_name,date(lastlogin) as date,version as string_release,sabor as string_flavour from analytics.clients_bkp where version like '15%' and sabor != 'dummy' and (sabor not like '%server%' and sabor not like '%client%' and sabor like '%desktop%') on duplicate key update uuid=values(uuid);
delete from analytics.clients_bkp where version like '15%' and sabor != 'dummy' and (sabor not like '%server%' and sabor not like '%client%' and sabor like '%desktop%');
insert into analytics.Client_Versions select CONV(SUBSTRING(CAST(SHA(CONCAT(month(lastlogin),'-',year(lastlogin),'-',user,'-',version,'-',sabor)) AS CHAR), 1, 16), 16, 10) as uuid,user as Client_uid,'15' as Releases_name, 'server' as Flavours_name,date(lastlogin) as date,version as string_release,sabor as string_flavour from analytics.clients_bkp where version like '15%' and sabor != 'dummy' and (sabor like '%server%') on duplicate key update uuid=values(uuid);
delete from analytics.clients_bkp where version like '15%' and sabor != 'dummy' and (sabor like '%server%');
insert into analytics.Client_Versions select CONV(SUBSTRING(CAST(SHA(CONCAT(month(lastlogin),'-',year(lastlogin),'-',user,'-',version,'-',sabor)) AS CHAR), 1, 16), 16, 10) as uuid,user as Client_uid,'15' as Releases_name, 'client' as Flavours_name,date(lastlogin) as date,version as string_release,sabor as string_flavour from analytics.clients_bkp where version like '15%' and sabor != 'dummy' and (sabor like '%client%') on duplicate key update uuid=values(uuid);
delete from analytics.clients_bkp where version like '15%' and sabor != 'dummy' and (sabor like '%client%');
insert into analytics.Client_Versions select CONV(SUBSTRING(CAST(SHA(CONCAT(month(lastlogin),'-',year(lastlogin),'-',user,'-',version,'-',sabor)) AS CHAR), 1, 16), 16, 10) as uuid,user as Client_uid,'16' as Releases_name, 'desktop' as Flavours_name,date(lastlogin) as date,version as string_release,sabor as string_flavour from analytics.clients_bkp where version like '16%' and sabor != 'dummy' and (sabor like '%desktop%') on duplicate key update uuid=values(uuid);
delete from analytics.clients_bkp where version like '16%' and sabor != 'dummy' and (sabor like '%desktop%');
insert into analytics.Client_Versions select CONV(SUBSTRING(CAST(SHA(CONCAT(month(lastlogin),'-',year(lastlogin),'-',user,'-',version,'-',sabor)) AS CHAR), 1, 16), 16, 10) as uuid,user as Client_uid,'16' as Releases_name, 'server' as Flavours_name,date(lastlogin) as date,version as string_release,sabor as string_flavour from analytics.clients_bkp where version like '16%' and sabor != 'dummy' and (sabor like '%server%') on duplicate key update uuid=values(uuid);
delete from analytics.clients_bkp where version like '16%' and sabor != 'dummy' and (sabor like '%server%');
insert into analytics.Client_Versions select CONV(SUBSTRING(CAST(SHA(CONCAT(month(lastlogin),'-',year(lastlogin),'-',user,'-',version,'-',sabor)) AS CHAR), 1, 16), 16, 10) as uuid,user as Client_uid,'16' as Releases_name, 'client' as Flavours_name,date(lastlogin) as date,version as string_release,sabor as string_flavour from analytics.clients_bkp where version like '16%' and sabor != 'dummy' and (sabor like '%client%') on duplicate key update uuid=values(uuid);
delete from analytics.clients_bkp where version like '16%' and sabor != 'dummy' and (sabor like '%client%');
insert into analytics.Client_Versions select CONV(SUBSTRING(CAST(SHA(CONCAT(month(lastlogin),'-',year(lastlogin),'-',user,'-',version,'-',sabor)) AS CHAR), 1, 16), 16, 10) as uuid,user as Client_uid,'15' as Releases_name, 'other' as Flavours_name,date(lastlogin) as date,version as string_release,sabor as string_flavour from analytics.clients_bkp where version like '15%' and sabor != 'dummy' on duplicate key update uuid=values(uuid);
delete from analytics.clients_bkp where version like '15%' and sabor != 'dummy';
insert into analytics.Client_Versions select CONV(SUBSTRING(CAST(SHA(CONCAT(month(lastlogin),'-',year(lastlogin),'-',user,'-',version,'-',sabor)) AS CHAR), 1, 16), 16, 10) as uuid,user as Client_uid,'16' as Releases_name, 'other' as Flavours_name,date(lastlogin) as date,version as string_release,sabor as string_flavour from analytics.clients_bkp where version like '16%' and sabor != 'dummy' on duplicate key update uuid=values(uuid);
delete from analytics.clients_bkp where version like '16%' and sabor != 'dummy';

insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(fecha),'-',year(fecha),'-15-desktop-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,fecha as date,'15' as Releases_name,'desktop' as Flavours_name,sum(count) as count from analytics.historico_bkp where app != 'dummy' and version like '15%' and (sabor not like '%server%' and sabor not like '%client%' and sabor like '%desktop%') and app != '' group by year(fecha),month(fecha),app on duplicate key update uuid=values(uuid);
delete from analytics.historico_bkp where app != 'dummy' and version like '15%' and (sabor not like '%server%' and sabor not like '%client%' and sabor like '%desktop%') and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(fecha),'-',year(fecha),'-15-server-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,fecha as date,'15' as Releases_name,'server' as Flavours_name,sum(count) as count from analytics.historico_bkp where app != 'dummy' and version like '15%' and sabor like '%server%' and app != '' group by year(fecha),month(fecha),app on duplicate key update uuid=values(uuid);
delete from analytics.historico_bkp where app != 'dummy' and version like '15%' and sabor like '%server%' and app != ''; 
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(fecha),'-',year(fecha),'-15-client-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,fecha as date,'15' as Releases_name,'client' as Flavours_name,sum(count) as count from analytics.historico_bkp where app != 'dummy' and version like '15%' and sabor like '%client%' and app != '' group by year(fecha),month(fecha),app on duplicate key update uuid=values(uuid);
delete from analytics.historico_bkp where app != 'dummy' and version like '15%' and sabor like '%client%' and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(fecha),'-',year(fecha),'-16-server-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,fecha as date,'16' as Releases_name,'server' as Flavours_name,sum(count) as count from analytics.historico_bkp where app != 'dummy' and version like '16%' and sabor like '%server%' and app != '' group by year(fecha),month(fecha),app on duplicate key update uuid=values(uuid);
delete from analytics.historico_bkp where app != 'dummy' and version like '16%' and sabor like '%server%' and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(fecha),'-',year(fecha),'-16-client-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,fecha as date,'16' as Releases_name,'client' as Flavours_name,sum(count) as count from analytics.historico_bkp where app != 'dummy' and version like '16%' and sabor like '%client%' and app != '' group by year(fecha),month(fecha),app on duplicate key update uuid=values(uuid);
delete from analytics.historico_bkp where app != 'dummy' and version like '16%' and sabor like '%client%' and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(fecha),'-',year(fecha),'-16-desktop-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,fecha as date,'16' as Releases_name,'desktop' as Flavours_name,sum(count) as count from analytics.historico_bkp where app != 'dummy' and version like '16%' and sabor like '%desktop%' and app != '' group by year(fecha),month(fecha),app on duplicate key update uuid=values(uuid);
delete from analytics.historico_bkp where app != 'dummy' and version like '16%' and sabor like '%desktop%' and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(fecha),'-',year(fecha),'-15-other-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,fecha as date,'15' as Releases_name,'other' as Flavours_name,sum(count) as count from analytics.historico_bkp where app != 'dummy' and version like '16%' and sabor like '%desktop%' and app != '' group by year(fecha),month(fecha),app on duplicate key update uuid=values(uuid);
delete from analytics.historico_bkp where app != 'dummy' and version like '15%' and app != '' ;
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(fecha),'-',year(fecha),'-16-other-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,fecha as date,'16' as Releases_name,'other' as Flavours_name,sum(count) as count from analytics.historico_bkp where app != 'dummy' and version like '16%' and sabor like '%desktop%' and app != '' group by year(fecha),month(fecha),app on duplicate key update uuid=values(uuid);
delete from analytics.historico_bkp where app != 'dummy' and version like '16%' and app != '';

insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(date(now())),'-',year(date(now())),'-15-desktop-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,date(now()) as date,'15' as Releases_name,'desktop' as Flavours_name,sum(count) as count from analytics.packages_bkp where app != 'dummy' and version like '15%' and (sabor not like '%server%' and sabor not like '%client%' and sabor like '%desktop%') and app != '' group by year(date(now())),month(date(now())),app on duplicate key update uuid=values(uuid);
delete from analytics.packages_bkp where app != 'dummy' and version like '15%' and (sabor not like '%server%' and sabor not like '%client%' and sabor like '%desktop%') and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(date(now())),'-',year(date(now())),'-15-server-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,date(now()) as date,'15' as Releases_name,'server' as Flavours_name,sum(count) as count from analytics.packages_bkp where app != 'dummy' and version like '15%' and sabor like '%server%' and app != '' group by year(date(now())),month(date(now())),app on duplicate key update uuid=values(uuid);
delete from analytics.packages_bkp where app != 'dummy' and version like '15%' and sabor like '%server%' and app != ''; 
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(date(now())),'-',year(date(now())),'-15-client-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,date(now()) as date,'15' as Releases_name,'client' as Flavours_name,sum(count) as count from analytics.packages_bkp where app != 'dummy' and version like '15%' and sabor like '%client%' and app != '' group by year(date(now())),month(date(now())),app on duplicate key update uuid=values(uuid);
delete from analytics.packages_bkp where app != 'dummy' and version like '15%' and sabor like '%client%' and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(date(now())),'-',year(date(now())),'-16-server-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,date(now()) as date,'16' as Releases_name,'server' as Flavours_name,sum(count) as count from analytics.packages_bkp where app != 'dummy' and version like '16%' and sabor like '%server%' and app != '' group by year(date(now())),month(date(now())),app on duplicate key update uuid=values(uuid);
delete from analytics.packages_bkp where app != 'dummy' and version like '16%' and sabor like '%server%' and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(date(now())),'-',year(date(now())),'-16-client-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,date(now()) as date,'16' as Releases_name,'client' as Flavours_name,sum(count) as count from analytics.packages_bkp where app != 'dummy' and version like '16%' and sabor like '%client%' and app != '' group by year(date(now())),month(date(now())),app on duplicate key update uuid=values(uuid);
delete from analytics.packages_bkp where app != 'dummy' and version like '16%' and sabor like '%client%' and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(date(now())),'-',year(date(now())),'-16-desktop-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,date(now()) as date,'16' as Releases_name,'desktop' as Flavours_name,sum(count) as count from analytics.packages_bkp where app != 'dummy' and version like '16%' and sabor like '%desktop%' and app != '' group by year(date(now())),month(date(now())),app on duplicate key update uuid=values(uuid);
delete from analytics.packages_bkp where app != 'dummy' and version like '16%' and sabor like '%desktop%' and app != '';
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(date(now())),'-',year(date(now())),'-15-other-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,date(now()) as date,'15' as Releases_name,'other' as Flavours_name,sum(count) as count from analytics.packages_bkp where app != 'dummy' and version like '16%' and sabor like '%desktop%' and app != '' group by year(date(now())),month(date(now())),app on duplicate key update uuid=values(uuid);
delete from analytics.packages_bkp where app != 'dummy' and version like '15%' and app != '' ;
insert into analytics.RecvPackages select CONV(SUBSTRING(CAST(SHA(CONCAT(month(date(now())),'-',year(date(now())),'-16-other-',app)) AS CHAR), 1, 16), 16, 10) as uuid,app as string,date(now()) as date,'16' as Releases_name,'other' as Flavours_name,sum(count) as count from analytics.packages_bkp where app != 'dummy' and version like '16%' and sabor like '%desktop%' and app != '' group by year(date(now())),month(date(now())),app on duplicate key update uuid=values(uuid);
delete from analytics.packages_bkp where app != 'dummy' and version like '16%' and app != '';

commit;

start transaction;

drop table analytics.clients_bkp;
drop table analytics.historico_bkp;
drop table analytics.packages_bkp;

commit;