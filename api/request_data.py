import os
import json
import argparse

import requests


URL = 'http://ci4ene01.ecn.purdue.edu/GMU_DIA2/DIA2/site/JSONRPC/query.php'


class InvalidYearMonth(Exception):
    pass


def json_rpc_request(json_content):
    """
    Make the request to the NSF database through the PHP query
    endpoint using the JSON contents passed as the POST body.

    """
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    res = requests.post(URL, json_content, headers=headers)
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


def trigger_caching(year, month, dir_id='05', logical_op='and'):
    params = {
        'logicalOp': str(logical_op),
        'yearMonth': str(year) + '-' + _translate_month(month),
        'directorateID': str(dir_id)
    }
    req_body = {'method': 'Trigger', 'params': params}
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
    trigger_caching(year, month, dir_id, logical_op)
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


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('year', action='store',
            help='the year to get data for')
    parser.add_argument('month', action='store',
            help='the month to get data for')
    parser.add_argument('dir_id', action='store',
            nargs='?', default='05',
            help='the directorate to get data for')

    return parser


def main():
    parser = setup_parser()
    args = parser.parse_args()

    try:
        data = request_data(args.year, args.month, args.dir_id)
    except InvalidYearMonth as err:
        print err


if __name__ == "__main__":
    exit(main())

