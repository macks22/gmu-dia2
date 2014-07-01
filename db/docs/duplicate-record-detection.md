## Idea

Duplicate record detection, or record linkage, is the problem of detecting records in one or
more databases that refer to the same real-world entity. Duplicate records are often a result of
inconsistencies in the cataloging of data, particularly string data. This is also referred to as
disambiguation elsewhere in the DB documentation.

## Applicability

For the purposes of the NSF award data, the entities which require duplicate record
detection are:

1.  Directorate
2.  Division
3.  Investigator
4.  Program Officer
5.  Institution

This is assuming the following:

1.  ProgramElement Code tags uniquely identify the Program.
2.  AwardIDs uniquely identify each Award.

## Methods

See:

[Elmagarmid, A. K., Ipeirotis, P. G., & Verykios, V. S. (2007).
Duplicate record detection: A survey.
Knowledge and Data Engineering, IEEE Transactions on, 19(1), 1-16.](
http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4016511)

### String Matching

There are a variety of string matching techniques which have been explored.
They are categorized as either:

1.  Character-based
2.  Token-based
3.  Phonetic

#### Character-Based Similarity Measures

1.  Edit distance (such as Levenshtein)
2.  Affine gap distance
3.  Smith-Waterman distance
4.  Jaro distance metric
5.  Q-gram distance

#### Token-Based Similarity Measures

1.  Atomic strings
2.  WHIRL (cosine similarity with TF.IDF)
3.  Q-grams with TF.IDF
4.  **SoftTF.IDF**

#### Phonetic Similarity Measures

1.  Soundex
2.  New York State Identification and Intelligence System (NYSIIS)
3.  Oxford Name Compression Algorithm (ONCA)
4.  Metaphone and Double Metaphone

## Approach

Since all of the entities we need to perform duplicate record detection on are
likely to be identified primarily by string attributes, string matching techniques
shoudl be sufficient. [The algorithm most likely to work ideally for this problem
is SoftTF.IDF](https://www.cs.cmu.edu/~pradeepr/papers/ijcai03.pdf). There is an
implementation of this algorithm and just about every other string matching
algorithm you might ever want in the [SecondString Java library](
http://secondstring.sourceforge.net/javadoc/com/wcohen/secondstring/SoftTFIDF.html).
Using this library along with JDBC for DB access should be sufficient for our
purposes.

Below, the approach for each particular entity is laid out in more detail.

### Directorate and Division

Perform string matching on LongName tag text.

### Investigator

First check for an identical email; if found, score as a perfect match. Otherwise,
perform string matching separately on the FirstName and LastName and aggregate the
scores together (a simple sum may suffice). If the score meets some threshold,
conclude the two records are duplicates and merge them.

### Program Officer

Perform string matching on the SignBlockName tag text. We also might consider
increasing the confidence score if the two records share a program in common.

### Institution

Consider two institutions the same if:

1.  they have the same phone number
2.  same name and zip code
3.  names match with high confidence and same zip code
4.  aggregate address matching produces high confidence
