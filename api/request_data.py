"""
This script exists to request data from the NSF database managed by Purdue. The
functionality contained herein is capable of getting NSF grant award history,
including information about the investigators and POs for each award, as well as
the organizations with which those individuals are affiliated with.

"""
import os
import sys
import time
import logging
import argparse
import requests

try:
    # roughly 2x faster
    import ujson as json
except ImportError:
    # builtin
    import json


URL = 'http://ci4ene01.ecn.purdue.edu/GMU_DIA2/DIA2/site/JSONRPC/query.php'


class InvalidYearMonth(Exception):
    """Raise if data is requested for a year/month no data exists for."""
    pass


def json_rpc_request(json_content):
    """
    Make a POST request to the NSF database through the PHP query
    endpoint using the JSON contents passed as the body.

    """
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    res = requests.post(URL, json_content, headers=headers)
    logging.debug(res.content)
    return res.json()

def _translate_month(month):
    """
    All months need to be two digit, so add a zero if less than 10.

    @type  month: int or str
    @param month: month to translate.

    @rtype:  str
    @return: The translated month.

    """
    month = str(month)
    return '0' + month if len(month) == 1 else month


def _trigger_award_caching(year, month, dir_id='05', logical_op='and'):
    params = {
        'logicalOp': str(logical_op),
        'yearMonth': str(year) + '-' + _translate_month(month),
        'directorateID': str(dir_id)
    }
    req_body = {'method': 'Trigger', 'params': params}
    return json_rpc_request(json.dumps(req_body))


def _trigger_name_caching(pi_id, logical_op='and'):
    params = {
        'logicalOp': str(logical_op),
        'personID': str(pi_id)
    }
    req_body = {'method': 'Trigger', 'params': params}
    return json_rpc_request(json.dumps(req_body))


def get_name_and_affiliation(pi_id, logical_op='and'):
    """
    Get the name of a PI by the disambiguated ID.

    @type  pi_id: int or str
    @param pi_id: ID of the PI to get the name of.

    @type  logical_op: str
    @param logical_op: How to combine the various query parameters.

    @rtype:  dict
    @return: The name of the PI if any, decoded from the JSON response.

    """
    _trigger_name_caching(pi_id, logical_op)
    params = {
        'logicalOp': str(logical_op),
        'personID': str(pi_id)
    }
    req_body = {'method': 'getNameGMU', 'params': params}
    return json_rpc_request(json.dumps(req_body))


def get_names(pi_id_file, logical_op='and'):
    """
    Get the name of a PI by the disambiguated ID.

    @type  pi_id: int or str
    @param pi_id: ID of the PI to get the name of.

    @type  logical_op: str
    @param logical_op: How to combine the various query parameters.

    @rtype:  dict
    @return: The names of the PIs, decoded from the JSON response.

    """
    with open(pi_id_file, 'r') as f:
        pi_ids = [pi_id for pi_id in f]

    params = {
        'logicalOp': str(logical_op),
        'personIDs': pi_ids
    }
    req_body = {'method': 'getNames', 'params': params}
    return json_rpc_request(json.dumps(req_body))


def get_title_and_abstract(doc_id):
    """
    Get the title and abstract for the specified document.

    @type  doc_id: str
    @param doc_id: The ID of the document to retreive the title and
        abstract for.

    @rtype:  dict
    @return: Dictionary with 'title' and 'abstract' fields.

    """
    req_body = {'method': 'getOneTitleAbstract', 'params': doc_id}
    res = json_rpc_request(json.dumps(req_body))
    return res['result']['data']


def write_data(data, year, month, dir_id):
    """
    Write the data to a file named based on the month, year,
    and directorate it contains awards for::

        docs-<year>-<month>

    @type  data: dict (json)
    @param data: The JSON formattable data to write to a file.

    @type  year: str or int
    @param year: The month the data contains awards for.

    @type  month: str or int
    @param month: The year the data contains awards for.

    @type  dir_id: str
    @param dir_id: The directorate the data contains awards for.

    """
    filename = '-'.join(['docs', str(year), str(month)]) + '.json'
    path = os.path.abspath(filename)
    with open(path, 'w') as json_file:
        json.dump(data, json_file)


def validate_year_and_month(year, month):
    """
    Make sure the requested year and month falls within the
    allowable time range of 1995-01 to 2014-02.

    @raises InvalidYearMonth: If the year/month is outside the
        allowable time range.

    """
    year = int(year)
    month = int(month)
    if year > 2014 or year < 1995:
        raise InvalidYearMonth('There is only data from 1995 to 2014')
    elif year == 2014 and month > 2:
        raise InvalidYearMonth('There is only data up until 2014-02')


