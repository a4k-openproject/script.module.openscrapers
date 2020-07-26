# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers (updated url 7-12-2020)

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

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus, unquote, unquote_plus
except ImportError: from urllib.parse import urlencode, quote_plus, unquote, unquote_plus


from openscrapers.modules import cache
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 2
		self.language = ['en']
		self.domains = ['thekat.app', 'kat.li', 'thekat.info', 'kickass.cm', 'kickass.ws',
								'kickasshydra.net', 'kkickass.com', 'kathydra.com', 'kickass.onl',
								'kickasstorrents.id', 'kickasst.net', 'thekat.cc', 'kkat.net',
								'thekat.ch', 'kickasstorrents.bz', 'kickass-kat.com']
		self._base_link = None
		self.search = '/usearch/{0}%20category:movies'
		self.search2 = '/usearch/{0}%20category:tv'
		self.min_seeders = 0
		self.pack_capable = True

	@property
	def base_link(self):
		if not self._base_link:
			self._base_link = cache.get(self.__get_base_url, 120, 'https://%s' % self.domains[0])
		return self._base_link


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'aliases': aliases, 'year': year}
			url = urlencode(url)
			return url
		except Exception:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'aliases': aliases, 'year': year}
			url = urlencode(url)
			return url
		except Exception:
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			url = parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urlencode(url)
			return url
		except Exception:
			return


	def sources(self, url, hostDict, hostprDict):
		self.sources = []
		try:
			if url is None:
				return self.sources
			if debrid.status() is False:
				return self.sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			self.title = self.title.replace('&', 'and').replace('Special Victims Unit', 'SVU')
			self.aliases = data['aliases']
			self.episode_title = data['title'] if 'tvshowtitle' in data else None
			self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
			self.year = data['year']

			query = '%s %s' % (self.title, self.hdlr)
			query = re.sub('[^A-Za-z0-9\s\.-]+', '', query)

			urls = []
			if 'tvshowtitle' in data:
				url = self.search2.format(quote_plus(query))
			else:
				url = self.search.format(quote_plus(query))
			url = urljoin(self.base_link, url)
			urls.append(url)

			# url2 = url + '/2/'
			# urls.append(url2)

			threads = []
			for url in urls:
				threads.append(workers.Thread(self.get_sources, url))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('KICKASS2')
			return self.sources


	def get_sources(self, url):
		# log_utils.log('url = %s' % url, __name__, log_utils.LOGDEBUG)
		try:
			headers = {'User-Agent': client.agent()}
			r = client.request(url, headers=headers)
			if not r:
				return
			posts = client.parseDOM(r, 'tr', attrs={'id': 'torrent_latest_torrents'})

			for post in posts:
				ref = client.parseDOM(post, 'a', attrs={'title': 'Torrent magnet link'}, ret='href')[0]
				link = ref.split('url=')[1]

				url = unquote_plus(link).replace('&amp;', '&').replace(' ', '.')
				url = url.split('&tr')[0]
				hash = re.compile('btih:(.*?)&').findall(url)[0]
				name = unquote_plus(url.split('&dn=')[1])
				name = source_utils.clean_name(self.title, name)
				if source_utils.remove_lang(name, self.episode_title):
					continue

				if not source_utils.check_title(self.title, self.aliases, name, self.hdlr, self.year):
					continue

				# filter for episode multi packs (ex. S01E01-E17 is also returned in query)
				if self.episode_title:
					if not source_utils.filter_single_episodes(self.hdlr, name):
						continue

				try:
					seeders = int(re.findall('<td class="green center">([0-9]+|[0-9]+,[0-9]+)</td>', post, re.DOTALL)[0].replace(',', ''))
					if self.min_seeders > seeders:
						continue
				except:
					seeders = 0
					pass

				quality, info = source_utils.get_release_quality(name, url)

				try:
					size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', post)[0]
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except:
					dsize = 0
					pass

				info = ' | '.join(info)

				self.sources.append({'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
											'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
		except:
			source_utils.scraper_error('KICKASS2')
			pass


	def sources_packs(self, url, hostDict, hostprDict, search_series=False, total_seasons=None, bypass_filter=False):
		self.sources = []
		try:
			self.search_series = search_series
			self.total_seasons = total_seasons
			self.bypass_filter = bypass_filter

			if url is None:
				return self.sources
			if debrid.status() is False:
				return self.sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			self.title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU')
			self.aliases = data['aliases']
			self.imdb = data['imdb']
			self.year = data['year']
			self.season_x = data['season']
			self.season_xx = self.season_x.zfill(2)

			query = re.sub('[^A-Za-z0-9\s\.-]+', '', self.title)
			queries = [
						self.search2.format(quote_plus(query + ' S%s' % self.season_xx)),
						self.search2.format(quote_plus(query + ' Season %s' % self.season_x))
							]
			if self.search_series:
				queries = [
						self.search2.format(quote_plus(query + ' Season')),
						self.search2.format(quote_plus(query + ' Complete'))
								]

			threads = []
			for url in queries:
				link = urljoin(self.base_link, url)
				threads.append(workers.Thread(self.get_sources_packs, link))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('KICKASS2')
			return self.sources


	def get_sources_packs(self, link):
		# log_utils.log('link = %s' % link, __name__, log_utils.LOGDEBUG)
		try:
			headers = {'User-Agent': client.agent()}
			r = client.request(link, headers=headers)
			if not r:
				return
			posts = client.parseDOM(r, 'tr', attrs={'id': 'torrent_latest_torrents'})

			for post in posts:
				ref = client.parseDOM(post, 'a', attrs={'title': 'Torrent magnet link'}, ret='href')[0]
				link = ref.split('url=')[1]

				url = unquote_plus(link).replace('&amp;', '&').replace(' ', '.')
				url = url.split('&tr')[0]
				hash = re.compile('btih:(.*?)&').findall(url)[0]
				name = unquote_plus(url.split('&dn=')[1])
				name = source_utils.clean_name(self.title, name)
				if source_utils.remove_lang(name):
					continue

				if not self.search_series:
					if not self.bypass_filter:
						if not source_utils.filter_season_pack(self.title, self.aliases, self.year, self.season_x, name):
							continue
					package = 'season'

				elif self.search_series:
					if not self.bypass_filter:
						valid, last_season = source_utils.filter_show_pack(self.title, self.aliases, self.imdb, self.year, self.season_x, name, self.total_seasons)
						if not valid:
							continue
					else:
						last_season = self.total_seasons
					package = 'show'

				try:
					seeders = int(re.findall('<td class="green center">([0-9]+|[0-9]+,[0-9]+)</td>', post, re.DOTALL)[0].replace(',', ''))
					if self.min_seeders > seeders:
						continue
				except:
					seeders = 0
					pass

				quality, info = source_utils.get_release_quality(name, url)

				try:
					size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', post)[0]
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except:
					dsize = 0
					pass

				info = ' | '.join(info)

				item = {'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
							'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package}
				if self.search_series:
					item.update({'last_season': last_season})
				self.sources.append(item)
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