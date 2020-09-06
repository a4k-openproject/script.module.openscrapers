# -*- coding: utf-8 -*-
# created by Venom for Openscrapers (updated url 4-20-2020)

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
import json

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus, unquote_plus
except ImportError: from urllib.parse import urlencode, quote_plus, unquote_plus

from openscrapers.modules import cfscrape
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domain = ['moviemagnet.co']
		self.base_link = 'http://moviemagnet.co'
		self.search_link = '/movies/search_movies?term=%s'
		self.min_seeders = 1


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'aliases': aliases, 'year': year}
			url = urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		scraper = cfscrape.create_scraper()
		sources = []
		try:
			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['title']
			aliases = data['aliases']
			episode_title = data['title'] if 'tvshowtitle' in data else None
			year = data['year']

			query = re.sub('[^A-Za-z0-9\s\.-]+', '', title)

			url = self.search_link % quote_plus(query)
			url = urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)
			try:
				r = scraper.get(url).content
				if not r:
					return sources
				if any(value in str(r) for value in ['No movies found', 'something went wrong', 'Connection timed out']):
					return sources
				r = json.loads(r)
				id = ''
				for i in r:
					if i['original_title'] == title and i['release_date'] == year:
						id = i['id']
						break
				if id == '':
					return sources
				link = '%s%s%s' % (self.base_link, '/movies/torrents?id=', id)

				result = scraper.get(link).content
				if 'magnet' not in result:
					return sources
				result = re.sub(r'\n', '', result)
				links = re.findall(r'<tr>.*?<a title="Download:\s*(.+?)"href="(magnet:.+?)">.*?title="File Size">\s*(.+?)\s*</td>.*?title="Seeds">([0-9]+|[0-9]+,[0-9]+)\s*<', result)

				for link in links:
					name = link[0]
					name = unquote_plus(name)
					name = source_utils.clean_name(title, name)
					if source_utils.remove_lang(name, episode_title):
						continue

					if not source_utils.check_title(title.replace('&', 'and'), aliases, name, year, year):
						continue

					url = link[1]
					try:
						url = unquote_plus(url).decode('utf8').replace('&amp;', '&').replace(' ', '.')
					except:
						url = unquote_plus(url).replace('&amp;', '&').replace(' ', '.')
					url = url.split('&tr')[0]
					hash = re.compile('btih:(.*?)&').findall(url)[0]

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = link[2]
						dsize, isize = source_utils._size(size)
						info.insert(0, isize)
					except:
						dsize = 0
						pass

					info = ' | '.join(info)

					try:
						seeders = int(link[3].replace(',', ''))
						if self.min_seeders > seeders:
							continue
					except:
						seeders = 0
						pass

					sources.append({'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
												'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
				return sources
			except:
				source_utils.scraper_error('MOVIEMAGNET')
				return sources
		except:
			source_utils.scraper_error('MOVIEMAGNET')
			return sources


	def resolve(self, url):
		return url