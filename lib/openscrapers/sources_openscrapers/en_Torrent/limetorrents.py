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

from openscrapers.modules import cfscrape
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 3
		self.language = ['en']
		self.domains = ['limetorrents.info', 'limetorrents.asia']
		self.base_link = 'https://www.limetorrents.info'
		self.tvsearch = 'https://www.limetorrents.info/search/tv/{0}/1/'
		self.moviesearch = 'https://www.limetorrents.info/search/movies/{0}/1/'
		self.min_seeders = 0


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
		self.scraper = cfscrape.create_scraper()
		self._sources = []
		try:
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
				url = self.tvsearch.format(urllib.quote(query))
			else:
				url = self.moviesearch.format(urllib.quote(query))
			urls.append(url)

			url2 = url.replace('/1/', '/2/')
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
			source_utils.scraper_error('LIMETORRENTS')
			return self._sources


	def _get_items(self, url):
		try:
			headers = {'User-Agent': client.agent()}
			r = self.scraper.get(url,headers=headers).content
			if not r:
				return
			posts = client.parseDOM(r, 'table', attrs={'class': 'table2'})[0]
			posts = client.parseDOM(posts, 'tr')

			for post in posts:
				data = client.parseDOM(post, 'a', ret='href')[1]
				if '/search/' in data:
					continue

				try:
					data = data.encode('ascii', 'ignore')
				except:
					pass

				data = re.sub('\s', '', data).strip()
				link = urlparse.urljoin(self.base_link, data)

				name = client.parseDOM(post, 'a')[1]
				name = urllib.unquote_plus(name)
				name = re.sub('[^A-Za-z0-9]+', '.', name).lstrip('.')
				if source_utils.remove_lang(name):
					continue

				match = source_utils.check_title(self.title, name, self.hdlr, self.year)
				if not match:
					continue

				try:
					seeders = int(client.parseDOM(post, 'td', attrs={'class': 'tdseed'})[0].replace(',', ''))
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
			source_utils.scraper_error('LIMETORRENTS')
			return self.items


	def _get_sources(self, item):
		try:
			name = item[0]
			quality, info = source_utils.get_release_quality(name, name)

			if item[2] != '0':
				info.insert(0, item[2])
			info = ' | '.join(info)

			data = self.scraper.get(item[1]).content
			if data is None:
				return

			try:
				url = re.search('''href=["'](magnet:\?[^"']+)''', data).groups()[0]
				url = urllib.unquote_plus(url).replace('&amp;', '&').replace(' ', '.')
				url = url.split('&tr')[0]
			except:
				return

			hash = re.compile('btih:(.*?)&').findall(url)[0]

			self._sources.append({'source': 'torrent', 'seeders': item[4], 'hash': hash, 'name': name, 'quality': quality,
											'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': item[3]})
		except:
			source_utils.scraper_error('LIMETORRENTS')
			pass


	def resolve(self, url):
		return url