"""
This module contains functions for working with the abstracts
for each award and paring them up with the PIs that worked on
those awards. The envisioned purpose of the functionality is
to enable topic modelling approaches by translating abstracts
into BoW representations and assembling a representative BoW
vector for each PI.

This will allow community detection via topic modelling approaches.

"""
import os
import cPickle as pickle

import gensim
import pandas as pd

import data
import doctovec


# -----------------------------------------------------------------------------
# MODULE SETUP
# -----------------------------------------------------------------------------
def _setup_module():
    """
    Parse the data into data frames.

        1. award/abstract pairings
        2. pi/award pairings

    """
    awd_abstract_pairings = []
    pi_awd_pairings = []
    for award_data in data.awards():
        award_id = str(award_data['awardID'])
        pi_list = [str(pi_id) for pi_id in award_data['PIcoPI']]
        abstract = award_data['abstract'].encode('utf-8')

        # add a record for the award/abstract pairing
        awd_abstract_pairings.append((award_id, abstract))

        # add a record for each pi/award pairing
        for pi_id in pi_list:
            pi_awd_pairings.append((pi_id, award_id))

    pi_awd_frame = pd.DataFrame(pi_awd_pairings,
            columns=['pi_id', 'award_id'])
    awd_abstract_frame = pd.DataFrame(awd_abstract_pairings,
            columns=['award_id', 'abstract'])

    return pi_awd_frame, awd_abstract_frame


PI_AWD_FRAME, AWD_ABSTRACT_FRAME = _setup_module()
# -----------------------------------------------------------------------------


def get_abstracts(pi_id):
    """
    Get all abstracts for a particular PI. This gets a list
    of all the abstracts for each award this PI has worked on.

    @param pi_id: ID of the PI to get abstracts for.
    @type  pi_id: str, unicode, or int

    @returns: list of abstracts
    @rtype:   L{numpy.ndarray} of str

    """
    selector = PI_AWD_FRAME['pi_id'] == str(pi_id)
    joined = PI_AWD_FRAME[selector].merge(AWD_ABSTRACT_FRAME, on='award_id')
    return joined['abstract'].values


def awards_for_pi(pi_id):
    """
    Retrieve the list of all awards for the PI.

    @param pi_id: ID of the PI to get awards for
    @type  pi_id: str, unicode, or int

    """
    selector = PI_AWD_FRAME['pi_id'] == pi_id
    return PI_AWD_FRAME[selector]['award_id'].values


def vectorize(awards=None, write_vec=False, pickle_vec=True):
    """
    Lookup abstracts based on the awards they were written for.  For
    each award in the list, parse the abstract into a vector of words
    (tokenized, cleaned, and stemmed). Store all in a dictionary
    indexed by award ids.

    If no list of award IDs is passed in, all will be used.
    Optionally write each vector to a text file.
    Optionally pickle each vector for quick loading later.

    @param awards: list of award IDs to parse abstracts for
    @type  awards: list of str

    @param write_vec: whether or not to write the abstract vectors
    @type  write_vec: bool

    @param pickle_vec: whether or not to pickle the abstract vectors
    @type  pickle_vec: bool

    @returns: dictionary of (award: vectorized abstract) pairs
    @rtype:   dict of (list of str)

    """
    if awards is not None:
        selector = AWD_ABSTRACT_FRAME['award_id'].isin(awards)
        df = AWD_ABSTRACT_FRAME[selector]
    else:
        df = AWD_ABSTRACT_FRAME

    for award_id, abstract in df.values:
        vec = doctovec.vectorize(abstract)
        records[award_id] = vec

        if write_vec:
            data.write_abstract_vec(vec, award_id)

        if pickle_vec:
            data.save_abstract_vec(vec, award_id)

        abstracts_parsed +=1
        print abstracts_parsed

    print "Total # abstracts parsed: {}".format(abstracts_parsed)
    return records


def bow_for_pi(pi_id, parse=False):
    """
    Get the representative BoW frequency distribution for the PI. By
    default, load the BoW from a saved file. This can be overriden by
    setting `parse` = True.

    @param pi_id: the ID of the PI to parse the BoW for
    @type  pi_id: str

    @param parse: whether or not to parse the BoW from the raw data; by
                  default, this is False, which means the BoW is loaded
                  from a saved file.
    @type  parse: bool

    @returns: the BoW frequency distribution parsed
    @rtype:   L{gensim.corpora.dictionary.Dictionary}

    """
    abstracts = []
    awards = awards_for_pi(pi_id)

    if parse:

        # get all pre-parsed abstracts from their pickle files
        for award_id in awards:
            abstracts.append(data.load_abstract_vec(award_id))

        # parse documents into BoW representation
        bow = gensim.corpora.dictionary.Dictionary(abstracts)
    else:
        bow = data.read_bow(pi_id)

    return bow


def parse_bow(pi_ids=None, write=True):
    """
    For each PI in the dataset, parse out the list of abstracts (one for each
    award worked on) into a BoW frequency distribution. Optionally write the
    BoW to a text file.

    @param pi_ids: list of PI IDs to parse BoWs for; if none is passed, all
                   will be used
    @type  pi_ids: list of str

    @param write: whether or not to write the abstract vectors
    @type  write: bool

    """
    if pi_ids is not None:
        selector = PI_AWD_FRAME['pi_id'].isin(pi_ids)
        df = PI_AWD_FRAME[selector]
    else:
        df = PI_AWD_FRAME

    pis_parsed = 0
    for pi_id in df.values:
        abstracts = []
        awards = awards_for_pi(pi_id)

        # get all pre-parsed abstracts from their pickle files
        for award_id in awards:
            abstracts.append(data.load_abstract_vec(award_id))

        # parse documents into BoW representation
        bow = gensim.corpora.dictionary.Dictionary(abstracts)

        # write BoW to text files for this PI
        if write:
            data.write_bow(bow, pi_id)

        pis_parsed += 1
        print pis_parsed

    print "Total # PIs parsed: {}".format(pis_parsed)


if __name__ == "__main__":
    parse_bow()

