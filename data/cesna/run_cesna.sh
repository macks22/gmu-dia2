~/workshop/sna/Snap-2.2/examples/cesna/cesna \
-i:pi-graph-edges.txt \  # the edges of the graph, with ids representing PIs
-a:pi-representative-doc-terms.txt \  # node features (terms in BoW for PI)
-n:abstracts-features.txt -c:96 \  # mappings from term IDs to their terms
-c:96 \  # number of communities to detect (main parameter)
# -l:node-labels-pi-names.txt  # the names of the PIs (node id/name pairs)
