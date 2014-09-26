import sys
import logging
import cPickle as pickle

import data
from repdoc_writer import read_pi_tfidf_bow, read_pi_tf_bow


header = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
     http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">

<graph id="G" edgedefault="undirected">
"""
footer = """
</graph>
</graphml>
"""

node_tag = """<node id="{node_id}" {attributes}/>\n"""
edge_tag = """<edge source="{source}" target="{target}"/>\n"""

key_tag = """
<key id="{attr_id}" for="node" attr.name="{name}" attr.type="{type}">
  <default>0</default>
</key>\n"""
data_tag = """  <data key="{key}">{value}</data>\n"""
node_with_data_tag = """<node id="{node_id}">\n{data_tags}</node>\n"""


def filter_edges(graph, pis):
    edgelist = set()

    # filter to only those edges that connect the given pis
    for edge in graph.es:
        pi1 = graph.vs[edge.source]['label']
        pi2 = graph.vs[edge.target]['label']
        if pi1 in pis and pi2 in pis:
            edgelist.add(edge)

    # remove parallel edges
    non_multiples = filter(lambda e: not e.is_multiple(), edgelist)
    return non_multiples


def write_sparse_graph(graph, corpus, term_map, dtype="double",
                       fpath='sparse-pi-graph.graphml'):
    pis = set(corpus.keys())
    with open(fpath, 'w') as f:
        f.write(header)
        write_keys(term_map, dtype, f)

        # write all nodes for the given PIs
        pi_nodes = (node for node in graph.vs if node['label'] in pis)
        for num, node in enumerate(pi_nodes):
            if num % 100 == 0:
                logging.info("{} nodes left to write...".format(
                    num_nodes - num))
            write_sparse_node(node, f, corpus, termids)

        # write all edges for the given PIs
        logging.info("done writing nodes.")
        edges = filter_edges(graph, pis)
        num_edges = len(edges)
        logging.info("writing {} edges...".format(num_edges))
        for edge in filter_edges(graph, pis):
            write_edge(edge, f)

        f.write(footer)


def write_keys(term_map, dtype, f):
    for term_id in term_map:
        tag = key_tag.format(
            attr_id=tlabel(term_id), name=term_map[term_id], type=dtype)
        f.write(tag)


def tlabel(termid):
    return "t%d" % termid


def write_sparse_node(node, f, corpus):
    node_id = node.index
    pi = node['label']
    doc = corpus[pi]
    terms = ((tlabel(termid), doc[termid]) for termid in doc)
    dtags = (data_tag.format(key=key, value=weight) for key, weight in terms)
    attr_string = ''.join(dtags)
    tag = node_with_data_tag.format(node_id=node_id, data_tags=attr_string)
    f.write(tag)


def write_graph(graph, corpus, termids, fpath='pi-graph.graphml'):
    pis = set(corpus.keys())
    num_nodes = len(pis)
    logging.info("writing dense graph: {} pi nodes, {} terms/node".format(
        num_nodes, len(termids)))

    with open(fpath, 'w') as f:
        f.write(header)

        # write all nodes for the given PIs
        pi_nodes = (node for node in graph.vs if node['label'] in pis)
        for num, node in enumerate(pi_nodes):
            if num % 100 == 0:
                logging.info("{} nodes left to write...".format(
                    num_nodes - num))
            write_node(node, f, corpus, termids)

        # write all edges for the given PIs
        logging.info("done writing nodes.")
        edges = filter_edges(graph, pis)
        num_edges = len(edges)
        logging.info("writing {} edges...".format(num_edges))
        for edge in filter_edges(graph, pis):
            write_edge(edge, f)

        f.write(footer)


def node_attributes(corpus, term_ids, node):
    pi = node['label']
    doc = corpus[pi]
    items = ((tlabel(term_id), doc.get(term_id, 0)) for term_id in term_ids)
    return ('{}="{}"'.format(term_label, weight)
            for term_label, weight in items)


def write_node(node, f, corpus, termids):
    node_id = node.index
    attr_string = ' '.join(node_attributes(corpus, termids, node))
    f.write(node_tag.format(node_id=node_id, attributes=attr_string))


def write_edge(edge, f):
    id1, id2 = edge.tuple
    f.write(edge_tag.format(source=id1, target=id2))


# LOADERS
# =============================================================================

def load_graph():
    return data.load_full_graph()

def load_pi_list(fpath='cise-lcc-binary-membership-ids.txt'):
    with open(fpath) as f:
        return f.read().split()

def load_corpus(pi_ids, corpus_type='tfidf'):
    read_pi_doc = (read_pi_tfidf_bow if corpus_type == 'tfidf'
                   else read_pi_tf_bow)
    return {pi:dict(read_pi_doc(pi)) for pi in pi_ids}

def load_term_ids():
    with open('termids.txt') as f:
        return map(int, f.read().split())

def load_term_map():
    with open('term-map.pickle') as f:
        return pickle.load(f)


# WRITERS
# =============================================================================

def write_dense_graph(weights='tfidf'):
    fpath = 'pi-{}-graph.graphml'.format(weights)
    logging.info("writing dense {} graph".format(weights))
    pis = load_pi_list()
    logging.info("filtering graph to %d pis" % len(pis))
    corpus = load_corpus(pis, weights)
    termids = load_term_ids()
    logging.info("writing %d terms for each pi node" % len(termids))
    graph = load_graph()
    write_graph(graph, corpus, termids, fpath)

def write_sparse_graph(weights='tfidf'):
    fpath = 'sparse-pi-{}-graph.graphml'.format(weights)
    logging.info("writing sparse {} graph".format(weights))
    pis = load_pi_list()
    logging.info("filtering graph to %d pis" % len(pis))
    corpus = load_corpus(pis, weights)
    term_map = load_term_map()
    logging.info("writing %d terms for each pi node" % len(term_map))
    graph = load_graph()
    dtype = 'double' if dtype == 'tfidf' else 'int'
    write_sparse_graph(graph, corpus, term_map, dtype, fpath)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s [%(levelname)s]: %(message)s")

    if len(sys.argv) < 2 or sys.argv[1] not in ['tf', 'tfidf']:
        print "graphml_writer.py <tfidf|tf>"

    if len(sys.argv) > 2 and sys.argv[2] in ['sparse', 'dense']:
        gtype = sys.argv[2]
    else:
        gtype = 'dense'

    if gtype == 'dense':
        write_dense_graph(sys.argv[1])
    else:
        write_sparse_graph(sys.argv[1])
