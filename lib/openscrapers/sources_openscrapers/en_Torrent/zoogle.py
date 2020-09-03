# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers (updated 7-12-2020)

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
try: from urllib import urlencode, quote_plus, unquote_plus
except ImportError: from urllib.parse import urlencode, quote_plus, unquote_plus

from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en', 'de', 'fr', 'ko', 'pl', 'pt', 'ru']
		self.domains = ['zooqle.com'] #it's a Q not a G..lol
		self.base_link = 'https://zooqle.com'
		self.search_link = '/search?pg=1&q=%s'
		self.min_seeders = 1
		self.pack_capable = True


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'aliases': aliases, 'year': year}
			url = urlencode(url)
			return url
		except:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'aliases': aliases, 'year': year}
			url = urlencode(url)
			return url
		except:
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
		except:
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

			category = '+category%3ATV' if 'tvshowtitle' in data else '+category%3AMovies'

			query = '%s %s' % (self.title, self.hdlr)
			query = re.sub('[^A-Za-z0-9\s\.-]+', '', query)

			urls = []
			url = self.search_link % quote_plus(query)
			url = urljoin(self.base_link, url) + str(category) + '&v=t&s=sz&sd=d'
			urls.append(url)
			urls.append(url.replace('pg=1', 'pg=2'))
			# log_utils.log('urls = %s' % urls, log_utils.LOGDEBUG)

			threads = []
			for url in urls:
				threads.append(workers.Thread(self.get_sources, url))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('ZOOGLE')
			return self.sources


	def get_sources(self, url):
		try:
			# For some reason Zooqle returns 404 even though the response has a body.
			# This is probably a bug on Zooqle's server and the error should just be ignored.
			html = client.request(url, ignoreErrors = 404)
			if not html:
				return
			html = html.replace('&nbsp;', ' ')

			try:
				results = client.parseDOM(html, 'table', attrs={'class': 'table table-condensed table-torrents vmiddle'})[0]
			except:
				return

			rows = re.findall('<tr(.+?)</tr>', results, re.DOTALL)
			if not rows:
				return

			for entry in rows:
				try:
					try:
						if 'magnet:' not in entry:
							continue
						url = 'magnet:%s' % (re.findall('href="magnet:(.+?)"', entry, re.DOTALL)[0])
						url = unquote_plus(url).split('&tr')[0].replace('&amp;', '&').replace(' ', '.')
						url = source_utils.strip_non_ascii_and_unprintable(url)
						if url in str(self.sources):
							continue
					except:
						continue

					hash = re.compile('btih:(.*?)&').findall(url)[0]

					try:
						name = re.findall('<a class=".+?>(.+?)</a>', entry, re.DOTALL)[0]
						name = client.replaceHTMLCodes(name).replace('<hl>', '').replace('</hl>', '')
						name = unquote_plus(name)
						name = source_utils.clean_name(self.title, name)
						# name = url.split('&dn=')[1]
					except:
						continue
					if source_utils.remove_lang(name, self.episode_title):
						continue

					# some titles have foreign title translation in front so remove it
					if './.' in name:
						name = name.split('./.', 1)[1]
					if '.com.' in name.lower():
						try:
							name = re.sub(r'(.*?)\W{2,10}', '', name)
						except:
							name = name.split('-.', 1)[1].lstrip()

					if not source_utils.check_title(self.title, self.aliases, name, self.hdlr, self.year):
						continue

					# filter for episode multi packs (ex. S01E01-E17 is also returned in query)
					if self.episode_title:
						if not source_utils.filter_single_episodes(self.hdlr, name):
							continue

					try:
						seeders = int(re.findall('class="progress prog trans90" title="Seeders: (.+?) \|', entry, re.DOTALL)[0].replace(',', ''))
						if self.min_seeders > seeders:
							continue
					except:
						seeders = 0
						pass

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', entry)[-1]
						dsize, isize = source_utils._size(size)
						info.insert(0, isize)
					except:
						dsize = 0
						pass

					info = ' | '.join(info)

					self.sources.append({'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
											'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
				except:
					continue
		except:
			source_utils.scraper_error('ZOOGLE')
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
			category = '+category%3ATV'

			# query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', self.title)
			query = re.sub('[^A-Za-z0-9\s\.-]+', '', self.title)
			queries = [
						self.search_link % quote_plus(query + ' S%s' % self.season_xx),
						self.search_link % quote_plus(query + ' Season %s' % self.season_x)
							]
			if self.search_series:
				queries = [
						self.search_link % quote_plus(query + ' Season'),
						self.search_link % quote_plus(query + ' Complete')
								]

			threads = []
			for url in queries:
				link = urljoin(self.base_link, url) + str(category) + '&v=t&s=sz&sd=d'
				threads.append(workers.Thread(self.get_sources_packs, link))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('ZOOGLE')
			return self.sources


	def get_sources_packs(self, link):
		# log_utils.log('link = %s' % str(link), __name__, log_utils.LOGDEBUG)
		try:
			# For some reason Zooqle returns 404 even though the response has a body.
			# This is probably a bug on Zooqle's server and the error should just be ignored.
			html = client.request(link, ignoreErrors = 404)
			if not html:
				return
			html = html.replace('&nbsp;', ' ')

			try:
				results = client.parseDOM(html, 'table', attrs={'class': 'table table-condensed table-torrents vmiddle'})[0]
			except:
				return

			rows = re.findall('<tr(.+?)</tr>', results, re.DOTALL)
			if not rows:
				return

			for entry in rows:
				try:
					try:
						if 'magnet:' not in entry:
							continue
						url = 'magnet:%s' % (re.findall('href="magnet:(.+?)"', entry, re.DOTALL)[0])
						url = unquote_plus(url).split('&tr')[0].replace('&amp;', '&').replace(' ', '.')
						url = source_utils.strip_non_ascii_and_unprintable(url)
						if url in str(self.sources):
							continue
					except:
						continue

					hash = re.compile('btih:(.*?)&').findall(url)[0]

					try:
						name = re.findall('<a class=".+?>(.+?)</a>', entry, re.DOTALL)[0]
						name = client.replaceHTMLCodes(name).replace('<hl>', '').replace('</hl>', '')
						name = unquote_plus(name)
						name = source_utils.clean_name(self.title, name)
						# name = url.split('&dn=')[1]
					except:
						continue
					if source_utils.remove_lang(name):
						continue

					# some titles have foreign title translation in front so remove it
					if './.' in name:
						name = name.split('./.', 1)[1]
					if '.com.' in name.lower():
						try:
							name = re.sub(r'(.*?)\W{2,10}', '', name)
						except:
							name = name.split('-.', 1)[1].lstrip()

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
						seeders = int(re.findall('class="progress prog trans90" title="Seeders: (.+?) \|', entry, re.DOTALL)[0].replace(',', ''))
						if self.min_seeders > seeders:
							continue
					except:
						seeders = 0
						pass

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', entry)[-1]
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
					continue
		except:
			source_utils.scraper_error('ZOOGLE')
			pass


	def resolve(self, url):
		return url