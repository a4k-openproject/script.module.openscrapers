# -*- coding: utf-8 -*-
# created by Venom for Openscrapers

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
		self.domain = ['torlock.cc', 'torlock.unblockit.red']
		self.base_link = 'https://torlock.cc' # server response time sucks ass!
		self.search_link = '/all/torrents/%s/?sort=seeds&order=desc'
		# self.base_link = 'https://torlock.unblockit.red/'
		# self.search_link = '/all/torrents/%s.html?sort=seeds&order=desc' # seeds sorting does not work behind proxy
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

			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			try:
				r = client.request(url)
				div = client.parseDOM(r, 'div', attrs={'class': 'panel panel-default'})[0]
				table = client.parseDOM(div, 'table', attrs={'class': 'table table-striped table-bordered table-hover table-condensed'})[0]
				links = re.findall('<a href="(.+?)">', table, re.DOTALL)

				threads = []
				for link in links:
					threads.append(workers.Thread(self.get_sources, link))
				[i.start() for i in threads]
				[i.join() for i in threads]
				return self.sources
			except:
				source_utils.scraper_error('TORLOCK')
				return self.sources

		except:
			source_utils.scraper_error('TORLOCK')
			return self.sources


	def get_sources(self, link):
		try:
			url = '%s%s' % (self.base_link, link)
			result = client.request(url)
			if result is None:
				return
			if 'magnet' not in result:
				return

			url = 'magnet:%s' % (re.findall('a href="magnet:(.+?)"', result, re.DOTALL)[0])
			url = urllib.unquote_plus(url).decode('utf8').replace('&amp;', '&')
			url = url.split('&tr=')[0].replace(' ', '.')
			if url in str(self.sources):
				return

			# hash = re.findall('magnet:\?xt=urn:btih:(.*?)&dn=', url)[0] # future dict add for hash only

			name = url.split('&dn=')[1]
			if name.startswith('www'):
				try:
					name = re.sub(r'www(.*?)\W{2,10}', '', name)
				except:
					name = name.split('-.', 1)[1].lstrip()

			if source_utils.remove_lang(name):
				return

			t = name.split(self.hdlr)[0].replace(self.year, '').replace('(', '').replace(')', '').replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
			if cleantitle.get(t) != cleantitle.get(self.title):
				return

			if self.hdlr not in name:
				return

			try:
				seeders = int(re.findall('<dt>SWARM</dt><dd>.*?>(.+?)</b>', result, re.DOTALL)[0].replace(',', ''))
				if self.min_seeders > seeders:
					return
			except:
				pass

			quality, info = source_utils.get_release_quality(name, url)

			try:
				size = re.findall('<dt>SIZE</dt><dd>(.*? [a-zA-Z]{2})', result, re.DOTALL)[0]
				dsize, isize = source_utils._size(size)
				info.insert(0, isize)
			except:
				dsize = 0
				pass

			info = ' | '.join(info)

			self.sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': url,
												'info': info, 'direct': False, 'debridonly': True, 'size': dsize})

		except:
			source_utils.scraper_error('TORLOCK')
			pass

	def resolve(self, url):
		return url
