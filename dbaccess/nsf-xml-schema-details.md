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


  Award (sequence):
    AwardTitle (string):
    AwardEffectiveDate (dateTime):
    AwardExpirationDate (dateTime):
    AwardAmount (int):
    AwardInstrument (sequence):
      Value (string):
    Organization (sequence):
      Code (int):
      Directorate (sequence):
        LongName (string):
      Division (sequence):
        LongName (string):
    ProgramOfficer (sequence)
      SignBlockName (string):
    AbstractNarration (string):
    MinAmdLetterDate (dateTime):
    MaxAmdLetterDate (dateTime):
    ARRAAmount (string):
    AwardID (int):
    Investigator (sequence):
      FirstName (string):
      LastName (string):
      EmailAddress (string):
      StartDate (dateTime):
      EndDate (dateTime):
      RoleCode (int):
    Institution (sequence):
      Name (string):
      CityName (string):
      ZipCode (int):
      PhoneNumber (decimal):
      StreetAddress (string):
      CountryName (string):
      StateName (string):
      StateCode (string):
    FoaInformation (sequence):
      Code (int):
      Name (string):
    ProgramElement (sequence):
      Code (int):
      Text (string):
    ProgramReference (sequence):
      Code (int):
      Text (string):
