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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.genre_filter = ['horror']
		self.domains = ['flimmerstube.com', 'horrorkino.do.am']
		self.base_link = 'http://flimmerstube.com/'
		self.search_link = 'video/shv'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases),
			                                                        year)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			r = client.request(urljoin(self.base_link, url))
			r = re.findall('''vicode\s*=\s*["'](.*?)["'];''', r)[0].decode('string_escape')
			r = dom_parser.parse_dom(r, 'iframe', req='src')
			r = [i.attrs['src'] for i in r]
			for i in r:
				valid, host = source_utils.is_host_valid(i, hostDict)
				if not valid: continue
				sources.append(
					{'source': host, 'quality': 'SD', 'language': 'de', 'url': i, 'direct': False, 'debridonly': False,
					 'checkquality': True})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __search(self, titles, year):
		try:
			t = [cleantitle.get(i) for i in set(titles) if i]
			y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']
			r = client.request(urljoin(self.base_link, self.search_link),
			                   post={'query': cleantitle.query(titles[0])})
			r = dom_parser.parse_dom(r, 'li', attrs={'class': 'entTd'})
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 've-screen'}, req='title')
			r = [(dom_parser.parse_dom(i, 'a', req='href'), i.attrs['title'].split(' - ')[0]) for i in r]
			r = [(i[0][0].attrs['href'], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
			r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
			r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
			r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]
			return source_utils.strip_domain(r)
		except:
			return
