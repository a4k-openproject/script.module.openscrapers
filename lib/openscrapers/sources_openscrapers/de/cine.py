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

import json
import re

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode
except ImportError: from urllib.parse import urlencode

from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.domains = ['cine.to']
		self.base_link = 'https://cine.to'
		self.request_link = '/request/links'
		self.out_link = '/out/%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			return urlencode({'imdb': imdb})
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if url is None:
				return sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			data = urlencode({'ID': re.sub('[^0-9]', '', str(data['imdb'])), 'lang': 'de'})
			data = client.request(urljoin(self.base_link, self.request_link), post=data, XHR=True)
			data = json.loads(data)
			data = [(i, data['links'][i]) for i in data['links'] if 'links' in data]
			data = [(i[0], i[1][0], (i[1][1:])) for i in data]
			for hoster, quli, links in data:
				valid, hoster = source_utils.is_host_valid(hoster, hostDict)
				if not valid: continue
				for link in links:
					try:
						sources.append(
							{'source': hoster, 'quality': 'SD', 'language': 'de', 'url': self.out_link % link,
							 'direct': False, 'debridonly': False})
					except:
						pass
			return sources
		except:
			return sources

	def resolve(self, url):
		try:
			url = urljoin(self.base_link, url)
			url = client.request(url, output='geturl')
			if self.out_link not in url:
				return url
		except:
			return
