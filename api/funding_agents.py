"""
This module contains functions for answering questions about the
funding agents for the NSF awards dataset. In particular, it is
useful for answering questions like:

    - How many unique programs his this PI worked on? Which ones?
    - Which programs have these two PIs worked on together?
    - How many directorates/divisons/programs are in the dataset?
    - Who has the most awards?
    - Which division has given out the most awards?
    - Which programs have the most PIs in common?

"""
import os
import numpy
import itertools

import parser


class FundingAgentExplorer(object):
    """Answer questions about NSF award funding agents."""

    def __init__(self):
        """
        Parse the funding agents from the raw JSON files using the
        parser module, then set up the hierarchy level selectors.

        """
        self._df = parser.parse_funding_agents()
        self._selectors = {
            'dir': ['dir_id', 'dir_abbr', 'dir_name'],
            'div': ['div_id', 'div_abbr', 'div_name'],
            'pgm': ['pgm_id', 'pgm_name'],
            'awd': ['award_id']
        }
        self._selectors['all'] = list(itertools.chain.from_iterable(
            self._selectors.values()))

    def available_selectors(self):
        """
        Return a list of all available selectors. These are all
        valid values for the `level` param in the `_filter_by_level`
        method.

        @rtype:  list of str
        @return: list of all available hierarchy level selectors

        """
        return self._selectors.keys()

    def selector(self, key):
        """
        Return the list of column names that will be used, given the
        key value as the hierarchy level selector.

        @type  key: str
        @param key: hierarchy level selector to use; see
            L{FundingAgentExplorer.available_selectors} for valid
            values.

        @rtype:  list of str
        @return: list of column names that will be used for the given
            selector

        @raise KeyError: if the key used is not a valid selector

        """
        return self._selectors[key]

    def directorates(self, pi_ids=None, agg='shared'):
        """
        Retreive all distinct directorates the PI has been involved with.

        @type  pi_ids: int, str, unicode, or list of those
        @param pi_ids: single pi id or list of pi ids to filter by

        @type  agg: str
        @param agg: aggregation method to use when filtering by pi ids::

            'total': returns all directorates, with freq values based
                on how many occurences showed up for the all PIs
                passed
            'shared': returns only directorates which every PI has
                been funded by

        @rtype:  L{pandas.DataFrame}
        @return: the filtered data frame with only the columns
            returned by the directorate hierarchy level selector

        """
        return self._records_for_pis(pi_ids, 'dir', agg)

    dirs = directorates

    def divisions(self, pi_ids=None, agg='shared', dirs=''):
        """
        Retreive all distinct divisions the PI has been funded by.

        @type  pi_ids: int, str, unicode, or list of those
        @param pi_ids: single pi id or list of pi ids to filter by

        @type  agg: str
        @param agg: aggregation method to use when filtering by pi ids::

            'total': returns all divisions, with freq values based
                on how many occurences showed up for the all PIs
                passed
            'shared': returns only divisions which every PI has
                been funded by

        @type  dirs: str, unicode, int, or list of these
        @param dirs: the directorate id or list of directorate ids
            to filter by.

        @rtype:  L{pandas.DataFrame}
        @return: the filtered data frame with only the columns
            returned by the division hierarchy level selector

        """
        if dirs:
            records = self.filter(self._df, 'dir', dirs)
        else:
            records = self._df

        return self._records_for_pis(pi_ids, 'div', agg, records)

    divs = divisions

    def programs(self, pi_ids=None, agg='shared', dirs='', divs=''):
        """
        Retrieve all programs the PI has worked on.

        @type  pi_ids: int, str, unicode, or list of those
        @param pi_ids: single pi id or list of pi ids to filter by

        @type  agg: str
        @param agg: aggregation method to use when filtering by pi ids::

            'total': returns all programs, with freq values based
                on how many occurences showed up for the all PIs
                passed
            'shared': returns only programs which every PI has
                been funded by

        @type  dirs: str, unicode, int, or list of these
        @param dirs: the directorate id or list of directorate ids
            to filter by

        @type  divs: str, unicode, int, or list of these
        @param divs: the division id or list of division ids to
            filter by

        @rtype:  L{pandas.DataFrame}
        @return: the filtered data frame with only the columns
            returned by the program hierarchy level selector

        """
        if dirs:
            records = self.filter(self._df, 'dir', dirs)
        else:
            records = self._df

        if divs:
            records = self.filter(records, 'div', divs)
        else:
            records = records

        return self._records_for_pis(pi_ids, 'pgm', agg, records)

    pgms = programs

    def awards(self, pi_ids=None, agg='shared'):
        """
        Retrieve the records for all awards which the given PIs have
        worked on together.

        @type  pi_ids: int, str, unicode, or list of those
        @param pi_ids: single pi id or list of pi ids to filter by

        @type  agg: str
        @param agg: aggregation method to use when filtering by pi ids::

            'total': returns all award ids, with freq values based
                on how many occurences showed up for the all PIs
                passed
            'shared': returns only award ids for awards which every
                PI has worked on

        """
        return self._records_for_pis(pi_ids, 'awd', agg)

    def unique_values(self, col_name):
        """
        Return all unique values for the given column name.

        @type  col_name: str
        @param col_name: the index of the column to return unique
            values for

        """
        return self._df[col_name].unique()

    def _records_for_pis(self, pi_ids, level, agg, frame=None):
        """
        Retrieve all records for the given PI ID or list of PI IDs.

        @type  pi_ids: str, unicode, list of str, or None
        @param pi_ids: the PI id or list of PI ids to retrieve records
            for; if None, all PIs and an aggregation method of 'total'
            are assumed

        @type  level: str
        @param level: the level in the funding agent hierarchy to select
            from; see the L{FundingAgentExplorer.available_selectors}
            method for valid options.

        @type  agg: str
        @param agg: method of aggregation to use; currently 'total' and
            'shared' are supported. 'total' returns all award instances
            where _any_ of the PI ids show up with the frequencies of
            occurence; 'shared' filters down to only those where _all_ PI
            ids show up.

        @rtype:   L{pandas.DataFrame}
        @return:  The DataFrame records remaining after selecting and
            filtering based on the parameters

        @raise KeyError: if passed an invalid agg value

        """
        df = self._df if frame is None else frame

        if pi_ids is None:
            pi_ids = df['pi_id'].values
            agg = 'total'
        elif type(pi_ids) != list and type(pi_ids) != numpy.ndarray:
            pi_ids = [str(pi_ids)]
        else:
            pi_ids = [str(pi_id) for pi_id in pi_ids]

        if agg == 'total':
            all_records = df
        else:
            selector = df['pi_id'].isin(pi_ids)
            all_records = df[selector]

        records = self._filter_by_level(all_records, level)

        if agg == 'total':
            return records.reset_index(drop=True)
        elif agg == 'shared':
            num_pis = len(pi_ids)
            shared = records[records['freq'] == num_pis].drop('freq', 1)
            return shared.reset_index(drop=True)
        else:
            raise KeyError("agg can be one of {'total', 'shared'}")

    def _filter_by_level(self, records, level):
        """
        Filter the records in the frame passed in based on the level
        in the funding agent hierarchy.

        @type  records:   L{pandas.DataFrame}
        @param records: data frame with records to be filtered

        @type  level: str
        @param level: level of funding agent hierarchy to filter by

        @rtype:  L{pandas.DataFrame}
        @return: the filtered data frame

        """
        cols = self._selectors[level]
        id_field = cols[0]
        filtered = records[cols]
        counts = filtered.groupby(id_field)[id_field].transform('count')
        filtered['freq'] = counts
        filtered = filtered.sort('freq', ascending=False)
        return filtered.drop_duplicates()

    def filter(self, frame, level, value):
        """
        Filter a data frame by the column name using the value or
        list of values passed. In other words, return only records
        where the column name is equal to the value or one of the
        values passed.

        Note that no attributes are removed, only records.

        @type  frame: L{pandas.DataFrame}
        @param frame: data frame to filter by level value

        @type  level: str
        @param level: one of {'dir', 'div', 'pgm'}

        @type  value: str, unicode, int or list of these
        @param value: single id or list of ids to filter by

        @rtype:  L{pandas.DataFrame}
        @return: filtered data frame

        @raise KeyError: if the level is not a valid option

        """
        if type(value) != list and type(value) != numpy.ndarray:
            values = [str(value)]
        else:
            values = [str(val) for val in value]

        if level == 'dir':
            filtered = frame[frame['dir_id'].isin(values)]
        elif level == 'div':
            filtered = frame[frame['div_id'].isin(values)]
        elif level == 'pgm':
            filtered = frame[frame['pgm_id'].isin(values)]
        else:
            raise KeyError("level must be one of {'dir', 'div','pgm'}")

        return filtered.reset_index(drop=True)

