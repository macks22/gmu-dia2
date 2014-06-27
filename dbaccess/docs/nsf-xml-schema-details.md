## Overview

The raw award data is warehoused by the NSF and obtainable through the nsf.gov website,
[here](http://www.nsf.gov/awardsearch/download.jsp). There is also a RESTful endpoint which
can be used to download the data by year:

    http://www.nsf.gov/awardsearch/download?DownloadFileName=`2014`&All=true
  
Each file that is downloaded is a zipped XML file with a listing of all awards for that year.
So for instance, a POST request to the above URI will return a zipped XML file that contains
all the award data for the year 2014. The schema for the XML data can be seen
[here](http://www.nsf.gov/awardsearch/resources/Award.xsd). It will be elaborated upon below
in order to formulate ideas for and detail assumptions made when parsing the awards into a
cleaned form which will be stored in a SQL database. The goal of this effort is to produce a
high quality representation of the data with minimal redundancy and maximum clarity, while
ensuring the XML representation of the awards is interpreted correctly.


    Award (sequence): the top-level tag for each award; contains all information relevant to the award
        AwardID (int): The unique ID of the award.

        AwardTitle (string): The title of the award.
        AbstractNarration (string): An overview of what the research is seeking to do.

        AwardEffectiveDate (dateTime): The date the award funding starts.
        AwardExpirationDate (dateTime): The date the award funding ends.

        MinAmdLetterDate (dateTime): The first date the award was amended.
        MaxAmdLetterDate (dateTime): The last date the award was amended.

        AwardAmount (int): The amount of money awarded to date.
        ARRAAmount (string): The amount of the award funded by the American Recovery and Reinvestment Act (ARRA).

        AwardInstrument (sequence): Listing of classifications for this award.
            Value (string): A particular classification (e.g. "Standard Grant").

        Organization (sequence): The NSF organization(s) funding the grant.
            Code (int): 
            Directorate (sequence):
                LongName (string):
            Division (sequence):
                LongName (string):

        ProgramElement (sequence):
            Code (int):
            Text (string):

        ProgramReference (sequence):
            Code (int):
            Text (string):

        ProgramOfficer (sequence): A listing of all Program Officers responsible for this award.
            SignBlockName (string): The name of the Program Officer.

        Investigator (sequence): A listing of all investigators who have worked on or are working on this award.
            FirstName (string): The first name of the investigator.
            LastName (string): The last name of the investigator.
            EmailAddress (string): The email address of the investigator (optional).
            StartDate (dateTime): The date the investigator started working on this award.
            EndDate (dateTime): The date the investigator stopped working on this award.
            RoleCode (int): The role of the investigator, identified by an integer code.
                Either "Principal Investigator" or "Co-Principal Investigator.

        Institution (sequence): The institution sponsoring this award (PO/Investigator affiliation).
            Name (string): Name of the institution.
            PhoneNumber (decimal): Phone number of the institution.
            CityName (string): Name of the city where the institution is located.
            StreetAddress (string): Name of the street on which the institution is located.
            StateCode (string): The
            StateName (string): Name of the state in which the institution is located.
            ZipCode (int): Zip code of the institution's postal address.
            CountryName (string): Name of the country in which the institution is located.

        FoaInformation (sequence):
            Code (int):
            Name (string):
