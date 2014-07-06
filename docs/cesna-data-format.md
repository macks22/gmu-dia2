### Goal

Figure out how to represent a graph in the format CESNA can process.

### Methodology

Examine the example data files to glean patterns and document the likely meaning
of the files in order to understand the format, then parse the NSF CISE data
into that format and try to run CESNA on it. If it fails, analyze and make
changes. Repeat until success.

### Input Data Files

There are 3 required input files and 1 which is not required. All are
tab-delimited, but shown as tuples below.

1.  **edges**: (node_id, node_id) pairs which represent edges
2.  **node features**: (node_id, feature_number), presumably to represent that a
    particular node has a particular feature
3.  **node feature names**: (feature_number, feature_name), presumably to
    identify which feature a particular number represents
4.  **node labels**: (node_id, node_label) labels for each node. <-- optional

The part where it gets hairy is the node feature identification. Since all of
the features are anonymized, it's hard to tell what's actually going on, and
where the meaningful feature information is really coming from. For instance,
the first line in the CESNA example data file 1912.nodefeat is this:

> 1913    0

This seems to indicate that the node with id 1913 has feature 0. The line for
this feature in 1912.nodefeatnames is this:

> 0    birthday;anonymized feature 5

So one key question arises here:

1.  Is the name of the feature "birthday;anonymized feature 5", or
    "birthday;anonymized", with the "feature 5" being some kind of reference to
    the non-anonymized dataset feature id?
    1. If the first is true, then the dataset being used must be some sample of
       the full dataset which contains nodes whose only attributes are some
       subset of the 28 listed in 1912.nodefeatnames. So the example above would
       identify a particular birthday which some of the nodes share in common.
    2. If the second is true, then the actual non-anonymized features would have
       to be pulled from an outside data source, such as a password-protected
       data store running on a publicly routable server.
    3. Of the two options, the first seems more likely. If this is the case, we
       can conclude this for our data: represent each word in the abstract
       corpus as a distinct feature with a unique ID. If a particular PI (node)
       has that word in his representative corpus, list it in the nodefeatures
       file, otherwise do not list it.

### Testing (Round 1)

Parsed all files into txt (tab-delimited) data files according to reasoning
above. CESNA runs just fine on that. One thing to note is that the node feature
lables were largely ignored. Even though there were labels for all nodes, only a
few were actually applied. This was not helpful, so I just reran it without
labels so only IDs show up.

