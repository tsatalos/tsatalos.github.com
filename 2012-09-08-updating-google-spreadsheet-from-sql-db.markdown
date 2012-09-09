---
title: Updating a google spreadsheet from an sql and an experience in code microtasking
date: 2012-09-01
---

A common problem I have is getting the output of my queries to google spreadsheets.
So I had an odesk contractor create a python script for me that does exactly that:

It gets as input 
* database connection information
* a query
* a pointer to a google spreadsheet

and it goes ahead executes the query fetches the data and "pastes" them on the google spreadsheet.

Here is the [job post](https://www.odesk.com/jobs/Small-python-program-that-uses-google-spreadsheet-api_~~ffec771ecb20b4bb)
I created. I actually gave the task as a $10 task to 3 people that applied to my job (3 out of 4 candidates)

From the time that I sat to post the job to the time I had the solution to my hands ... approximately 18 hours. I invested approximately 2+ hours or my own time
in creating the job in varoious marketplaces as well as helping the candidate. I did try rentacoder/vworker ([here](http://www.vworker.com/RentACoder/misc/BidRequests/ShowBidRequest.asp?lngBidRequestId=1960405) is the post
and closed the job after 24 hours with no bids, freelancer - where I was denied the opportunity to post the job because it was under the $30 minimum, and peopleperhour where I was denied because
I was below the minimum $50 budget.

Here is the [script file](db2google.py) produced by the contractor called [Yuan](https://www.odesk.com/users/~0176b4c06b81285630?sid=28001)

<pre>
#!/usr/bin/python
#Tested on Python 2.6
#Dependencies:
#Google Data Api for Python. Available @ http://pypi.python.org/pypi/gdata
#psycopg2. Available @ http://www.initd.org/psycopg/download
#MySQLdb. Availabe @ http://mysql-python.sourceforge.net

import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service

DATABASE = 'mysql' # currently support postgresql or mysql
dbhost = '127.0.0.1'
dbport = 3306
dbname = 'mytestdb'
dbuser = 'user'
dbpassword = 'pass'
dbquery = 'select * from places;'

google_user = 'some_user@gmail.com'
google_passwd = "1234thisisnotapass"
spreadsheet_key = '0At_gOKJHHGFDHGFJHGKJHLJLKJLJLKJLKJKHeEVIVHc'
worksheet_name = 'Test1'
where_row = 6
where_col = 2

if DATABASE == 'postgresql':
    import psycopg2
    print "Connecting to postgresql database ..."
    conn = psycopg2.connect(host=dbhost, port=dbport, database=dbname,
     user=dbuser, password=dbpassword)
elif DATABASE == 'mysql':
    import MySQLdb
    print "Connecting to mysql database ..."
    conn = MySQLdb.connect(host=dbhost, port=dbport, db=dbname, user=dbuser,
     passwd=dbpassword)


cur = conn.cursor()
print "Connected!"
print "Retrieving data ..."
cur.execute(dbquery)
data = list(cur.fetchall())
data.insert(0, tuple([_[0] for _ in cur.description]))
data = tuple(data)
print "Data successfully fetched!"

print "Connecting to google spreadsheet ..."
gd_client = gdata.spreadsheet.service.SpreadsheetsService()
gd_client.email = google_user
gd_client.password = google_passwd
gd_client.ProgrammaticLogin()
q = gdata.spreadsheet.service.DocumentQuery()
q.title = worksheet_name
feed = gd_client.GetWorksheetsFeed(spreadsheet_key, query=q)
worksheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
print "Connected!"

print "Writing data to Google Spreadsheet ..."
rownum = where_row
for line in data:
    colnum = where_col
    for cell in line:
	gd_client.UpdateCell(row=rownum, col=colnum, inputValue=str(cell), 
	 key=spreadsheet_key, wksht_id=worksheet_id)
	colnum += 1
    rownum += 1
print "Done!"
</pre>
