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

from openscrapers.modules import cfscrape
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 2
		self.language = ['en']
		self.domains = ['torrentgalaxy.to', 'torrentgalaxy.pw']
		self.base_link = 'https://torrentgalaxy.to'
		self.search_link = '/torrents.php?search=%s&sort=size&order=desc'
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
		scraper = cfscrape.create_scraper()
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

			r = scraper.get(url).content
			posts = client.parseDOM(r, 'div', attrs={'class': 'tgxtable'})

			for post in posts:
				links = zip(re.findall('a href="(magnet:.+?)"', post, re.DOTALL),
							re.findall(r"<span class='badge badge-secondary' style='border-radius:4px;'>(.*?)</span>", post, re.DOTALL),
							re.findall(r"<span title='Seeders/Leechers'>\[<font color='green'><b>(.*?)<", post, re.DOTALL))

				for link in links:
					url = urllib.unquote_plus(link[0]).split('&tr')[0].replace(' ', '.')
					hash = re.compile('btih:(.*?)&').findall(url)[0]

					name = url.split('&dn=')[1]
					name = re.sub('[^A-Za-z0-9]+', '.', name).lstrip('.')
					if source_utils.remove_lang(name):
						continue

					match = source_utils.check_title(title, name, hdlr, data['year'])
					if not match:
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


	def resolve(self, url):
		return url