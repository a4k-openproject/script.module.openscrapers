# -*- coding: UTF-8 -*-

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

from openscrapers.modules import client
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 32
		self.language = ['en']
		self.domains = ['moviescouch.vip', 'moviescouch.xyz', 'moviescouch.pro', 'moviescouch.pw']
		self.base_link = 'https://moviescouch.vip'
		self.search_link = '/?s=%s'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			search_id = cleantitle.getsearch(title)
			url = urljoin(self.base_link, self.search_link)
			url = url % (search_id.replace(':', ' ').replace(' ', '+'))
			search_results = client.request(url)
			match = re.compile('<article id=.+?href="(.+?)" title="(.+?)"',re.DOTALL).findall(search_results)
			for row_url, row_title in match:
				if cleantitle.get(title) in cleantitle.get(row_title):
					if str(year) in str(row_title):
						return row_url
			return
		except:
			source_utils.scraper_error('MOVIESCOUCH')
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			html = client.request(url)
			links = re.compile('<iframe src="(.+?)"', re.DOTALL).findall(html)
			for link in links:
				try:
					quality = re.compile('<li>Quality: – (.+?)</li>', re.DOTALL).findall(html)[0]
					info = re.compile('<li>Size: – (.+?)</li>', re.DOTALL).findall(html)[0]
				except:
					quality, info = source_utils.get_release_quality(link, link)
				host = link.split('//')[1].replace('www.', '')
				host = host.split('/')[0].split('.')[0].title()
				valid, host = source_utils.is_host_valid(host, hostDict)
				if valid:
					sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': link, 'direct': False, 'debridonly': False})
			return sources
		except:
			source_utils.scraper_error('MOVIESCOUCH')
			return sources


	def resolve(self, url):
		return url