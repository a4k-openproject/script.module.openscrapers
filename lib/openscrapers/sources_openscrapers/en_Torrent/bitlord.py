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
import urllib
import urlparse

from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domain = ['bitlordsearch.com']
		self.base_link = 'http://www.bitlordsearch.com'
		self.search_link = '/search?q=%s'
		# bitlords api-possible future switch
		# self.search_link = '/get_list'
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
		sources = []
		try:
			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			r = client.request(url)
			if r is None:
				return sources
			links = zip(client.parseDOM(r, 'a', attrs={'class': 'btn btn-default magnet-button stats-action banner-button'}, ret='href'), client.parseDOM(r, 'td', attrs={'class': 'size'}), client.parseDOM(r, 'td', attrs={'class': 'seeds rescrap'}))

			for link in links:
				try:
					url = urllib.unquote_plus(link[0]).replace('&amp;', '&').replace(' ', '.')
					url = url.encode('ascii', errors='ignore').decode('ascii', errors='ignore')
					url = re.sub(r'(&tr=.+)&dn=', '&dn=', url) # some links on bitlord &tr= before &dn=
					url = url.split('&tr=')[0]
					url = url.split('&xl=')[0]
					if 'magnet' not in url:
						continue

					hash = re.compile('btih:(.*?)&').findall(url)[0]

					name = url.split('&dn=')[1]
					name = re.sub('[^A-Za-z0-9]+', '.', name).lstrip('.')
					if name.startswith('www'):
						try:
							name = re.sub(r'www(.*?)\W{2,10}', '', name)
						except:
							name = name.split('-.', 1)[1].lstrip()

					if source_utils.remove_lang(name):
						continue

					match = source_utils.check_title(title, name, hdlr, data['year'])
					if not match:
						continue

					try:
						seeders = int(link[2].replace(',', ''))
						if self.min_seeders > seeders:
							continue
					except:
						seeders = 0
						pass

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = int(link[1])
						size = str(size) + ' GB' if len(str(size)) == 1 else str(size) + ' MB'
						dsize, isize = source_utils._size(size)
						info.insert(0, isize)
					except:
						source_utils.scraper_error('BITLORD')
						dsize = 0
						pass

					info = ' | '.join(info)

					sources.append({'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
												'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
				except:
					source_utils.scraper_error('BITLORD')
					return sources
			return sources
		except:
			source_utils.scraper_error('BITLORD')
			return sources


	def resolve(self, url):
		return url