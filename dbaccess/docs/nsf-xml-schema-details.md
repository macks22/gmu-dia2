## Overview

The raw award data is warehoused by the NSF and obtainable through the nsf.gov website,
[here](_http://www.nsf.gov/awardsearch/download.jsp_). There is also a RESTful endpoint which
can be used to download the data by year:

    http://www.nsf.gov/awardsearch/download?DownloadFileName=`2014`&All=true

Each file that is downloaded is a zipped XML file with a listing of all awards for that year.
So for instance, a POST request to the above URI will return a zipped XML file that contains
all the award data for the year 2014. The schema for the XML data can be seen
[here](_http://www.nsf.gov/awardsearch/resources/Award.xsd_). It will be elaborated upon below
in order to formulate ideas for and detail assumptions made when parsing the awards into a
cleaned form which will be stored in a SQL database. The goal of this effort is to produce a
high quality representation of the data with minimal redundancy and maximum clarity, while
ensuring the XML representation of the awards is interpreted correctly.

## XML Schema Breakdown

Each year is downloaded as a zip file and is named using the year: `<year>.zip`.
Each zip file contains a bunch of XML files, each containing info for exactly one
award. These files are named using the award ID: `<awardID>.xml`. Each XML file has
a `rootTag>`, followed by an `<Award>` tag which contains the following elements:

1.  **AwardID** (_int_): The unique ID of the award.

2.  **AwardTitle** (_string_): The title of the award.
3.  **AbstractNarration** (_string_): An overview of what the research is seeking
        to do.

4.  **AwardEffectiveDate** (_dateTime_): The date the award funding starts.
5.  **AwardExpirationDate** (_dateTime_): The date the award funding ends.

6.  **MinAmdLetterDate** (_dateTime_): The first date the award was amended.
7.  **MaxAmdLetterDate** (_dateTime_): The last date the award was amended.

8.  **AwardAmount** (_int_): The amount of money awarded to date.
9.  **ARRAAmount** (_string_): Portion of AwardAmount funded by the American
        Recovery and Reinvestment Act (_ARRA_).

10. **AwardInstrument** (_sequence_): Listing of classifications for this award.
    1.  **Value_ (_string_): A particular classification** (e.g. "Standard Grant",
        "Cooperative Agreement", "Contract").

11. **Organization** (_sequence): The NSF organization(s_) funding the grant.
    1.  **Code** (_int_): Unique ID of the organization funding this award.
            DIRECTORE, DIVISON, or COMBO?
    2.  **Directorate** (_sequence_): Listing of directorates funding this award.
        1.  **LongName** (_string_): Name of directorate.
    3.  **Division** (_sequence_): Listing of divisions funding this award.
        1.  **LongName** (_string_): Name of division.

12. **ProgramElement** (_sequence_): Listing of programs funding this award.
    1.  **Code** (_int_): Unique ID of the program.
    2.  **Text** (_string_): Name of the program.

13. **ProgramReference** (_sequence_): Listing of programs related to the one funding this award.
    1.  **Code** (_int_): Unique ID of the program referenced.
    2.  **Text** (_string_): Name of the program referenced.

14. **ProgramOfficer** (_sequence_): A listing of all Program Officers responsible for this award.
    1.  **SignBlockName** (_string_): The name of the Program Officer.

15. **Investigator** (_sequence_): A listing of all investigators who have worked on or are working on this award.
    1.  **FirstName** (_string_): The first name of the investigator.
    2.  **LastName** (_string_): The last name of the investigator.
    3.  **EmailAddress (_string): The email address of the investigator** (optional_).
    4.  **StartDate** (_dateTime_): The date the investigator started working on this award.
    5.  **EndDate** (_dateTime_): The date the investigator stopped working on this award.
    6.  **RoleCode** (_int_): The role of the investigator, identified by an integer code.
            Either "Principal Investigator" or "Co-Principal Investigator".

16. **Institution** (_sequence): The institution sponsoring this award (PO/Investigator affiliation_).
    1.  **Name** (_string_): Name of the institution.
    2.  **PhoneNumber** (_decimal_): Phone number of the institution.
    3.  **CityName** (_string_): Name of the city where the institution is located.
    4.  **StreetAddress** (_string_): Name of the street on which the institution is located.
    5.  **StateCode** (_string_): The
    6.  **StateName** (_string_): Name of the state in which the institution is located.
    7.  **ZipCode** (_int_): Zip code of the institution's postal address.
    8.  **CountryName** (_string_): Name of the country in which the institution is located.

17. **FoaInformation** (_sequence): Funding Opportunity Anouncement (FOA) reference (to Grants.gov FOA listing_).
    1.  **Code** (_int_): Unique ID of FOA.
    2.  **Name** (_string_): Name of FOA.
