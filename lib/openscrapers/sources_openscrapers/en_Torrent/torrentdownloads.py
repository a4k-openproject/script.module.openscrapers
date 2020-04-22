# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers (updated url 4-20-2020)

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
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['torrentdownloads.info', 'torrentdownloads.me', 'torrentdownloads.d4.re']
		self.base_link = 'https://torrentdownloads.info/' # not used anyways
		self.search = 'https://www.torrentdownloads.info/rss.xml?new=1&type=search&cid={0}&search={1}'
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
		self._sources = []
		try:
			if url is None:
				return self._sources

			if debrid.status() is False:
				return self._sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			self.title = self.title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
			self.year = data['year']

			query = '%s %s' % (self.title, self.hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			if 'tvshowtitle' in data:
				url = self.search.format('8', urllib.quote(query))
			else:
				url = self.search.format('4', urllib.quote(query))
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			headers = {'User-Agent': client.agent()}
			_html = client.request(url, headers=headers)

			threads = []
			for i in re.findall(r'<item>(.+?)</item>', _html, re.DOTALL):
				threads.append(workers.Thread(self._get_items, i))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self._sources
		except:
			source_utils.scraper_error('TORRENTDOWNLOADS')
			return self._sources


	def _get_items(self, r):
		try:
			try:
				seeders = int(re.search(r'<seeders>([\d]+)</seeders>', r).groups()[0].replace(',', ''))
				if seeders < self.min_seeders:
					return
			except:
				seeders = 0
				pass

			hash = re.search(r'<info_hash>([a-zA-Z0-9]+)</info_hash>', r).groups()[0]
			name = re.search(r'<title>(.+?)</title>', r).groups()[0]
			name = urllib.unquote_plus(name)
			name = re.sub('[^A-Za-z0-9]+', '.', name).lstrip('.')
			if source_utils.remove_lang(name):
				return

			match = source_utils.check_title(self.title, name, self.hdlr, self.year)
			if not match:
				return

			url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)

			quality, info = source_utils.get_release_quality(name, url)

			try:
				size = re.search(r'<size>([\d]+)</size>', r).groups()[0]
				dsize, isize = source_utils.convert_size(float(size), to='GB')
				info.insert(0, isize)
			except:
				dsize = 0
				pass

			info = ' | '.join(info)

			self._sources.append({'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
												'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
		except:
			source_utils.scraper_error('TORRENTDOWNLOADS')
			pass


	def resolve(self, url):
		return url