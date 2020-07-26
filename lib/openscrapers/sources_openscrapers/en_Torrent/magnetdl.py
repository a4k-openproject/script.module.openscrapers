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

import json
import re

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, unquote_plus
except ImportError: from urllib.parse import urlencode, unquote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 2
		self.language = ['en']
		self.domains = ['magnetdl.com']
		self.base_link = 'https://www.magnetdl.com'
		self.search_link = '/{0}/{1}'
		self.min_seeders = 0
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

			url = urljoin(self.base_link, self.search_link.format(query[0].lower(), cleantitle.geturl(query)))
			# log_utils.log('url = %s' % url, __name__, log_utils.LOGDEBUG)

			r = client.request(url)
			if not r:
				return sources
			if '<tbody' not in r:
				return sources

			r = client.parseDOM(r, 'tbody')[0]
			results = client.parseDOM(r, 'tr')
			posts = [i for i in results if 'magnet:' in i]

			try:
				next_page = [i for i in results if 'Next Page' in i]
				if not next_page:
					raise Exception()
				page = client.parseDOM(next_page, 'a', ret='href', attrs={'title': 'Downloads | Page 2'})[0]
				r2 = client.request(self.base_link+page)
				results2 = client.parseDOM(r2, 'tr')
				posts += [i for i in results2 if 'magnet:' in i]
			except:
				pass

			for post in posts:
				post = post.replace('&nbsp;', ' ')

				links = client.parseDOM(post, 'a', ret='href')
				magnet = [i.replace('&amp;', '&') for i in links if 'magnet:' in i][0]
				url = unquote_plus(magnet).split('&tr')[0].replace(' ', '.')
				if url in str(sources):
					continue

				hash = re.compile('btih:(.*?)&').findall(url)[0]

				name = client.parseDOM(post, 'a', ret='title')[1].replace('&ndash;', '-')
				name = unquote_plus(name)
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
					seeders = int(client.parseDOM(post, 'td', attrs={'class': 's'})[0].replace(',', ''))
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

				sources.append({'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
											'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			return sources
		except:
			source_utils.scraper_error('MAGNETDL')
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
						self.search_link.format(query[0].lower(), cleantitle.geturl(query + ' S%s' % self.season_xx)),
						self.search_link.format(query[0].lower(), cleantitle.geturl(query + ' Season %s' % self.season_x))
							]
			if search_series:
				queries = [
						self.search_link.format(query[0].lower(), cleantitle.geturl(query + ' Season')),
						self.search_link.format(query[0].lower(), cleantitle.geturl(query + ' Complete'))
								]

			threads = []
			for url in queries:
				link = urljoin(self.base_link, url)
				threads.append(workers.Thread(self.get_sources_packs, link))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('MAGNETDL')
			return self.sources


	def get_sources_packs(self, url):
		# log_utils.log('url = %s' % str(url), __name__, log_utils.LOGDEBUG)
		try:
			r = client.request(url)
			if not r:
				return
			if '<tbody' not in r:
				return

			r = client.parseDOM(r, 'tbody')[0]

			results = client.parseDOM(r, 'tr')
			posts = [i for i in results if 'magnet:' in i]

			try:
				next_page = [i for i in results if 'Next Page' in i]
				if not next_page:
					raise Exception()
				page = client.parseDOM(next_page, 'a', ret='href', attrs={'title': 'Downloads | Page 2'})[0]
				r2 = client.request(self.base_link+page)
				results2 = client.parseDOM(r2, 'tr')
				posts += [i for i in results2 if 'magnet:' in i]
			except:
				pass

			for post in posts:
				post = post.replace('&nbsp;', ' ')

				links = client.parseDOM(post, 'a', ret='href')
				magnet = [i.replace('&amp;', '&') for i in links if 'magnet:' in i][0]
				url = unquote_plus(magnet).split('&tr')[0].replace(' ', '.')
				if url in str(self.sources):
					continue

				hash = re.compile('btih:(.*?)&').findall(url)[0]

				name = client.parseDOM(post, 'a', ret='title')[1].replace('&ndash;', '-')
				name = unquote_plus(name)
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
					seeders = int(client.parseDOM(post, 'td', attrs={'class': 's'})[0].replace(',', ''))
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
			source_utils.scraper_error('MAGNETDL')
			pass


	def resolve(self, url):
		return url