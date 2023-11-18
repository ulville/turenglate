#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

# Turenglate : A terminal program to get Turkish-English or
# English-Turkish translations from the online dictionary tureng.com
# Copyright (C) 2022-2023  Ulvican Kahya aka ulville

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from math import floor
import requests
import urllib.parse
from bs4 import BeautifulSoup
import argparse
import argcomplete
from tabulate import tabulate
import shutil
from textwrap import wrap

def tureng_phrase_completer(prefix, parsed_args, **kwargs):
    url = "https://ac.tureng.co/"
    querystring = {"t":urllib.parse.quote(prefix),"l":"entr"}
    return (requests.get(url, params=querystring).json())

parser = argparse.ArgumentParser(
    description='Get Turkish-English or English-Turkish translations from Tureng',
    epilog="Hitting <TAB> twice, after typing a couple of characters for the phrase "
     + "you want to translate, will get the suggestions. If it only has one suggestion, "
     + "a single <TAB> will complete the phrase for you.")
parser.add_argument(
    "-r", "--related", help="show other phrases containing the query phrase", action='store_true')
parser.add_argument(
    "-e", "--english", help="use english header and category names", action='store_true')
parser.add_argument("phrase", nargs='*',
                    help="specify the phrase to translate").completer = tureng_phrase_completer
argcomplete.autocomplete(parser)
args = parser.parse_args()

if args.english:
    lang = 'en/turkish-english/'
    rel_filter = 'other'
else:
    lang = 'tr/turkce-ingilizce/'
    rel_filter = 'terimlerle'

query_raw = ''

if args.phrase:
    query_raw = ' '.join(args.phrase)
    query = urllib.parse.quote(query_raw)
else:
    parser.print_help()
    exit()

base_url = 'https://tureng.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0'}
url = base_url + lang + str(query)
print(url)

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.content, 'lxml')
tables = soup.find_all('table', class_='searchResultsTable')

if tables:
    h2s = soup.find_all('h2')

    table_format = 'fancy_grid'
    terminal_width = shutil.get_terminal_size().columns
    max_col_width = floor((terminal_width - 16) / 3)

    for i, table in enumerate(tables):
        if (not (rel_filter in h2s[i].text)) or args.related:
            print()
            print(h2s[i].text)
            print()

            rows = table.find_all('tr')
            _headers = list(map(lambda cell: cell.text.strip(
                '\n '), rows[0].find_all('th')))
            _headers.pop(0)
            _headers.pop()
            for index, header in enumerate(_headers):
                _headers[index] = '\n'.join(wrap(header, max_col_width))

            tureng_table = []

            for row in rows:
                cells = list(
                    map(lambda cell: cell.text.strip('\n '), row.find_all('td')))

                if (len(cells)) >= 5:
                    cells.pop(0)
                    cells.pop()

                    for index, cell in enumerate(cells):
                        cells[index] = '\n'.join(wrap(cell, max_col_width))

                    tureng_table.append(cells)

            print(tabulate(tureng_table, headers=_headers, tablefmt=table_format))
else:
    message = soup.find('h1')
    print(message.text)
    suggestion_ul = soup.find('ul', class_='suggestion-list')

    if suggestion_ul:
        suggestions = suggestion_ul.find_all('a')

        for suggestion in suggestions:
            print(suggestion.text)
