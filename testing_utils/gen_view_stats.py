DISTROS=['15','16','19','21']
FLAVOURS=['desktop','server','client']
AGES=['0','1','2']
str1="(select Releases_name,Flavours_name,string,count from RecvPackages where year(date) = year(current_date - interval {} month) and month(date) = month(current_date - interval {} month) and Flavours_name = '{}' and Releases_name = '{}' order by count desc limit 10){}"
str2="(select Releases_name,Flavours_name,string,count from RecvPackages where year(date) = year(current_date - interval {} month) and month(date) = month(current_date - interval {} month) and Flavours_name = 'other' order by count desc limit 10){}"
res=[]
for age in AGES:
    for distro in DISTROS:
        for flavour in FLAVOURS:
            res.append(str1.format(age,age,flavour,distro,'{}_{}_{}'.format(age,distro,flavour)))
        res.append(str2.format(age,age,'{}_other'.format(age)))
    res = ' union all select * from '.join(res)
    res = 'select * from {};\n'.format(res)
    print('>>>> VIEW v_{}\n{}<<<<\n'.format(age,res))
    res = []