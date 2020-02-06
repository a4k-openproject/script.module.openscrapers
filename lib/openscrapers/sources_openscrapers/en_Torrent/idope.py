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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['idope.se, idope.today']
		self.base_link = 'http://idope.se'
		self.search_link = '/torrent-list/%s/'
		self.min_seeders = 1


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urllib.urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		self.sources = []
		try:
			if url is None:
				return self.sources

			if debrid.status() is False:
				return self.sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			self.title = self.title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
			self.year = data['year']

			query = '%s %s' % (self.title, self.hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			urls = []
			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url)
			urls.append(url)
			urls.append(url + '?p=2')
			# log_utils.log('urls = %s' % urls, log_utils.LOGDEBUG)

			threads = []
			for url in urls:
				threads.append(workers.Thread(self._get_sources, url))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources

		except:
			source_utils.scraper_error('IDOPE')
			return self.sources


	def _get_sources(self, url):
		try:
			r = client.request(url)
			div = client.parseDOM(r, 'div', attrs={'id': 'div2child'})

			for row in div:
				row = client.parseDOM(r, 'div', attrs={'class': 'resultdivbotton'})

				for post in row:
					infohash = re.findall('<div id="hideinfohash.+?" class="hideinfohash">(.+?)<', post, re.DOTALL)[0]
					name = re.findall('<div id="hidename.+?" class="hideinfohash">(.+?)<', post, re.DOTALL)[0]
					name = urllib.unquote_plus(name).replace(' ', '.')
					url = 'magnet:?xt=urn:btih:%s&dn=%s' % (infohash, name)

					if url in str(self.sources):
						continue

					seeders = re.findall('<div class="resultdivbottonseed">(.+?)<', post, re.DOTALL)[0]
					if self.min_seeders > seeders:
						continue

					if source_utils.remove_lang(name):
						continue

					t = name.split(self.hdlr)[0].replace(self.year, '').replace('(', '').replace(')', '').replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
					if cleantitle.get(t) != cleantitle.get(self.title):
						continue

					if self.hdlr not in url:
						continue

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = re.findall('<div class="resultdivbottonlength">(.+?)<', post)[0]
						div = 1 if size.endswith(('GB', 'GiB', 'Gb')) else 1024
						size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
						size = '%.2f GB' % size
						info.insert(0, size)
					except:
						size = '0'
						pass

					info = ' | '.join(info)

					self.sources.append({'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': url, 'info': info,
													'direct': False, 'debridonly': True})

		except:
			source_utils.scraper_error('IDOPE')
			pass


	def resolve(self, url):
		return url