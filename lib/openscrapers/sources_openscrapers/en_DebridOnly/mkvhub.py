# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers  (added cfscrape 4-3-2020)

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
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 28
		self.language = ['en']
		self.domains = ['www.mkvhub.com']
		self.base_link = 'https://www.mkvhub.com'
		# self.search_link = '/search/%s/feed/rss2/'
		self.search_link = '/?s=%s'


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
			if url is None: return

			url = parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		self._sources = []
		try:
			self.scraper = cfscrape.create_scraper()

			if url is None:
				return self._sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')
			aliases = data['aliases']

			hdlr = 'S%02d' % (int(data['season'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = self.search_link % quote_plus(query)
			url = urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			r = self.scraper.get(url).content
			if '404 Not found' in r:
				return self._sources

			posts = client.parseDOM(r, 'figure')
			items = []
			for post in posts:
				try:
					url = client.parseDOM(post, 'a', ret='href')[0]
					name = client.parseDOM(post, 'img', ret='title')[0].replace(' ', '.')

					if source_utils.remove_lang(name):
						continue
					# if not source_utils.check_title(title, name, hdlr, data['year']):
						# continue

					if not source_utils.check_title(title, aliases, name, hdlr, data['year']):
						continue

					items.append((url, name))
				except:
					source_utils.scraper_error('MKVHUB')
					pass

			threads = []
			for i in items:
				threads.append(workers.Thread(self._get_sources, i[0], i[1], hostDict, hostprDict))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self._sources
		except:
			source_utils.scraper_error('MKVHUB')
			return self._sources


	def _get_sources(self, url, name, hostDict, hostprDict):
		try:
			urls = []
			result = self.scraper.get(url).content
			if 'dbuttn watch' not in result:
				return
			urls = [(client.parseDOM(result, 'a', ret='href', attrs={'class': 'dbuttn watch'})[0],
						client.parseDOM(result, 'a', ret='href', attrs={'class': 'dbuttn blue'})[0],
						client.parseDOM(result, 'a', ret='href', attrs={'class': 'dbuttn magnet'})[0])]

			# '''<a class="dbuttn watch" href="https://www.linkomark.xyz/view/EnWNqSNeLw" target="_blank" rel="nofollow noopener">Watch Online Links</a>
			# <a class="dbuttn blue" href="https://www.linkomark.xyz/view/3-Gjyz5Q2R" target="_blank" rel="nofollow noopener">Get Download Links</a> 
			# <a class="dbuttn magnet" href="https://torrentbox.site/save/2970fa51e8af52b7e2d1d5fa61a6005777d768ba" target="_blank" rel="nofollow noopener">Magnet Link</a>'''

			quality, info = source_utils.get_release_quality(name, url)

			try:
				size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', result)[0]
				dsize, isize = source_utils._size(size)
				info.insert(0, isize)
			except:
				dsize = 0
				pass

			fileType = source_utils.getFileType(name)
			info.append(fileType)
			info = ' | '.join(info) if fileType else info[0]
		except:
			source_utils.scraper_error('MKVHUB')
			return

		for url in urls[0]:
			try:
				r = client.request(url)
				if r is None:
					continue

				if 'linkomark' in url:
					p_link = client.parseDOM(r, 'link', attrs={'rel': 'canonical'}, ret='href')[0]

					#<input type="hidden" name="_csrf_token_" value=""/>
					input_name = client.parseDOM(r, 'input', ret='name')[0]
					input_value = client.parseDOM(r, 'input', ret='value')[0]

					post = {input_name: input_value}
					p_data = client.request(p_link, post=post)
					links = client.parseDOM(p_data, 'a', ret='href', attrs={'target': '_blank'})

					for i in links:
						valid, host = source_utils.is_host_valid(i, hostDict)
						if not valid:
							valid, host = source_utils.is_host_valid(i, hostprDict)
							if not valid:
								continue
							else:
								rd = True
						else:
							rd = False
						if i in str(self._sources):
							continue

						if 'rapidgator' in i:
							rd = True

						if rd:
							self._sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': i,
																	'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
						else:
							self._sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': i,
																	'info': info, 'direct': False, 'debridonly': False, 'size': dsize})

				elif 'torrent' in url:
					data = client.parseDOM(r, 'a', ret='href')
					url = [i for i in data if 'magnet:' in i][0]
					url = unquote_plus(url).replace('&amp;', '&').replace(' ', '.')
					url = url.split('&tr')[0]
					hash = re.compile('btih:(.*?)&').findall(url)[0]
					name = url.split('&dn=')[1]
					if '.-.MkvHub' in name:
						name = name.split('.-.')[0]
					seeders = 0

					self._sources.append({'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
													'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			except:
				source_utils.scraper_error('MKVHUB')
				pass


	def resolve(self, url):
		return url