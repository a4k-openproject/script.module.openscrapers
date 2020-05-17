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

from openscrapers.modules import cfscrape # fails IUAM_challenge as of 5-17-20
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 15
		self.language = ['en']
		self.domains = ['torrentz2.eu', 'torrentz2.is']
		self.base_link = 'https://torrentz2.eu'
		# self.base_link = 'https://torrentz2.is'
		self.search_link = '/search?f=%s'
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
		scraper = cfscrape.create_scraper(delay=5)
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

			try:
				r = scraper.get(url).content
				# if 'DDoS protection by <a href="https://www.cloudflare.com/5xx-error-landing?utm_source=iuam" target="_blank">Cloudflare</a>' in r:
					# log_utils.log('TORRENTZ - Failed to solve IUAM challenge', log_utils.LOGDEBUG)
					# return sources

				posts = client.parseDOM(r, 'div', attrs={'class': 'results'})[0]
				posts = client.parseDOM(posts, 'dl')

				for post in posts:
					links = re.findall('<dt><a href=/(.+)</a>', post, re.DOTALL)
					try:
						seeders = int(re.findall('<span>([0-9]+|[0-9]+,[0-9]+)</span>', post, re.DOTALL)[0].replace(',', ''))
						if self.min_seeders > seeders:
							continue
					except:
						seeders = 0
						pass

					for link in links:
						hash = link.split('>')[0]
						name = link.split('>')[1]
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

						url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)

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
				source_utils.scraper_error('TORRENTZ')
				return
		except:
			source_utils.scraper_error('TORRENTZ')
			return sources


	def resolve(self, url):
		return url