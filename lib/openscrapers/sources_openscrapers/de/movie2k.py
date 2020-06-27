# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 11-23-2018 by JewBMX in Scrubs.
# Only browser checks for active domains.

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    OpenScrapers Project
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re

try: from urlparse import urljoin
except ImportError: from urllib.parse import urljoin
try: from urllib import quote_plus
except ImportError: from urllib.parse import quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.domains = ['movie2k.st', 'movie2k.ac']
		self.base_link = 'http://www.movie2k.st'
		self.search_link = '/search/%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
			if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			query = urljoin(self.base_link, url)
			r = client.request(query)
			r = dom_parser.parse_dom(r, 'div', attrs={'id': 'tab-plot_german'})
			r = dom_parser.parse_dom(r, 'tbody')
			r = dom_parser.parse_dom(r, 'tr')
			for i in r:
				if re.search('(?<=">)(\n.*?)(?=<\/a>)', i[1]).group().strip():
					hoster = re.search('(?<=">)(\n.*?)(?=<\/a>)', i[1]).group().strip()
					link = re.search('(?<=href=\")(.*?)(?=\")', i[1]).group()
					rel = re.search('(?<=oddCell qualityCell">)(\n.*?)(?=<\/td>)', i[1]).group().strip()
					quality, info = source_utils.get_release_quality(rel)
					if not quality:
						quality = 'SD'
					valid, hoster = source_utils.is_host_valid(hoster, hostDict)
					if not valid: continue
					sources.append(
						{'source': hoster, 'quality': quality, 'language': 'de', 'url': link, 'direct': False,
						 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __search(self, titles):
		try:
			query = self.search_link % (quote_plus(quote_plus(cleantitle.query(titles[0]))))
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i]
			r = client.request(query)
			r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'coverBox'})
			r = dom_parser.parse_dom(r, 'li')
			r = dom_parser.parse_dom(r, 'span', attrs={'class': 'name'})
			r = dom_parser.parse_dom(r, 'a')
			title = r[0][1]
			title = cleantitle.get(title)
			if title in t:
				return source_utils.strip_domain(r[0][0]['href'])
			else:
				return
		except:
			return
