import os


repdoc_dir = 'repdocs'
doc_dir = os.path.join(repdoc_dir, 'text')
vec_dir = os.path.join(repdoc_dir, 'vectors')
tf_bow_dir = os.path.join(repdoc_dir, 'tf-bows')
tfidf_bow_dir = os.path.join(repdoc_dir, 'tfidf-bows')

def write_pi_doc(corpus, pi_id):
    fname = os.path.join(doc_dir, "%s.txt" % pi_id)
    with open(fname, 'w') as f:
        f.write(corpus.pi_document(pi_id))

def read_pi_doc(pi_id):
    fname = os.path.join(doc_dir, "%s.txt" % pi_id)
    with open(fname) as f:
        return f.read()

def write_pi_doc_vector(vector_corpus, pi_id):
    fname = os.path.join(vec_dir, "%s.txt" % pi_id)
    doc = u' '.join(vector_corpus.pi_document(pi_id))
    with open(fname, 'w') as f:
        f.write(doc.encode('utf-8'))

def read_pi_doc_vector(pi_id):
    fname = os.path.join(vec_dir, "%s.txt" % pi_id)
    with open(fname) as f:
        return f.read().split(' ')

def write_pi_tf_bow(bow_corpus, pi_id):
    fname = os.path.join(tf_bow_dir, "%s.csv" % pi_id)
    bow = bow_corpus.pi_document(pi_id)
    strings = [','.join(map(str, tup)) for tup in bow]
    with open(fname, 'w') as f:
        f.write('\n'.join(strings))

def read_pi_tf_bow(pi_id):
    fname = os.path.join(tf_bow_dir, "%s.csv" % pi_id)
    with open(fname) as f:
        lines = [line.split(',') for line in f.read().split()]
        return [(int(term_id), int(tf)) for term_id, tf in lines]

def write_pi_tfidf_bow(pi_id):
    fname = os.path.join(tfidf_bow_dir, "%s.csv" % pi_id)
    bow = abow.pi_document(pi_id)
    tfidf_bow = tfidf[bow]
    strings = [','.join(map(str, tup)) for tup in tfidf_bow]
    with open(fname, 'w') as f:
        f.write('\n'.join(strings))

def read_pi_tfidf_bow(pi_id):
    fname = os.path.join('repdocs/tfidf-bows', "%s.csv" % pi_id)
    with open(fname) as f:
        lines = [line.split(',') for line in f.read().split()]
        return [(int(term_id), float(weight)) for term_id, weight in lines]

def tlabel(termid):
    return "t%d" % termid

def iterterms(term_ids, doc):
    return ((tlabel(term_id), doc.get(term_id, 0)) for term_id in term_ids)

def add_attributes(corpus, term_ids, vertex):
    pi = vertex['label']
    doc = corpus[pi]
    for term_label, weight in iterterms(term_ids, doc):
        vertex[term_label] = weight
