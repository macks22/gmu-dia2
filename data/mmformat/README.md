This document details the contents of the following three data files:

1.  pi-feature-matrix.mtx
2.  pi-name-index.csv
3.  feature-name-index.csv

Together these files comprise a set of _representative documents_ for each
principal investigator (PI) in the CISE NSF directorate. This document is
organized into 3 sections. The first gives background on the origin of the data
and previous processing procedures. The second provides detailed methodology for
the additional pre-processing steps performed on the data, and the third
outlines the format of the data in each of the 3 files, while also explaining
the relationships between the files.

## Background

The dataset was originally downloaded from the
[nsf.gov](http://www.nsf.gov/awardsearch/download.jsp) and pre-processed by
Purdue University. The pre-processing steps of relevance to this subset of that
data are as follows:

1.  Disambiguate PIs based on Levenshtein distances between names
2.  Disambiguate programs and divisions in the same manner

The Levenshtein distance method used had one of 3 outcomes (PIs, divisions, and
programs are all referred to as "entities"):

1.  two entities were matched correctly
2.  two entities not the same were matched incorrectly
3.  two entities the same were not matched and are represented separately

There is no way, given the pre-processed dataset to determine to what extent the
disambiguation procedure produced outcome #1 vs. outcome #2 & #3.

## Methodology

Given the pre-processed NSF data from Purdue, the goal of this particular
transformation of the dataset was to produce a representation suitable for
topic modelling. Each of the PIs in the dataset has a set of one or more awards
he/she has worked on. **In total, there are 14,979 PIs and 22,263 awards.** Each
of these awards has a single abstract, which may be empty, quite short, or very
lengthy. More specifically, here are statistics on the lengths:

*   min = 0
*   max = 5000
*   avg = 1881
*   std = 847

Given this information, a _representative document_ (repdoc) was parsed for each
PI in the dataset, in the following manner:

1.  For all awards the PI has worked on, concatenate with spaces between to get
    a single string of words.
2.  The following cleaning operations are performed:
    1. punctuation removed
    2. all characters lowercased
    3. whitespace stripped
3.  Words meeting these filtering criteria are removed:
    1. empty or only 1 character
    2. stopword
    3. all digits
    4. starts with digit
4.  Finally, all words are stemmed using a Porter stemmer.

At this point, each repdoc is represented as a list of words. In order to
produce a BoW matrix of term frequencies, all 14,979 repdocs are together
treated as a corpus of abstracts and the following steps are performed:

1.  All words in the corpus are assigned an ID (dictionary of words)
    *   each word is now represented as (id, frequency), with an associated
        lookup table of (id, term)
2.  Filter out tokens that appear in
    1.  less than 5 documents (absolute number) or
    2.  more than half of all documents
    3.  after (1) and (2), keep only the first 100,000 most frequent terms
3.  After the pruning, shrink resulting gaps in word ids so they are continuous

For the abstracts corpus, step 2.3 does not discard any words. The total number
of words after this process is 12,171.

## Data Format

### pi-feature-matrix.mtx


### pi-name-index.csv
### feature-name-index.csv
