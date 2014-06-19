This short document describes what the folders in the data directory are and
what they're supposed to contain, as well as conventions for each.


##json

Contains raw data in JSON format. The files are named based on the year and
month which they contain data for:

    docs-<year>-<month>.json

<month> := 2-digit month of the year (1-12)
<year>  := 4-digit year

Each file contains JSON data indexed at the top level by document ids.  Each
document represents an award, so that the award ids and document ids maintain a
1:1 mapping.

The other data in each doc/award JSON block is:

* abstract
* title
* awardID
* effectiveDate
* expirationDate
* fundingAgent
    - dir
        + id
        + name
        + abbr
    - div
        + id
        + name
        + abbr
    - pgm
        + id
        + name
* PIcoPI
* PO


##csv

Contains tables of information parsed from the JSON files. All files are in CSV
(comma-separated values) format.


##pi-award-graphs

Contains graph data which was parsed from the JSON files, typically in GraphML
format.


##pickle

Contains pickled Python data structures which were time-consuming to parse.
This directory is primarily to avoid unecessary re-parsing of the JSON data, as
pickle files are much faster to load from.

##bow

Contains text files which contain BoW representations for each PI in the
dataset. The BoW for each PI is generated using the following methodology:

    1. get list of all awards the PI has been involved with
    2. get the abstracts for each of those awards
    3. treat the list of abstracts as a set of documents
    4. parse the set of documents into a BoW frequency distribution
    5. assign the BoW to the PI and save it as a text file
    6. use the ID of the PI as the name of the text file

So the bow directory contains one text file for every PI in the JSON dataset.
Each file is named using the PI ID, so the filenames look like:

    pi-<pi_id>.txt

For convenience, the intermediate award abstract parsings are also
stored in text files, named using the award ids, like so:

    award-<award_id>.txt

