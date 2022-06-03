#!/usr/bin/env python3

    # Turenglate : A terminal program to get Turkish-English or 
    # English-Turkish translations from the online dictionary tureng.com
    # Copyright (C) 2022  Ulvican Kahya aka ulville

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

import requests
from bs4 import BeautifulSoup
import argparse
from tabulate import tabulate
import os
from textwrap import wrap

parser = argparse.ArgumentParser(description='Get Turkish-English or English-Turkish translations from Tureng')
parser.add_argument("-r", "--related", help = "show other phrases containing the query phrase", action='store_true')
parser.add_argument("-e", "--english", help = "use english header and categorie names", action='store_true')
parser.add_argument("phrase", nargs='*', help = "specify the phrase to translate")
args = parser.parse_args()

if args.english:
    lang = 'en/turkish-english/'
    rel_filter = 'other'
else:
    lang = 'tr/turkce-ingilizce/'
    rel_filter = 'terimlerle'

query = ''

if args.phrase:
    query = ' '.join(args.phrase)
else:
    parser.print_help()
    exit()

base_url = 'https://tureng.com/'
headers = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0'}
url = base_url + lang + str(query)
print(url)

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.content, 'lxml')
tables = soup.find_all('table', class_ = 'searchResultsTable')

if tables:
    h2s = soup.find_all('h2')
    
    table_format = 'fancy_grid'
    terminal_width = os.get_terminal_size().columns
    max_col_width = int(terminal_width / 3) - 5

    for i, table in enumerate(tables):
        if (not (rel_filter in h2s[i].text)) or args.related:
            print()
            print(h2s[i].text)
            print()
            
            rows = table.find_all('tr')
            headers = list(map(lambda cell : cell.text.strip('\n '), rows[0].find_all('th')))
            headers.pop(0)
            headers.pop()
            tureng_table = []

            for row in rows:
                cells = list(map(lambda cell : cell.text.strip('\n '), row.find_all('td')))

                if (len(cells)) >= 5:
                    cells.pop(0)
                    cells.pop()
                    
                    for index, cell in enumerate(cells):
                        cells[index] = '\n'.join(wrap(cell, max_col_width))

                    tureng_table.append(cells)

            print(tabulate(tureng_table, headers = headers, tablefmt=table_format))
else:
    message = soup.find('h1')
    print(message.text)
    suggestion_ul = soup.find('ul', class_ = 'suggestion-list')

    if suggestion_ul:
        suggestions = suggestion_ul.find_all('a')

        for suggestion in suggestions:
            print(suggestion.text)
            