def request_data(year, month, dir_id='05', mode='current', logical_op='and'):
    """
    Request data from DIA2 by year, month, and directorate. Before
    making each request, the trigger method is used to build cache
    files (for efficient access, I presume?).

    @type  year: int or str
    @param year: The year to request data for.

    @type  month: int or str
    @param month: The month to request data for.

    @type  dir_id: str
    @param dir_id: ID of the directorate to get data for.

    @type  mode: str
    @param mode: This indicates how to handle modified awards.
        It is current by default, which means keep only the newest
        status of modified awards, so as to reduce complexity::

        mode indicate the document disambiguation status
        default mode is "disambiguated"
        disambiguated: nonColModDocIDs
        all: dupDocIDs
        current: nonModOriDocIDs
        collab: nonModDocIDs
        ori: oriDocIDs

    @type  logical_op: str
    @param logical_op: how to combine the query parameters. This is
        set to 'and' by default, which indicates that only data with
        the specified directorate AND the specified month AND the
        specified year should be returned.

    @rtype:  dict
    @return: The awards which matched the query results. By default,
        this will be awards that matched the specified month, year,
        and directorate.

    @raises InvalidYearMonth: If the year/month is outside the
        allowable time range.

    """
    validate_year_and_month(year, month)
    month = _translate_month(month)
    _trigger_award_caching(year, month, dir_id, logical_op)
    params = {
        'logicalOp': str(logical_op),
        'mode': str(mode),
        'yearMonth': str(year) + '-' + month,
        'directorateID': dir_id
    }
    req_body = {'method': 'GMUDataTransfer', 'params': params}
    res = json_rpc_request(json.dumps(req_body))
    data = res['result']['data']

    # We now have the basic award info; let's also get abstract and title.
    for doc_id in data:
        title_and_abstract = get_title_and_abstract(doc_id)
        data[doc_id]['title'] = title_and_abstract['title']
        data[doc_id]['abstract'] = title_and_abstract['abstract']

    # Now write the data to a JSON file and return it.
    write_data(data, year, month, dir_id)
    return data


def write_name_and_affiliation(pi_id):
    """
    Write the name and affiliation info for the given PI to a JSON file named
    using this convention::

        <pi_id>-name-affiliation.json'

    @param str pi_id: The PI ID to get and write name and affiliation info for.
    @raise TypeError: If the ID of the PI is not parseable as an int.

    """
    pi_id = str(int(pi_id))  # raise TypeError if bad ID & strip in the process
    out_format = '{}-name-affiliation.json'

    # TODO: STORE SOMEWHERE BETTER
    json_dir = os.path.abspath('json')
    path = os.path.join(json_dir, out_format.format(pi_id))
    json_data = get_name_and_affiliation(pi_id)
    with open(path, 'w') as f:
        json.dump(json_data, f)


def name(args):
    """Main CLI for 'name' subcommand."""

    if args.id:
        try:
            write_name_and_affiliation(args.id)
        except ValueError:
            return 2

        return 0

    elif args.file:
        # read requested pids from file
        infile = os.path.abspath(args.file)
        with open(infile, 'r') as f:
            pi_ids = set(f.read().split())

        # get listing of those we already have
        files = os.listdir('json')
        pids_we_have = set([name.split('-')[0] for name in files])

        # narrow down to those we don't have
        pi_ids.difference_update(pids_we_have)

        logging.info('Requesting data for {} PIs'.format(len(pi_ids)))
        num_processed = 0
        for pi_id in pi_ids:
            try:
                write_name_and_affiliation(pi_id)
                num_processed += 1
                logging.info('Got name/affiliation info for {}.'.format(pi_id))
                logging.info('{} Processed.'.format(num_processed))
            except ValueError as err:
                logging.error(str(err))
                logging.error('Unable to parse PI ID: ' + pi_id)

                if args.delay:
                    time.sleep(args.delay)
        return 0
    return 1


def download(args):
    """Main CLI for 'download' subcommand."""
    try:
        data = request_data(args.year, args.month, args.dir_id)
    except InvalidYearMonth as err:
        print err
        return 1
    return 0


def setup_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help='valid subcommands')

    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='change log level to debug')

    download_parser = subparsers.add_parser(
        'download', help='download award data for a year/month')
    download_parser.add_argument(
        'year', action='store',
        help='the year to get data for')
    download_parser.add_argument(
        'month', action='store',
        help='the month to get data for')
    download_parser.add_argument(
        'dir_id', action='store',
        nargs='?', default='05',
        help='the directorate to get data for')
    download_parser.set_defaults(func=download)

    name_parser = subparsers.add_parser(
        'name', help='get people names and affiliations')
    name_parser.add_argument(
        'id', nargs='?', default='',
        help='the person ID to get name info for')
    name_parser.add_argument(
        '-f', '--file', action='store', default='',
        help='file of PI IDs, one per line, to get names for')
    name_parser.add_argument(
        '-d', '--delay', action='store', default=0, type=float,
        help='seconds to delay between requests for PIs.')
    name_parser.set_defaults(func=name)

    return parser


def main():
    parser = setup_parser()
    args = parser.parse_args()

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # set up logging to console
    logging.basicConfig(
        level=log_level,
        format='[%(levelname)s\t%(asctime)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

    exit_code = args.func(args)
    if exit_code:
        parser.print_usage()
    return exit_code


if __name__ == "__main__":
    exit(main())
