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
The code is at the bottom of this post as well as a link to the script if you want to use it.

For anyone interested to hear about how this code micro-tasking effort worked out, read on.

* At 4pm Friday, I sat to convert my own notes to a $10 fixed price job post - the job was posted by 4:30pm.  Here is the [job post](https://www.odesk.com/jobs/Small-python-program-that-uses-google-spreadsheet-api_~~ffec771ecb20b4bb)
I created. 

* By 6pm Friday I had gone through all the markeplaces that advertise themselves that they focus on small projects - fiverr, vworker, freelancer and peopleperhour.

  - fiverr it has a functionality to allow a buyer to suggest a service - but that is targeting generic services not specific jobs
  - freelncer after putting the job together I was denied the opportunity to post - there is a $30 minimum
  - peopleperhour - similarly to freelancer minimum $50 budget
  - vworker - very non-obvious interface - I posted the job eventually the job stayed hidden for another 8-9hrs (I was a new account...) - i closed the job after 20 hrs with no bids.
[Here](http://www.vworker.com/RentACoder/misc/BidRequests/ShowBidRequest.asp?lngBidRequestId=1960405)  is that job post

* By 4am Saturday I had received 4 applicants all practically new to odesk but with tests - and all appearing python comfortable  (couldn't find the actual time they applied)
* By 8:30am Saturday (when I woke up) I hired three out of four applicants and closed the job. No interviewing just a quick look at what they told me in the message center - and how confident they looked about doing the job.
* By 9:00 am Saturday I sent the following message to all the hires - explaining them the rules and asking them to connect with me on skype 

	Hi all and welcome, 

	I ended up hiring all three of you - you can consider this as a "paid test" - ie you will all be paid assuming that you will be able to deliver the answer by end of day Monday PST and get paid the offered amount , $10.
	With regards to one question that was asked - ie what is the DB, my first use of the script involves postgresql - but I would rather if you make the script so as it works for either postgresql or mysql.
	Also I would like that you work independently on this - ie I want three answers that were done without you talking with each other.
	My skypeid is tsatalos, please invite me and I will create a  skype chatroom where we can communicate more actively - we shouldnt need much communication for this :-) , but we would for subsequent tasks.
	Assuming things work out with each one of you I will pay you with a milestone payment and keep the assignment open - so as we don't need to recreate the contract for any subsequent tasks.
	Finally, just to set the expectations right, you shouldn't spend on this more time than what corresponds to the amount I pay you. In my view this is about a 30 minutes job to do it well and I assumed that a good python developer can earn an average of $20/hr in odesk.

	Nice to meet you all,

	odysseas

and left for a family thing, keeping an eye on skype to accept any incoming contact request.

* At 11:00am Saturday I resumed, connecting over skype with 2 of the hires, spending 30 mins explaining questions to the contractor from Ukraine - who after that took off (equiv to 10pm for him). I continued with the other contractor (US timezone)
answering questions and working on other stuff on parallel with the skype.
* At 2pm Saturday approximately after 2hrs of work from that candidate I got the first result. We proceeded in back and forths resolving problems with the delivable (not all types were handled correctly, misunderstandings (lack of headers, no handling of spreadsheet tabs  etc))
* At 3:30pm Saturday approximately 24 hours after I sat to do the original post and after approximately 4 hrs of my own time and 3-4 hrs of one contractor I had the first outcome I was looking for. ( [Contractor profile](https://www.odesk.com/users/~0176b4c06b81285630?sid=28001), [python script](sheet/db2google.py.txt))
* At 8:30am Sunday I had a brief exchange with the Ukranian contractor wher I reminded him of the deadline and resend a msg to the Russian contractor from whom I hadn't received any response yet
* At 1:30 pm Sunday without any prior contact, the russian contractor message-center-responded me (the job post deadline is Monday) with a zip file containing everything I have ever asked or meant but didn't ask for.
  - perfect use of the ideal python library (gspread) that makes dealing with google spreadsheet a joy.
  - full use of command line params - using the ideal command line library that provides default, help etc...
  - complete test suite with dataset for both mysql and postgresql
  - and never asked anything with regards my own time !
  - self contained with enclosed the gspread library.
  - total lines of code excluding the command line parsing function 20 of which 10 is doing logging - in case you chose the -verbose option!!
He gave me his skype contact only after he submitted his full answer!. ([Contractor profile](https://www.odesk.com/users/~018d29cf303df3dafd?sid=28001), [python script](sheet/sheet.py.txt), [mysql test](sheet/mysql_test.sql.txt), [pg test](sheet/pg_test.sql.txt), [readme](sheet/README.txt) )

Summary, I feel very happy and successful with each one of the contractors, in spite of the apparent inbalance between effort invested and return. The reason is that, 
* like always, I have now about 10 things I want to get done with the script for which I would have no time to actually do - while now, all I need to do is ask the contractor and he would gladly do them for me - its his own code - and by now he understands better what I mean/want etc.
* I have found at least one python developer whose skills significantly outmatch my own, whose interface is compatible with mine and thus requires minimal communication overhead and is at the price range that I can afford to pay
 
