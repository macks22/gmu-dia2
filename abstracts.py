"""
This module contains functions for working with the abstracts
for each award and paring them up with the PIs that worked on
those awards. The envisioned purpose of the functionality is
to enable topic modelling approaches by translating abstracts
into BoW representations and assembling a representative BoW
vector for each PI.

This will allow community detection via topic modelling approaches.

"""
import data


PI_AWD_FRAME, AWD_ABSTRACT_FRAME = _setup_module()


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
            records.append((pi_id, award_id))

    pi_awd_frame = pd.DataFrame(records,
            columns=['pi_id', 'award_id'])
    awd_abstract_frame = pd.DataFrame(records.items(),
            columns=['award_id', 'abstract']).set_index('award_id')

    return pi_awd_frame, awd_abstract_frame


