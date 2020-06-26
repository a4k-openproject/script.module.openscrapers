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

import json

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 32
		self.language = ['en']
		self.domains = ['watchepisodes.com', 'watchepisodes.unblocked.pl']
		self.base_link = 'http://www.watchepisodes4.com/'
		self.search_link = 'search/ajax_search?q=%s'


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urlencode(url)
			return url
		except:
			source_utils.scraper_error('WATCHEPISODES')
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
			source_utils.scraper_error('WATCHEPISODES')
			return


	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if url is None:
				return sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle']
			hdlr = 's%02de%02d' % (int(data['season']), int(data['episode']))
			query = quote_plus(cleantitle.getsearch(title))
			surl = urljoin(self.base_link, self.search_link % query)
			# log_utils.log('surl = %s' % surl, log_utils.LOGDEBUG)

			r = client.request(surl, XHR=True)
			r = json.loads(r)
			r = r['series']

			for i in r:
				tit = i['value']

				if cleantitle.get(title) != cleantitle.get(tit):
					continue
				slink = i['seo']
				slink = urljoin(self.base_link, slink)
				r = client.request(slink)

				if not data['imdb'] in r:
					continue

				data = client.parseDOM(r, 'div', {'class': 'el-item\s*'})

				epis = [client.parseDOM(i, 'a', ret='href')[0] for i in data if i]
				epis = [i for i in epis if hdlr in i.lower()][0]

				r = client.request(epis)
				links = client.parseDOM(r, 'a', ret='data-actuallink')

				for url in links:
					try:
						valid, host = source_utils.is_host_valid(url, hostDict)
						if not valid:
							continue
						sources.append({'source': host, 'quality': 'SD', 'info': '', 'language': 'en', 'url': url,
						                'direct': False, 'debridonly': False})
					except:
						source_utils.scraper_error('WATCHEPISODES')
						return sources
			return sources
		except:
			source_utils.scraper_error('WATCHEPISODES')
			return sources


	def resolve(self, url):
		return url