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
import urllib
import urlparse

from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['divxcrawler.tv']
		self.base_link = 'http://www.divxcrawler.club'
		self.search_link = '/latest.htm'
		self.search_link2 = '/streaming.htm'
		self.search_link3 = '/movies.htm'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []

			if url is None: return sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			imdb = data['imdb']

			query = urlparse.urljoin(self.base_link, self.search_link)
			result = client.request(query)
			m = re.findall('Movie Size:(.+?)<.+?href="(.+?)".+?href="(.+?)"\s*onMouse', result, re.DOTALL | re.I)
			m = [(i[0], i[1], i[2]) for i in m if imdb in i[1]]
			if m:
				link = m
			else:
				query = urlparse.urljoin(self.base_link, self.search_link2)
				result = client.request(query)
				m = re.findall('Movie Size:(.+?)<.+?href="(.+?)".+?href="(.+?)"\s*onMouse', result, re.DOTALL | re.I)
				m = [(i[0], i[1], i[2]) for i in m if imdb in i[1]]
				if m:
					link = m
				else:
					query = urlparse.urljoin(self.base_link, self.search_link3)
					result = client.request(query)
					m = re.findall('Movie Size:(.+?)<.+?href="(.+?)".+?href="(.+?)"\s*onMouse', result,
					               re.DOTALL | re.I)
					m = [(i[0], i[1], i[2]) for i in m if imdb in i[1]]
					if m: link = m

			for item in link:
				try:

					quality, info = source_utils.get_release_quality(item[2], None)

					try:
						size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', item[0], flags=re.I)[-1]
						div = 1 if size.endswith(('GB', 'GiB')) else 1024
						size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
						size = '%.2f GB' % size
						info.append(size)
					except:
						pass

					info = ' | '.join(info)

					url = item[2]
					if any(x in url.lower() for x in ['.rar.', '.zip.', '.iso.']) or any(
							url.lower().endswith(x) for x in ['.rar', '.zip', '.iso']): raise Exception()

					if any(x in url.lower() for x in ['youtube', 'sample', 'trailer']): raise Exception()
					url = client.replaceHTMLCodes(url)
					url = url.encode('utf-8')

					sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'info': info,
					                'direct': True, 'debridonly': False})
				except:
					pass

			return sources
		except:
			return sources

	def resolve(self, url):
		return url
