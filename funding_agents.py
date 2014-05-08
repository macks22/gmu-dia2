"""
This module contains functions for answering questions about the
funding agents for the NSF awards dataset. In particular, it is
useful for answering questions like:

    * How many unique programs his this PI worked on? Which ones?
    * Which programs have these two PIs worked on together?
    * How many directorates/divisons/programs are in the dataset?
    * Who has the most awards?
    * Which division has given out the most awards?
    * Which programs have the most PIs in common?

"""
import os
import numpy
import itertools

import parser


DF = parser.parse_funding_agents()
SELECTORS = {
    'dir': ['dir_id', 'dir_abbr', 'dir_name'],
    'div': ['div_id', 'div_abbr', 'div_name'],
    'pgm': ['pgm_id', 'pgm_name'],
    'awd': ['award_id']
}
# fa = funding agent
SELECTORS['fa'] = list(itertools.chain.from_iterable(
    SELECTORS.values()))


def programs(pi_ids=None, agg='shared'):
    """
    Retrieve all programs the PI has worked on.

    """
    return _records_for_pis(pi_ids, 'pgm', agg)

pgms = programs


def divisions(pi_ids=None, agg='shared'):
    """
    Retreive all distinct divisions the PI has been funded by.

    """
    return _records_for_pis(pi_ids, 'div', agg)

divs = divisions


def directorates(pi_ids=None, agg='shared'):
    """
    Retreive all distinct directorates the PI has been involved with.

    """
    return _records_for_pis(pi_ids, 'dir', agg)

dirs = directorates


def awards(pi_ids=None, agg='shared'):
    """
    Retrieve the records for all awards which the given PIs have
    worked on together.

    """
    return _records_for_pis(pi_ids, 'awd', agg)


def unique_values(col_name):
    """
    Return an array of all unique values for the given column name.

    """
    return DF[col_name].unique()


def _records_for_pis(pi_ids, level, agg):
    """
    Retrieve all records for the given PI ID or list of PI IDs.

    """
    if pi_ids is None:
        pi_ids = DF['pi_id'].values
        agg = 'total'
    elif type(pi_ids) != list and type(pi_ids) != numpy.ndarray:
        pi_ids = [pi_ids]

    pi_ids = [str(pi_id) for pi_id in pi_ids]
    all_records = DF if agg == 'total' else DF[DF['pi_id'].isin(pi_ids)]
    records = _filter_by_level(all_records, level)

    if agg == 'total':
        return records.reset_index(drop=True)
    elif agg == 'shared':
        num_pis = len(pi_ids)
        shared = records[records['freq'] == num_pis].drop('freq', 1)
        return shared.reset_index(drop=True)


def _filter_by_level(records, level):
    cols = SELECTORS[level]
    id_field = cols[0]
    filtered = records[cols]
    counts = filtered.groupby(id_field)[id_field].transform('count')
    filtered['freq'] = counts
    filtered = filtered.sort('freq', ascending=False)
    return filtered.drop_duplicates()

