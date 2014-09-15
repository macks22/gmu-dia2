import cPickle as pickle

import gensim

import data
import abstracts



class EdgesFile(object):
    """Write the file of edges as PI ID pairings."""

    def __init__(self):
        self.g = data.load_full_graph()

    def get_pi_id(self, idx):
        return self.g[idx]['label']

    def get_edge_pis(edge):
        id1, id2 = edge.tuple
        return (self.get_pi_id(id1), self.get_pi_id(id2))

    def parse():
        return (get_edge_pis(edge) for edge in self.g.es)

    def write():
        pi_pairings = self.parse()
        with open('cesna-edge-pi-pairings.txt', 'w') as f:
            for pi_id1, pi_id2 in pi_pairings:
                f.write('{} {}\n'.format(pi_id1, pi_id2))


class FeaturesFiles(object):
    """Write the features file for all PI representative documents."""

    def __init__(self, **kwargs):
        self.g = data.load_full_graph()
        self.bowas = abstracts.AbstractBoWs(**kwargs)

    def all_pis(self):
        return (v['label'] for v in self.g.vs)

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


class TfidfTermDocMatrix(object):
    """Write a term-document matrix in pseudo-mmformat: tfidf for counts."""

    def __init__(self, **kwargs):
        self.g = data.load_full_graph()
        self.pis = set([(v.index, v['label']) for v in self.g.vs])
        self.pis = sorted(list(self.pis), key=lambda tuple: tuple[0])

        corpus = kwargs.get('corpus', None)
        self.corpus = corpus if corpus else abstracts.AbstractBoWs(**kwargs)
        tfidf = kwargs.get('tfidf', None)
        self.tfidf = tfidf if tfidf else gensim.models.TfidfModel(self.corpus)

        self.num_docs = self.corpus.num_docs
        self.num_terms = self.corpus.num_terms
        self.num_nnz = self.corpus.num_nnz
        self.header = "%%MatrixMarket matrix coordinate real general"

    @property
    def stats(self):
        return ' '.join(map(str,
                (self.num_docs, self.num_terms, self.num_nnz)))

    @property
    def mmheader(self):
        return ''.join([self.header,'\n',self.stats,'\n'])

    @classmethod
    def load(cls, corpusfile, tfidf_file):
        with open(corpusfile) as f:
            corpus = pickle.load(f)
        with open(tfidf_file) as f:
            tfidf = pickle.load(f)
        return TfidfTermDocMatrix(corpus=corpus, tfidf=tfidf)

    def iterdocs(self):
        for pi_label, pi_id in self.pis:
            tf_doc = self.corpus.pi_document(pi_id)
            yield (pi_label, tf_doc)

    def itertfidfdocs(self):
        for pi_label, doc in self.iterdocs():
            tfidf_doc = self.tfidf[doc]
            yield (pi_label, tfidf_doc)

    def write(self, fpath='abstracts-matrix'):
        """Writes four different files for the tfidf version of the abstracts
        corpus::

            1.  Matrix Market (doc termid tfidf)
            2.  Matrix Market (doc termid tf)
            3.  document frequencies (termid, docfreq)
            4.  term mappings (term-id, term)

        ...where `doc` is the ID of the PI.

        """
        tf_file = fpath + '-tf.mm'
        tfidf_file = fpath + '-tfidf.mm'

        self.write_tf_matrix_fast(tf_file)
        self.write_tfidf_matrix_fast(tfidf_file)
        self.write_tmap_and_dfs()

    # IN BOTH MM WRITING METHODS: YOU NEED TO ENSURE FORTRAN START-FROM-1
    # INDEXING IS USED AND PI INDICES SHOULD BE MAPPED TO CONTIGUOUS RANGE FROM
    # 1-#PIS IN ORDER TO ENSURE ROW INDICES DO NOT EXCEED MATRIX DIMENSIONS

    def write_tf_matrix_fast(self, fpath='abstracts-matrix-tf.mm'):
        gensim.corpora.MmCorpus.serialize(
            fpath, (doc for pi, doc in self.iterdocs()),
            self.corpus.dictionary.id2token)

    def write_tf_matrix(self, fpath='abstracts-matrix-tf.mm'):
        with open(fpath, 'wb') as f:
            f.write(self.mmheader)
            for pi, doc in self.iterdocs():
                f.write('\n'.join(
                    [' '.join((str(pi+1), str(termid+1), str(tf)))
                    for termid, tf in doc]))

    def write_tfidf_matrix_fast(self, fpath='abstracts-matrix-tfidf.mm'):
        gensim.corpora.MmCorpus.serialize(
            fpath, (doc for pi, doc in self.itertfidfdocs()),
            self.corpus.dictionary.id2token)

    def write_tfidf_matrix(self, fpath='abstracts-matrix-tfidf.mm'):
        with open(fpath, 'wb') as f:
            f.write(self.mmheader)
            for pi, doc in self.itertfidfdocs():
                f.write('\n'.join(
                    [' '.join((str(pi+1), str(termid+1), str(tfidf)))
                    for termid, tfidf in doc]))

    def write_pimap_and_names(self, fpath='pimap-and-names.csv'):
        with open('name-index.pickle') as f:
            index = pickle.load(f)
        tuples = ((str(pi_label), pi_id, unicode(name_index[pi_id]))
                  for pi_label, pi_id in self.pis)
        strings = (u','.join(tup) for tup in tuples)
        with open(fpath, 'wb') as f:
            f.write('docid,pi-id,pi-name\n')
            f.write(u'\n'.join(pair for pair in strings).encode('utf-8'))

    def write_pimap(self, fpath='pi-id-mappings.csv'):
        tuples = ((str(pi_label), pi_id) for pi_label, pi_id in self.pis)
        strings = (','.join(tup) for tup in tuples)
        with open(fpath, 'wb') as f:
            f.write('pilabel,piid\n')
            f.write('\n'.join(pair for pair in strings))

    def write_tmap_and_dfs(self, fpath='term-map-and-freqs.csv'):
        get_dfs = lambda termid: self.corpus.dictionary.dfs[termid]
        tok2id = sorted(self.corpus.dictionary.items())
        tuples = ((unicode(tid), term, unicode(get_dfs(tid)))
                  for tid, term in tok2id)

        with open(fpath, 'wb') as f:
            f.write('termid,term,docreq\n')
            f.write(u'\n'.join(
                [u','.join(tup) for tup in tuples]).encode('utf-8'))

    def write_term_mappings(self, fpath='termid-mappings.csv'):
        with open(fpath, 'wb') as f:
            f.write('termid,term\n')
            term_pairs = [u','.join((unicode(termid), unicode(term)))
                          for term, termid
                          in self.corpus.dictionary.token2id.iteritems()]
            content = u'\n'.join(term_pairs)
            f.write(content.encode('utf-8'))

    def write_dfs(self, fpath='term-document-frequencies.csv'):
        with open(fpath, 'wb') as f:
            f.write('termid,docfreq\n')
            f.write('\n'.join([','.join((str(termid), str(df)))
                              for termid, df
                              in self.tfidf.dfs.iteritems()]))
