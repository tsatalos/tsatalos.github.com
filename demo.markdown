---
title: This will be used as the title-tag of the page head
---

We added the World Bank "World Development Indicators" 
from [here](http://data.worldbank.org/indicator/all)  in the data warehouse under schema : wdi

( I would advise anyone that is doing research/analysis to take a closer look at the indicators above - its quite an unbelievable trove of information. from market cap of country's stock to number of PCs, to $ transfers from abroad, unemployment rate, number of people finishing university…. etc etc

The data could be used for anything from understanding trends, forecasting growth, or interesting blog posts.

Here is a query that shows some of the data:

<pre>
    select
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
    ------------------------------------------------+-----------------+----------------+------------
     Not classified                                 |                 |                |           
     World                                          |       529552633 |     2038625951 | 6894377794
     Low & middle income                            |       231326829 |     1211559964 | 5766461466
     Middle income                                  |       230963174 |     1171514374 | 4966657601
     Lower middle income                            |        26129949 |      334184408 | 2494159560
     Upper middle income                            |       204833225 |      837329966 | 2472498041
     East Asia & Pacific (all income levels)        |       205613769 |      749045994 | 2201613485
     East Asia & Pacific (developing only)          |       139030021 |      563285528 | 1961101773
     South Asia                                     |        11893861 |      132800217 | 1632939098
     China                                          |       126337000 |      460077957 | 1337825000
     OECD members                                   |       304879562 |      844430192 | 1237234841
     India                                          |        10990000 |       91846075 | 1224614327
     High income                                    |       298225804 |      827065987 | 1127916328
     High income: OECD                              |       284686258 |      772541200 | 1033945781
     Europe & Central Asia (all income levels)      |       167104549 |      512371917 |  891039428
     Sub-Saharan Africa (all income levels)         |         1477152 |       89458998 |  853931672
     Sub-Saharan Africa (developing only)           |         1475966 |       89416974 |  853231271
     Least developed countries: UN classification   |          699160 |       35242769 |  825210584
     Low income                                     |          363655 |       40045590 |  799803865
     Heavily indebted poor countries (HIPC)         |          679731 |       28981478 |  620267812
     Latin America & Caribbean (all income levels)  |        38534602 |      200827202 |  588757676
     Latin America & Caribbean (developing only)    |        37695393 |      198016893 |  582501932
     European Union                                 |       130004397 |      355546517 |  502302566
     Europe & Central Asia (developing only)        |        36772909 |      158676575 |  405670230
     Middle East & North Africa (all income levels) |         9026704 |       96625274 |  382556328
     Arab World                                     |         6716509 |       81902398 |  347672135
     North America                                  |        95901996 |      257496348 |  343540107
     Euro area                                      |        91720222 |      236149428 |  331943805
     Middle East & North Africa (developing only)   |         4458679 |       69363777 |  331017162
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

The metadata (i.e. the list of series, countries together with their description) is also viewable here [Countries](https://docs.google.com/a/odesk.com/spreadsheet/ccc?key=0Asr9ZuzplUMbdDktbVBhODFYWEM4VFl1TFRxNkhYSVE#gid=0) , [Series](https://docs.google.com/a/odesk.com/spreadsheet/ccc?key=0Asr9ZuzplUMbdHJvRkVTRkY4OTNibmZac0dWWGhlaWc#gid=0)
In general, you would open up the series spreadsheet or the world bank url mentioned in the beginning search to find based on the description the relevant indicator find its code (in the web page the code is in the link) and then issue the query like above.

If you want to use multiple indicators the structure of the file will force you to do a join for each indicator..  Non ideal but necessary - thats why I created a temp view in the example above to make the query more readable
Here is the process to update it with a fresh version of the WDI data - probably we would do that yearly

<pre>

    > mkdir /tmp/wdi; cd /tmp/wdi
    > curl -O http://databank.worldbank.org/databank/download/WDIandGDF_csv.zip
    > unzip WDIandGDF_csv.zip
    > for f in *.csv
    > do 
      oldf=f
      f=`echo $oldf|sed 's/WDI_GDF_//'`
      mv $oldf $f
      python ~/scripts/csv_db_import.py -r 0 -c -x -D odw -U ... -p ... -s wdi -V 12000 -H dbs16 $f
      ff=`basename $f .csv`
      nl=$'\n'
      echo "set client_encoding to 'latin1';$nl \copy wdi.$ff from '$f' CSV HEADER;" |psql -h dbs16 -p 12000  -U odw -d odw -f - 
    done

</pre>

Scripts used

<pre>
    csv_db_import.py from http://furius.ca/pubcode/pub/conf/bin/csv-db-import.html   #slightly modified to allow for schema setting/create table stmt only
</pre>

