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
import json

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 0
		self.language = ['en']
		self.domain = ['moviemagnet.unblockit.biz']
		self.base_link = 'https://moviemagnet.unblockit.biz'
		self.search_link = '/movies/search_movies?term=%s'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['title']
			year = data['year']

			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', title)

			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			try:
				r = client.request(url)
				if r == str([]):
					return sources
				r = json.loads(r)

				id = ''
				for i in r:
					if i['original_title'] == title and i['release_date'] == year:
						id = i['id']
						break

				if id == '':
					return sources
				link = 'http://moviemagnet.co/movies/torrents?id=%s' % id
				result = client.request(link)
				if 'magnet' not in result:
					return sources

				result = re.sub(r'\n', '', result)
				links = re.findall(r'<tr>.*?<a title="Download:\s*(.+?)"href="(magnet:.+?)">.*?title="File Size">\s*(.+?)\s*</td>', result)

				for link in links:
					name = link[0]
					name = urllib.unquote_plus(name).replace(' ', '.')
					if source_utils.remove_lang(name):
						continue

					t = name.split(year)[0].replace(year, '').replace('(', '').replace(')', '').replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
					if cleantitle.get(t) != cleantitle.get(title):
						continue

					if year not in name:
						continue

					url = link[1]
					url = urllib.unquote(url).decode('utf8').replace('&amp;', '&')
					url = url.split('&tr')[0]

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = link[2]
						div = 1 if size.endswith(('GB', 'GiB')) else 1024
						size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
						size = '%.2f GB' % size
						info.insert(0, size)
					except:
						size = '0'
						pass

					info = ' | '.join(info)

					sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': url,
														'info': info, 'direct': False, 'debridonly': True})
				return sources

			except:
				source_utils.scraper_error('MOVIEMAGNET')
				return sources

		except:
			source_utils.scraper_error('MOVIEMAGNET')
			return sources


	def resolve(self, url):
		return url
