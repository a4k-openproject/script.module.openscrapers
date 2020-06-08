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

from openscrapers.modules import cache
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 2
		self.language = ['en']
		self.domains = ['thekat.app', 'kat.li', 'thekat.info', 'kickass.cm', 'kat.how', 'kickass.vc',
								'kickass2.biz', 'kickass2.st', 'kickasshydra.net', 'kkickass.com',
								'kathydra.com', 'kickasstorrents.id', 'kickasst.net', 'thekat.cc',
								'thekat.ch', 'kickasstorrents.bz', 'kickass-kat.com', 'katcr.co']
		self._base_link = None
		self.search = '/usearch/{0}%20category:movies'
		self.search2 = '/usearch/{0}%20category:tv'
		self.min_seeders = 1


	@property
	def base_link(self):
		if not self._base_link:
			self._base_link = cache.get(self.__get_base_url, 120, 'https://%s' % self.domains[0])
		return self._base_link


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except Exception:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except Exception:
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
		except Exception:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			self._sources = []
			self.items = []

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

			urls = []
			if 'tvshowtitle' in data:
				url = self.search2.format(urllib.quote(query))
			else:
				url = self.search.format(urllib.quote(query))
			url = urlparse.urljoin(self.base_link, url)
			urls.append(url)

			url2 = url + '/2/'
			urls.append(url2)
			# log_utils.log('urls = %s' % urls, log_utils.LOGDEBUG)

			threads = []
			for url in urls:
				threads.append(workers.Thread(self._get_items, url))
			[i.start() for i in threads]
			[i.join() for i in threads]

 			threads2 = []
			for i in self.items:
				threads2.append(workers.Thread(self._get_sources, i))
			[i.start() for i in threads2]
			[i.join() for i in threads2]
			return self._sources

		except:
			source_utils.scraper_error('KICKASS2')
			return self._sources


	def _get_items(self, url):
		try:
			headers = {'User-Agent': client.agent()}
			r = client.request(url, headers=headers)
			posts = client.parseDOM(r, 'tr', attrs={'id': 'torrent_latest_torrents'})

			for post in posts:
				ref = client.parseDOM(post, 'a', attrs={'title': 'Torrent magnet link'}, ret='href')[0]
				link = urllib.unquote(ref).decode('utf8').replace('https://mylink.me.uk/?url=', '').replace('https://mylink.cx/?url=', '')

				name = urllib.unquote_plus(re.search('dn=([^&]+)', link).groups()[0])
				name = re.sub('[^A-Za-z0-9]+', '.', name).lstrip('.')
				if source_utils.remove_lang(name):
					continue

				match = source_utils.check_title(self.title, name, self.hdlr, self.year)
				if not match:
					continue

				try:
					seeders = int(re.findall('<td class="green center">([0-9]+|[0-9]+,[0-9]+)</td>', post, re.DOTALL)[0].replace(',', ''))
					if self.min_seeders > seeders:
						continue
				except:
					seeders = 0
					pass

				try:
					size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', post)[0]
					dsize, isize = source_utils._size(size)
				except:
					isize = '0'
					dsize = 0
					pass

				self.items.append((name, link, isize, dsize, seeders))
			return self.items
		except:
			source_utils.scraper_error('KICKASS2')
			return self.items


	def _get_sources(self, item):
		try:
			name = item[0]
			url = urllib.unquote_plus(item[1]).replace('&amp;', '&').replace(' ', '.')
			url = url.split('&tr')[0]
			url = url.encode('ascii', errors='ignore').decode('ascii', errors='ignore')

			hash = re.compile('btih:(.*?)&').findall(url)[0]

			quality, info = source_utils.get_release_quality(name, url)

			if item[2] != '0':
				info.insert(0, item[2])
			info = ' | '.join(info)

			self._sources.append({'source': 'torrent', 'seeders': item[4], 'hash': hash, 'name': name, 'quality': quality,
											'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': item[3]})
		except:
			source_utils.scraper_error('KICKASS2')
			pass


	def resolve(self, url):
		return url


	def __get_base_url(self, fallback):
		try:
			for domain in self.domains:
				try:
					url = 'https://%s' % domain
					result = client.request(url, limit=1, timeout='5')
					result = re.findall('<title>(.+?)</title>', result, re.DOTALL)[0]
					if result and 'Kickass' in result:
						return url
				except:
					pass
		except:
			pass
		return fallback