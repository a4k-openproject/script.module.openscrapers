# -*- coding: utf-8 -*-
# created by Venom for Openscrapers (updated url 7-12-2020)

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

from openscrapers.modules import cfscrape
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 2
		self.language = ['en']
		self.domains = ['torrentgalaxy.to', 'torrentgalaxy.pw']
		self.base_link = 'https://torrentgalaxy.to'
		self.search_link = '/torrents.php?search=%s&sort=size&order=desc'
		self.min_seeders = 0
		self.scraper = cfscrape.create_scraper()
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
		sources = []
		try:
			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')
			aliases = data['aliases']
			episode_title = data['title'] if 'tvshowtitle' in data else None
			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('[^A-Za-z0-9\s\.-]+', '', query)

			url = self.search_link % quote_plus(query)
			url = urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			r = self.scraper.get(url).content
			posts = client.parseDOM(r, 'div', attrs={'class': 'tgxtable'})

			for post in posts:
				links = zip(re.findall('a href="(magnet:.+?)"', post, re.DOTALL),
							re.findall(r"<span class='badge badge-secondary' style='border-radius:4px;'>(.*?)</span>", post, re.DOTALL),
							re.findall(r"<span title='Seeders/Leechers'>\[<font color='green'><b>(.*?)<", post, re.DOTALL))

				for link in links:
					url = unquote_plus(link[0]).split('&tr')[0].replace(' ', '.')
					url = source_utils.strip_non_ascii_and_unprintable(url)
					hash = re.compile('btih:(.*?)&').findall(url)[0]

					name = url.split('&dn=')[1]
					name = source_utils.clean_name(title, name)
					if source_utils.remove_lang(name, episode_title):
						continue

					if not source_utils.check_title(title, aliases, name, hdlr, data['year']):
						continue

					# filter for episode multi packs (ex. S01E01-E17 is also returned in query)
					if episode_title:
						if not source_utils.filter_single_episodes(hdlr, name):
							continue

					try:
						seeders = int(link[2])
						if self.min_seeders > seeders:
							continue
					except:
						seeders = 0
						pass

					quality, info = source_utils.get_release_quality(name, url)

					try:
						dsize, isize = source_utils._size(link[1])
						info.insert(0, isize)
					except:
						dsize = 0
						pass

					info = ' | '.join(info)

					sources.append({'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
												'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			return sources
		except:
			source_utils.scraper_error('TORRENTGALAXY')
			return sources


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
						self.search_link % quote_plus(query + ' S%s' % self.season_xx),
						self.search_link % quote_plus(query + ' Season %s' % self.season_x)
							]
			if search_series:
				queries = [
						self.search_link % quote_plus(query + ' Season'),
						self.search_link % quote_plus(query + ' Complete')
								]

			threads = []
			for url in queries:
				link = urljoin(self.base_link, url)
				threads.append(workers.Thread(self.get_sources_packs, link))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('TORRENTGALAXY')
			return self.sources


	def get_sources_packs(self, link):
		# log_utils.log('link = %s' % str(link), __name__, log_utils.LOGDEBUG)
		try:
			r = self.scraper.get(link).content
			if not r:
				return
			posts = client.parseDOM(r, 'div', attrs={'class': 'tgxtable'})
		except:
			source_utils.scraper_error('TORRENTGALAXY')
			return

		for post in posts:
			try:
				links = zip(
							re.findall('a href="(magnet:.+?)"', post, re.DOTALL),
							re.findall(r"<span class='badge badge-secondary' style='border-radius:4px;'>(.*?)</span>", post, re.DOTALL),
							re.findall(r"<span title='Seeders/Leechers'>\[<font color='green'><b>(.*?)<", post, re.DOTALL))
				for link in links:
					url = unquote_plus(link[0]).split('&tr')[0].replace(' ', '.')
					url = source_utils.strip_non_ascii_and_unprintable(url)
					hash = re.compile('btih:(.*?)&').findall(url)[0]

					name = url.split('&dn=')[1]
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
						seeders = int(link[2])
						if self.min_seeders > seeders:
							continue
					except:
						seeders = 0
						pass

					quality, info = source_utils.get_release_quality(name, url)

					try:
						dsize, isize = source_utils._size(link[1])
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
				source_utils.scraper_error('TORRENTGALAXY')
				pass


	def resolve(self, url):
		return url