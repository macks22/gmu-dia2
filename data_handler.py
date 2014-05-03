"""
This module contains methods used for parsing through the data
by year, month, awardID, etc. It's basically just here to help
with retrieving the files of interest to a particular analysis.

"""
import os


DATA_DIR = os.path.join(os.getcwd(), 'data')
JSON_FILE_LIST = os.listdir(DATA_DIR)
AVAILABLE = {}

# get all available years/months
for filename in JSON_FILE_LIST:
    without_extension = filename.split('.')[0]
    _, year, month = without_extension.split('-')

    if not AVAILABLE.has_key(year):
        AVAILABLE[year] = set(month)
    else:
        AVAILABLE[year] += month


def available_years():
    return AVAILABLE.keys()


def available_months(year):
    return AVAILABLE[year]


def filter_files(year_start, year_end, month_start, month_end):
    """
    Filter the list of JSON files by year and month, allowing
    for a possible range of dates based on month/year.

    @param year_start: first year in range to get
    @type  year_start: int

    @param year_end: last year in range to get
    @type  year_end: int

    @param month_start: first month in range to get
    @type  month_start: int

    @param month_end: last month in range to get
    @type  month_end: int

    """
    years = range(year_start, year_end + 1)
    months = range(month_start, month_end + 1)

    file_list = []
    for year in years:
        for month in months:
            file_list.append(get_file(year, month))

    return file_list


def get_file(year, month):
    """
    Construct a data file name from the month and year.

    """
    year = str(year)
    month = str(month)
    month = '0' + month if len(month) == 1 else month
    filename_pieces = ['docs', year, month]
    filename = '.'.join(filename_pieces)
    full_name = filename + '.json'
    full_path = os.path.join(DATA_DIR, full_name)
    return full_path

