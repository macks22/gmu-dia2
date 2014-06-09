import data
import abstracts


class EdgesFile(object):
    """Write the file of edges as PI ID pairings."""

    def __init__(self):
        self.g = data.load_full_graph()

    def get_pi_id(self, idx):
        return self.g[idx]['label']

    def get_edge_pis(edge):
        igraph_ids = edge.tuple
        pi_id1 = self.get_pi_id(igraph_ids[0])
        pi_id2 = self.get_pi_id(igraph_ids[1])
        return (pi_id1, pi_id2)

    def parse():
        for edge in self.g.es:
            yield get_edge_pis(edge)

    def write():
        pi_pairings = self.parse()
        with open('cesna-edge-pi-pairings.txt', 'w') as f:
            for pi_id1, pi_id2 in pi_pairings:
                f.write('{} {}\n'.format(pi_id1, pi_id2))


class FeaturesFiles(object):
    """Write the features file for all PI representative documents."""

    def __init__(self):
        self.g = data.load_full_graph()
        self.bowas = abstracts.AbstractBoWs()

    def all_pis(self):
        for v in self.g.vs:
            yield v['label']

    def all_term_freqs_for_pi(self, pi_id):
        all_freqs = []
        rep_doc = dict(self.bowas.pi_document(pi_id))
        for num in range(len(self.bowas.dictionary)):
            if num in rep_doc:
                all_freqs.append(rep_doc[num])
            else:
                all_freqs.append(0)

        return all_freqs

    def parse(self):
        for pi_id in self.all_pis():
            all_term_freqs = self.all_term_freqs_for_pi(pi_id)
            yield unicode(pi_id) + ' '.join(map(unicode, all_term_freqs))

    def write(self, features=True, descriptors=True):
        pi_features = self.parse()

        if features:
            with open('cesna-features-file.txt', 'w') as f:
                for pi_feature_string in pi_features:
                    to_write = pi_feature_string + '\n'
                    f.write(to_write.encode('utf-8'))

        if descriptors:
            with open('cesna-features-file-descriptors.txt', 'w') as f:
                for item in self.bowas.dictionary.iteritems():
                    f.write('{} {}\n'.format(item[0], item[1]))
