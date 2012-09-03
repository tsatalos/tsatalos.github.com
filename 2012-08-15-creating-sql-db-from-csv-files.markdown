---
title: Creating an SQL DB from csv files
date: 2012-09-01
---
I captured in this post a quick way to go from a set of CSV files to a Database. The idea is that I should be able within a couple commands to get a mysql db with the right schema (tables, fields, types) fully populated with the data from csv files.

The instructions follow:


You will need to replace all occurrences of 

* `$DATADIR` the directory with the csv files
* `$DBHOSTNAME` optional
* `$DBPORT` optional
* `$PASSWORD` optional
* `$USERNAME` set it to root for development use
* `$DBNAME` the database name
* `$SCRIPTDIR` the directory where csv_db_import is located
* `$SCHEMA` do not use for mysql - for postgres you can use it to avoid putting tables at top level

with your own

<pre>
    > cd $DATADIR
    > ls
./         ../        employees.csv   departments.csv  
    >


    > for f in *.csv
    > do
    > # some option explanations here : -r 0 asks to read all rows to determine type,
    > # -c asks to use first row as header, -x asks to only create the tables and not import the data (ot addition) 
    > # -s schema to be used within db o/w at top level (ot  addition)
    >   $SCRIPTDIR/csv_db_import.py -r 0 -c -x -D $DBNAME -U $USERNAME -p $PASSWORD -s $SCHEMA -V $DBPORT -H $DBHOSTNAME $f
    >   ff=`basename $f .csv`
    >   # --------------------
    >   # if postgresql
    >   nl=$'\n'
    >   # had to change the client encoding some of the footnotes use accented chars and cause postgres errors otherwise
    >   # I use the \copy instead of the sql copy because the later has user restrictions
    >   # need to create ~/.pgpass with a row  dbhostname:dbport:dbname:username:password to avoid getting interactively asked for pass
    >   echo "set client_encoding to 'latin1';$nl \copy $SCHEMA.$ff from '$f' CSV HEADER;" |psql -h $DBHOSTNAME -p $DBPORT  -U $USERNAME -d $DBNAME -f -
    >   # --------------------
    >   # if mysql (latin1 is the default char set for mysql - no need to set it) - don't know how to use schemas in mysql so no schema parameter
    >   mysql -h $DBHOSTNAME -P $DBPORT -u $USERNAME -p $PASSWORD -e "load data infile '$f' into table $ff" $DBNAME
    > done
</pre>



I am using a script I found that produces the create table stmt automatically from the csv header and the subsequent column width/value types... It does a pretty good job. I am not using the scripts own capability for data import because it fails for "large" data sets like the ones we have - plus it takes very long - one insert per line... the copy stmt is much much faster.

<pre>
    csv_db_import.py from http://furius.ca/pubcode/pub/conf/bin/csv-db-import.html   #slightly modified to allow for schema setting/create table stmt only
</pre>

