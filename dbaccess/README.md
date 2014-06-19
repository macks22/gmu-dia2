## Overview

From what I can tell, the design decisions made when constructing the DIA2
database schema either boil down to an unnecessary desire for strict
normalization (3NF in the most recent version), lack of experience,
over-engineering, or a combination of some of the above. In an attempt to learn
from the mistakes of others and produce a useful working database for the
research GMU is doing with the DIA2 data, I am planning to redesign the DIA2
database schema and populate it from scratch with the raw data available from NSF.

## Disambiguation

After initially populating the database, I'll need to perform disambiguation
based on the methods used by Purdue. Hopefully these methods are sufficient, but
if I find they are ineffective in more than a few cases, I will also attempt to
improve that process. Either way, I will seek to better document the
methodology. I have yet to decide whether or not to retain disambiguation
history as Purdue has done. The method they used was to enter every person
as having a unique ID, then disambiguate by tying those unique IDs to unique
canonical IDs. This method retains history but may complicate queries.
Perhaps better would be to transition the stored people entries to using the
canonical IDs as their PKs and retain in another database disambiguation
records.

## Address Storage: Consistency/Convenience Tradeoffs

Another area of improvement is the way that addresses are stored. Currently, an
address is made up of a bunch of IDs, which index into tables that contain
things like ISO codes. This succeeds at ensuring consistency of various address
fields but makes it a huge pain in the ass to actually get the meaningful
address codes of the various fields stored in the address table. A better
approach would be to store the codes in separate tables, with display names as
attributes, use the codes as keys, and then put FKs on the attributes of the
address table. There needs to be a reasonable balance between planning for
internationalization and simplicity. In this case, NSF data is mostly for
analysis and we don't really need to care about shipping things to the proper
postal addresses, so this general schema should suffice:

    *********************************
    Field              Type
    *********************************
    address_id (PK)    int
    unit               string
    building           string
    street             string
    city               string
    region             string
    country            string
    address_code       string
    *********************************

It will be useful to have additional tables for codes/abbreviations, as
described above:

1. state (abbrev, name)
2. country (code, name)

A note on #1: since a region may not be a state, there are a few possible
approaches which could be taken:

1. Do not constrain region at all, and don't use a state table
2. Do not constrain region at all, and use a state table only when abbreviations
   are found
3. Do not constrain region at all, and use a general region-mapping table to map
   region abbreviations to region names; use this for translation
4. Attempt to capture all region abbreviations in a region table, and constrain
   the region attribute using that
5. Add another attribute for state, constrain that one, and allow either to be
   NULL (but not both at the same time? Is that possible?)

### Geospatial Analysis

It will likely be interesting at some point to map a trend of NSF funding based
on geospatial locality, so adding two lat/lon fields to the address table
might also be useful. The decimal values used below allow for ~1mm accuracy at
the equator. Initially at least it will be useful to allow these to be NULL by
default, since the raw NSF data does not have lat/lon coords.

    *********************************
    Field              Type
    *********************************
    lat             decimal(10,8)
    lon             decimal(11,8)
    *********************************

## Enrichment

One of the more ambitious goals with this database will be an effort to enrich
the data we have by mining additional papers, abstracts, publications, etc for
each investigator. It will also be useful to make an attempt to map their
affiliation progressions. For instance, for a particular researcher, we can
currently tell what their affiliations are as a group, and we can infer what the
current one is, but we do not have the time interval over which they were
actually affiliated with an organization. This could probably be scraped from
personal pages, institutional faculty listings, etc.
