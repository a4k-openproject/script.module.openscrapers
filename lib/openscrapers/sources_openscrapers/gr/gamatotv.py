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
from openscrapers.modules import trakt


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['gr']
		self.domains = ['gamatotv.co', 'gamatotv.me']
		self.base_link = 'http://gamatotv.co'
		self.search_link = '/groups/group/search?q=%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
			if not url: url = self.__search(self.search_link + trakt.getMovieTranslation(imdb, 'el'), year)
			return url
		except:
			return

	def __search(self, titles, year):
		try:
			query = self.search_link % (quote_plus(cleantitle.getsearch(titles[0] + ' ' + year)))
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i][0]
			r = client.request(query)
			r = client.parseDOM(r, 'div', attrs={'class': 'bd'})
			for i in r:
				r = dom_parser.parse_dom(i, 'h3')
				r = dom_parser.parse_dom(r, 'a')
				title = r[0][1]
				y = re.findall('(\d{4})', title, re.DOTALL)[0]
				title = cleantitle.get(title.split('(')[0])
				if title in t and year == y:
					return source_utils.strip_domain(r[0][0]['href'])
			return
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			query = urljoin(self.base_link, url)
			r = client.request(query)
			links = client.parseDOM(r, 'div', attrs={'class': 'xg_user_generated'})
			links = dom_parser.parse_dom(links, 'a')
			for i in links:
				url = i[0]['href']
				if 'youtube' in url: continue
				quality = 'SD'
				lang, info = 'gr', 'SUB'
				valid, host = source_utils.is_host_valid(url, hostDict)
				if 'hdvid' in host: valid = True
				if not valid: continue
				sources.append({'source': host, 'quality': quality, 'language': lang, 'url': url, 'info': info,
				                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
