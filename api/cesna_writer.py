# coding: utf-8

import data
import abstracts


def pi_labels_from_graph(graph):
    return [v['label'] for v in g.vs]

def pi_from_docid(graph, docid):
    return graph.vs[docid]['label']

def edge_to_string(graph, edge):
    return '\t'.join(
        [pi_from_docid(graph, docid) for docid in edge.tuple])

def write_graph_edges(graph, edges, fpath):
    with open(fpath, 'w') as f:
        f.write('\n'.join(
            [edge_to_string(graph, edge) for edge in edges]))

def get_pi_terms(bow_corpus, pi):
    return [tup[0] for tup in bow_corpus.pi_document(pi)]

def pi_terms_to_string(pi_terms, pi_id):
    pairs = zip([pi_id] * len(pi_terms), map(str, pi_terms))
    strings = ['\t'.join(pair) for pair in pairs]
    return '\n'.join(strings)

def pi_terms_string(bow_corpus, pi_id):
    pi_terms = [tup[0] for tup in bow_corpus.pi_document(pi_id)]
    pairs = zip([pi_id] * len(pi_terms), map(str, pi_terms))
    strings = ['\t'.join(pair) for pair in pairs]
    return '\n'.join(strings)

def write_all_pi_terms(pis, bow_corpus, fpath):
    with open(fpath, 'w') as f:
        for pi in pis:
            f.write(pi_terms_string(bow_corpus, pi))

def term_map_to_string(bow_corpus):
    items = [(unicode(term_id), term) for term_id, term in
            sorted(bow_corpus.dictionary.items())]
    strings = [u'\t'.join(tup) for tup in items]
    return u'\n'.join(strings)

def write_term_map(bow_corpus, fpath):
    with open(fpath, 'w') as f:
        f.write(term_map_to_string(bow_corpus).encode('utf-8'))

def load_pi_list(fpath='cise-lcc-binary-membership-ids.txt'):
    with open(fpath) as f:
        return f.read().split()

def filter_edges_to_pis(graph, pis):
    edges = set()
    for edge in graph.es:
        pi1 = graph.vs[edge.source]['label']
        pi2 = graph.vs[edge.target]['label']
        if pi1 in pis and pi2 in pis:
            edges.add(edge)
    return edges


if __name__ == "__main__":
    graph = data.load_full_graph()
    pis = load_pi_list()
    edges = filter_edges_to_pis(graph, pis)

    write_graph_edges(graph, edges, 'pi-graph-edges.tsv')
    #bow_corpus = abstracts.AbstractBoWs(parse=True)
    #write_all_pi_terms(pis, bow_corpus, 'repdoc-terms.tsv')
    #write_term_map(bow_corpus, 'term-map.tsv')
