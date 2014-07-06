The contents of this directory are as follows. All files are tab-delimited.

Input Data Files
================

pi-graph-edges.txt
------------------

(node_id, node_id), where each node_id is the ID of the PI the node represents.
Corresponds to 1912.edges in CESNA sample data.

abstracts-features.txt
----------------------

(term_id, term), where each term is a word in the corpus of abstracts for all
NSF CISE awards, and each term_id is a unique ID assigned to that term.
Corresponds to 1912.nodefeatnames in the CESNA sample data.

pi-representative-doc-terms.txt
-------------------------------

(node_id, term_id), where node_id is the ID of the PI represented by the node,
and the term_id is a term that showed up in the PI's representative document,
which is the concatenation of all abstracts for all awards the PI worked on.
Corresponds to 1912.nodefeats in the CESNA sample data.

node-labels-pi-names.txt
------------------------

(node_id, node_label), where node_id is the ID of the PI represented by the
node, and the node_label is the name of the PI. This file is not required by
CESNA. Oddly, when it is passed in, only some of the labels are applied, so it
was not used to produce the results discussed below.


Results Files
=============

Docs for these were taken straight from:
https://github.com/snap-stanford/snap/tree/master/examples/cesna.

cmtyvv.txt
----------

"Community memberships. Each row shows the IDs of nodes that belong to each
community."

weights.txt
-----------

"Logistic weight. k-th number for i-th row shows the logistic weight factor
between community i and attribute k. If the names of attributes are given, the
names are written in the first row."

