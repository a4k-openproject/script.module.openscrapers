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
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser
from openscrapers.modules import workers, log_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['www.mkvhub.com']
		self.base_link = 'https://www.mkvhub.com'
		# self.search_link = '/search/%s/feed/rss2/'
		self.search_link = '/?s=%s'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except BaseException:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except BaseException:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None: return

			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urllib.urlencode(url)
			return url
		except BaseException:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			self._sources = []

			if url is None:
				return self._sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']),
				int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
				data['title'], data['year'])
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url)

			r = client.request(url)

			posts = client.parseDOM(r, 'figure')

			items = []
			for post in posts:
				try:
					tit = client.parseDOM(post, 'img', ret='title')[0]

					t = tit.split(hdlr)[0].replace('(', '')
					if not cleantitle.get(t) == cleantitle.get(title):
						raise Exception()

					if hdlr not in tit:
						raise Exception()

					url = client.parseDOM(post, 'a', ret='href')[0]

					try:
						size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', post)[0]
						div = 1 if size.endswith(('GB', 'GiB', 'Gb')) else 1024
						size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
						size = '%.2f GB' % size
					except:
						size = '0'

					items += [(tit, url, size)]

				except:
					pass

			datos = []
			for title, url, size in items:
				try:
					name = client.replaceHTMLCodes(title)

					quality, info = source_utils.get_release_quality(name, name)

					info.append(size)
					info = ' | '.join(info)

					datos.append((url, quality, info))
				except:
					pass

			threads = []
			for i in datos:
				threads.append(workers.Thread(self._get_sources, i[0], i[1], i[2], hostDict, hostprDict))
			[i.start() for i in threads]
			[i.join() for i in threads]

			return self._sources
		except BaseException:
			return self._sources


	def _get_sources(self, url, quality, info, hostDict, hostprDict):
		urls = []

		# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

		result = client.request(url)

		urls = [(client.parseDOM(result, 'a', ret='href', attrs={'class': 'dbuttn watch'})[0],
				client.parseDOM(result, 'a', ret='href', attrs={'class': 'dbuttn blue'})[0],
				client.parseDOM(result, 'a', ret='href', attrs={'class': 'dbuttn magnet'})[0])]
		# log_utils.log('urls = %s' % urls, log_utils.LOGDEBUG)

			# '''<a class="dbuttn watch" href="https://www.linkomark.xyz/view/EnWNqSNeLw" target="_blank" rel="nofollow noopener">Watch Online Links</a>
			# <a class="dbuttn blue" href="https://www.linkomark.xyz/view/3-Gjyz5Q2R" target="_blank" rel="nofollow noopener">Get Download Links</a> 
			# <a class="dbuttn magnet" href="https://torrentbox.site/save/2970fa51e8af52b7e2d1d5fa61a6005777d768ba" target="_blank" rel="nofollow noopener">Magnet Link</a>'''

		for url in urls[0]:
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)
			try:
				r = client.request(url)
				# log_utils.log('r = %s' % r, log_utils.LOGDEBUG)

				# if 'linkprotector' in url:
					# log_utils.log('linkprotector exists', log_utils.LOGDEBUG)

				if 'linkomark' in url:
					p_link = dom_parser.parse_dom(r, 'link', {'rel': 'canonical'},  req='href')[0]
					# p_link = dom_parser.parse_dom(r, 'link', {'rel': 'canonical'},  req='href')[0]
					# log_utils.log('p_link = %s' % str(p_link), log_utils.LOGDEBUG)

					p_link = p_link.attrs['href']
					# log_utils.log('p_link = %s' % str(p_link), log_utils.LOGDEBUG)

					#<input type="hidden" name="_csrf_token_" value=""/>
					input_name = client.parseDOM(r, 'input', ret='name')[0]
					# log_utils.log('input_name = %s' % str(input_name), log_utils.LOGDEBUG)

					input_value = client.parseDOM(r, 'input', ret='value')[0]
					# log_utils.log('input_value = %s' % str(input_value), log_utils.LOGDEBUG)

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
							self._sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': i, 'info': info,
																'direct': False, 'debridonly': True})
						else:
							self._sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': i, 'info': info,
																'direct': False, 'debridonly': False})

				elif 'torrent' in url:
					data = client.parseDOM(r, 'a', ret='href')
					# log_utils.log('data = %s' % data, log_utils.LOGDEBUG)

					url = [i for i in data if 'magnet:' in i][0]
					url = url.split('&tr')[0]
					# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

					self._sources.append({'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': url,
													'info': info, 'direct': False, 'debridonly': True})

			except:
				import traceback
				traceback.print_exc()
				pass

	def resolve(self, url):
		return url