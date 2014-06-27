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

## XML Schema Breakdown

Each year is downloaded as a zip file and is named using the year: `<year>.zip`.
Each zip file contains a bunch of XML files, each containing info for exactly one
award. These files are named using the award ID: `<awardID>.xml`. Each XML file has
a `rootTag>`, followed by an `<Award>` tag which contains the following elements:

1.  **AwardID** (int): The unique ID of the award.

2.  **AwardTitle** (string): The title of the award.
3.  **AbstractNarration** (string): An overview of what the research is seeking
        to do.

4.  **AwardEffectiveDate** (dateTime): The date the award funding starts.
5.  **AwardExpirationDate** (dateTime): The date the award funding ends.

6.  **MinAmdLetterDate** (dateTime): The first date the award was amended.
7.  **MaxAmdLetterDate** (dateTime): The last date the award was amended.

8.  **AwardAmount** (int): The amount of money awarded to date.
9.  **ARRAAmount** (string): Portion of AwardAmount funded by the American
        Recovery and Reinvestment Act (ARRA).

10. **AwardInstrument** (sequence): Listing of classifications for this award.
    1.  **Value_ (string): A particular classification** (e.g. "Standard Grant",
        "Cooperative Agreement", "Contract").

11. **Organization** (sequence): The NSF organization(s) funding the grant.
    1.  **Code** (int): Unique ID of the organization funding this award.
            DIRECTORE, DIVISON, or COMBO?
    2.  **Directorate** (sequence): Listing of directorates funding this award.
        1.  **LongName** (string): Name of directorate.
    3.  **Division** (sequence): Listing of divisions funding this award.
        1.  **LongName** (string): Name of division.

12. **ProgramElement** (sequence): Listing of programs funding this award.
    1.  **Code** (int): Unique ID of the program.
    2.  **Text** (string): Name of the program.

13. **ProgramReference** (sequence): Listing of programs related to the one funding this award.
    1.  **Code** (int): Unique ID of the program referenced.
    2.  **Text** (string): Name of the program referenced.

14. **ProgramOfficer** (sequence): A listing of all Program Officers responsible for this award.
    1.  **SignBlockName** (string): The name of the Program Officer.

15. **Investigator** (sequence): A listing of all investigators who have worked on or are working on this award.
    1.  **FirstName** (string): The first name of the investigator.
    2.  **LastName** (string): The last name of the investigator.
    3.  **EmailAddress (string): The email address of the investigator** (optional).
    4.  **StartDate** (dateTime): The date the investigator started working on this award.
    5.  **EndDate** (dateTime): The date the investigator stopped working on this award.
    6.  **RoleCode** (int): The role of the investigator, identified by an integer code.
            Either "Principal Investigator" or "Co-Principal Investigator".

16. **Institution** (sequence): The institution sponsoring this award (PO/Investigator affiliation).
    1.  **Name** (string): Name of the institution.
    2.  **PhoneNumber** (decimal): Phone number of the institution.
    3.  **CityName** (string): Name of the city where the institution is located.
    4.  **StreetAddress** (string): Name of the street on which the institution is located.
    5.  **StateCode** (string): The
    6.  **StateName** (string): Name of the state in which the institution is located.
    7.  **ZipCode** (int): Zip code of the institution's postal address.
    8.  **CountryName** (string): Name of the country in which the institution is located.

17. **FoaInformation** (sequence): Funding Opportunity Anouncement (FOA) reference (to Grants.gov FOA listing).
    1.  **Code** (int): Unique ID of FOA.
    2.  **Name** (string): Name of FOA.
