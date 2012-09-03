---
title: Creating an SQL DB from world bank data 
date: 2012-08-17
---

I would advise anyone that is doing research/analysis to take a closer look at the 
[world bank indicators](http://data.worldbank.org/indicator/all).
They represent a very juicy subset of the [UNdata](http://data.un.org) 
from market captalization of all country's publics stock to number of PCs, to $ transfers from abroad, unemployment rate, number of people finishing university…. etc etc.
On top of World Bank makes the complete database easily available as an excel or set of csv files - contrary to the UNdata which opts to keep the database "hidden" and exposes only an exploring interface (there is just one [third party service](http://www.undata-api.org) that offers a restricted API to UNdata ).

From my side - I always was in need of some slice of that database - but everytime it wasn't worth the trouble to get the data in my own database in a way that I can query/filter/display as I want.

That is, I haven't had time until last week.

Here is a query that shows some of the data:

<pre>
    create temp view wdi_example as select
      bb."Country Name" as country,
      round(cast(bb."2010" as numeric)) as broadband_users,
      round(cast(internet."2010" as numeric)) as internet_users,
      round(cast(population."2010" as numeric)) as population
    from
      wdi.data bb,
      wdi.data internet,
      wdi.data population
    where
      bb."Country Name" = internet."Country Name"
      and bb."Country Name" = population."Country Name"
      and bb."Indicator Code" = 'IT.NET.BBND'
      and internet."Indicator Code" = 'IT.NET.USER'
      and population."Indicator Code" = 'SP.POP.TOTL'
    order by population desc
    ;
    odw=> select * from wdi_example order by population desc;

                       country                     | broadband_users | internet_users | population 
    -----------------------------------------------+-----------------+----------------+------------
    Not classified                                 |                 |                |           
    World                                          |       529552633 |     2038625951 | 6894377794
    Low + middle income                            |       231326829 |     1211559964 | 5766461466
    Middle income                                  |       230963174 |     1171514374 | 4966657601
    Lower middle income                            |        26129949 |      334184408 | 2494159560
    Upper middle income                            |       204833225 |      837329966 | 2472498041
    East Asia + Pacific (all income levels)        |       205613769 |      749045994 | 2201613485
    East Asia + Pacific (developing only)          |       139030021 |      563285528 | 1961101773
    South Asia                                     |        11893861 |      132800217 | 1632939098
    China                                          |       126337000 |      460077957 | 1337825000
    OECD members                                   |       304879562 |      844430192 | 1237234841
    India                                          |        10990000 |       91846075 | 1224614327
    High income                                    |       298225804 |      827065987 | 1127916328
    High income: OECD                              |       284686258 |      772541200 | 1033945781
    Europe + Central Asia (all income levels)      |       167104549 |      512371917 |  891039428
    Sub-Saharan Africa (all income levels)         |         1477152 |       89458998 |  853931672
    Sub-Saharan Africa (developing only)           |         1475966 |       89416974 |  853231271
    Least developed countries: UN classification   |          699160 |       35242769 |  825210584
    Low income                                     |          363655 |       40045590 |  799803865
    Heavily indebted poor countries (HIPC)         |          679731 |       28981478 |  620267812
    Latin America + Caribbean (all income levels)  |        38534602 |      200827202 |  588757676
    Latin America + Caribbean (developing only)    |        37695393 |      198016893 |  582501932
    European Union                                 |       130004397 |      355546517 |  502302566
    Europe + Central Asia (developing only)        |        36772909 |      158676575 |  405670230
    Middle East + North Africa (all income levels) |         9026704 |       96625274 |  382556328
    Arab World                                     |         6716509 |       81902398 |  347672135
    North America                                  |        95901996 |      257496348 |  343540107
    Euro area                                      |        91720222 |      236149428 |  331943805
    Middle East + North Africa (developing only)   |         4458679 |       69363777 |  331017162
    United States                                  |        85723155 |      229684122 |  309349689
    Indonesia                                      |         1900300 |       23747223 |  239870937
    Brazil                                         |        13266310 |       79245740 |  194946470
    Pakistan                                       |          531787 |       29128970 |  173593383
    Nigeria                                        |           99108 |       45039711 |  158423182
    Bangladesh                                     |           60000 |        5501609 |  148692131
    Russian Federation                             |        15700000 |       61472011 |  141920000
    Japan                                          |        34044729 |       98951089 |  127450459
    Mexico                                         |        11325022 |       35217856 |  113423047

</pre>

Note that the data includes as countries certain useful aggregations like "middle income", or "world" - that are not countries themselves.

Also note that the DB is in "attribute-value" form, ie you won't find a very wide table with one row per country and a column per indicator  (there are too many indicators for that), but instead you will find a row for each country/indicator combination (250 country rows x 1200 indicators = approximately 300K rows in the main Data table). 
This gets futrher complicated by the fact that each record contains a column for each of the years - ranging from the 70s to now. All this extra inforation could be used for historical trend analysis but it makes things harder if you just want to get the most recent value of the indicator by country - thats what I typically need for example - a country population or similar country metrics.
On top of that not all indicators are available for all countries and even in the case they are not all countries make the indicators available in all years.

In the example above I made things simpler by just going a couple years back (2010) to make sure that I can definitely find the indicator - still in general the simplistic join query that I have above needs to be replaced with an outer join query instead.

There is a country/series table that includes among some other information which is the most recent year that the indicator is available for the particular country. I haven't checked it but ideally the query should consult first that table and use that to fish the right value from the data table to produce the most recent value of an inducator for a particular country.

At some point me or someone else should probably create flattend views that perform the logic described above and expose one such view for each subsection of the world data indicators (e.g. "Agriculture & Rural Development", "Aid Effectiveness", "Climate Change", "Economic Policy & External Debt" etc...  (a single flattened view would be too much even for postgres)

I uploaded two of the small tables ([Series](https://docs.google.com/spreadsheet/ccc?key=0AuEZc8NNSRlzdE5ZcTlkYnNyWUdmRXc4T214czlrZWc) - 1200 rows and [Countries](https://docs.google.com/spreadsheet/ccc?key=0AuEZc8NNSRlzdExya1Z4RzhiTVlPVU52R3dRWkJyNmc) - 250 rows to google so you can easily take a look at these datasets as google spreadsheets.

To find the code for each indicator you want you can go to the [worldbank site](http://data.worldbank.org/indicator/all) search for the indicator you want (e.g. Population), as you can see there are many options, e.g. Urban Population etc. In our case our indicator is called "Population, total", click on it and you will the code as the last part of the URL : http://data.worldbank.org/indicator/SP.POP.TOTL, ie the code is SP.POP.TOTL  . 

As for countries (ie to join these data with your country column) this are a bit messier there - not due to world bank's faults but because every application I know uses a slightly different convention for coding countries. The countries table has several of those (2-letter-code, 3-letter-code, short name, long name, table name etc etc...). In the event that the "Country Name" that is included in the Data table doesn't suit you, you should be able to join back with the Countries table and gert from the key column that better fits whatever you are using as your country key/code/name.


Again, I may be restating the obvious here, If you want to use multiple indicators in your query, you will need to do a join for each indicator..  Non ideal but necessary - thats why I created a temp view in the example above to make the query more readable
Here is the process to update it with a fresh version of the WDI data - probably you should do that yearly

<pre>

    > # zip file contains csvs at top level, so we need to put things ourselves in a directory
    > mkdir /tmp/wdi; cd /tmp/wdi
    > # -O creates the file use the url's last part as name
    > curl -O http://databank.worldbank.org/databank/download/WDIandGDF_csv.zip
    > unzip WDIandGDF_csv.zip
    > for f in *.csv
    > do 
    >   # take out the name prefix from the csv files - we will rely on the file names for table names
    >   oldf=f
    >   f=`echo $oldf|sed 's/WDI_GDF_//'`
    >   mv $oldf $f
    > done
</pre>

At this point you have a directory with csv files whose names are appropriate to be used as table names and you can follow the instructions
about how to create an SQL DB from a set of CSV files given at my earlier [post](2012-08-15-creating-sql-db-from-csv-files.html)

