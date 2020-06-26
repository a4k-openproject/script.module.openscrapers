# -*- coding: utf-8 -*-

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

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 31
		self.language = ['en']
		self.domains = ['filmxy.nl', 'filmxy.me', 'filmxy.one', 'filmxy.ws', 'filmxy.live']
		self.base_link = 'https://www.filmxy.nl'
		self.search_link = '/%s-%s'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title)
			url = urljoin(self.base_link, (self.search_link % (title, year)))
			return url
		except:
			source_utils.scraper_error('FILEXY')
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []

			if url is None:
				return sources
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'}
			result = self.scraper.get(url, headers=headers).content
			streams = re.compile('data-player="&lt;[A-Za-z]{6}\s[A-Za-z]{3}=&quot;(.+?)&quot;', re.DOTALL).findall(
				result)

			for link in streams:
				quality = source_utils.check_url(link)
				host = link.split('//')[1].replace('www.', '')
				host = host.split('/')[0].lower()

				if quality == 'SD':
					sources.append({'source': host, 'quality': '720p', 'info': '', 'language': 'en', 'url': link, 'direct': False,
					                'debridonly': False})
				else:
					sources.append({'source': host, 'quality': quality, 'info': '', 'language': 'en', 'url': link, 'direct': False,
					                'debridonly': False})

			return sources
		except:
			source_utils.scraper_error('FILEXY')
			return sources

	def resolve(self, url):
		return url