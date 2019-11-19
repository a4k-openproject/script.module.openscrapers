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

import re
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['mkvcage.site', 'www.mkvcage.ws', 'mkvcage.fun']
		self.base_link = 'https://www.mkvcage.site'
		self.search_link = '/?s=%s'

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
			if url is None: return
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
				raise Exception()

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s S%02dE%02d' % (title, int(data['season']), int(data['episode'])) \
				if 'tvshowtitle' in data else '%s %s' % (title, data['year'])
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			r = client.request(url)

			try:
				posts = client.parseDOM(r, 'h2', attrs={'class': 'entry-title'})

				for post in posts:
					data = client.parseDOM(post, 'a', ret='href')

					tit = client.parseDOM(post, 'a')[0].replace('Download ', '')
					t = tit.split(hdlr)[0].replace('(', '')

					if cleantitle.get(t) != cleantitle.get(title):
						continue

					if hdlr not in tit:
						continue

					for u in data:
						r = client.request(u)
						r = client.parseDOM(r, 'div', attrs={'class': 'clearfix entry-content'})

						for i in r:
							if 'buttn magnet' not in i:
								continue

							# link = client.parseDOM(i, 'a', ret='href', attrs={'class': 'buttn magnet'})[0] #random drops with this
							link = re.findall('a class="buttn magnet" href="(.+?)"', i, re.DOTALL)[0]
							# log_utils.log('magnet link = %s' % link, log_utils.LOGDEBUG)

							# # for another day to fetch torrent link from form data, seems like junk though
							# btorrent = client.parseDOM(i, 'a', ret='href', attrs={'class': 'buttn torrent'})[0]
							# btorrent = btorrent.replace(' ', '+')
							# # <input type="password" name="Pass1" size="20"></p>
							# # <input type="submit" value="Submit" name="Submit0"></p>
							# post = {'Pass1': "mkvcage", 'Submit0': 'Submit'}
							# import requests
							# p_data = requests.post(btorrent, data=post)
							# response = p_data.content
							# torrent = re.findall('a href="(.+?)"', response, re.DOTALL)[4]
							# # log_utils.log('torrent link = %s' % torrent, log_utils.LOGDEBUG)

							# <a class="buttn watch" href="https://ylink.bid/watchonline" target="_blank" rel="noopener noreferrer">Watch Online</a>
							# <a class="buttn blue" href="https://l.ylink.bid/index.php?ID=759s341illy" target="_blank" rel="noopener noreferrer">Download Links</a>
							# <a class="buttn magnet" href="magnet:?xt=urn:btih:9BC72CEF74E3BD56D46509B35B621113FE10EB86" target="_blank" rel="noopener noreferrer">Magnet</a>
							# <a class="buttn torrent" href="https://l.ylink.bid/index.php?ID=604lessy74" target="_blank" rel="noopener noreferrer">Torrent</a>
							# linksPassword = 'mkvcage'

							quality, info = source_utils.get_release_quality(u)
							try:
								size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:gb|gib|mb|mib))', str(data))[-1]
								div = 1 if size.endswith(('gb')) else 1024
								size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
								size = '%.2f gb' % size
								info.append(size)
							except:
								pass
							info = ' | '.join(info)

							sources.append(
								{'source': 'torrent', 'quality': quality, 'language': 'en', 'url': link, 'info': info,
								 'direct': False, 'debridonly': True})


			except:
				source_utils.scraper_error('MKVCAGE')
				pass

			return sources

		except:
			source_utils.scraper_error('MKVCAGE')
			return sources

	def resolve(self, url):
		return url
