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

from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import dom_parser  # switch to client.parseDOM() to rid import
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['ultrahdindir.com']
		self.base_link = 'http://ultrahdindir.com'
		self.post_link = '/index.php?do=search'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []

			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			hostDict = hostprDict + hostDict

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['title'].replace('&', 'and')

			year = data['year']

			query = '%s %s' % (title, year)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = urlparse.urljoin(self.base_link, self.post_link)

			post = 'do=search&subaction=search&search_start=0&full_search=0&result_from=1&story=%s' % urllib.quote_plus(query)

			r = client.request(url, post=post)
			# log_utils.log('r = %s' % r, log_utils.LOGDEBUG)

			r = client.parseDOM(r, 'div', attrs={'class': 'box-out margin'})
			# log_utils.log('r = %s' % r, log_utils.LOGDEBUG)

				# switch to client.parseDOM() to rid import
			r = [(dom_parser.parse_dom(i, 'div', attrs={'class':'news-title'})) for i in r if data['imdb'] in i]
			r = [(dom_parser.parse_dom(i[0], 'a', req='href')) for i in r if i]
			r = [(i[0].attrs['href'], i[0].content) for i in r if i]

			for item in r:
				try:
					name = item[0]
					s = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', name)
					s = s[0] if s else '0'

					data = client.request(item[0])
					data = dom_parser.parse_dom(data, 'div', attrs={'id': 'r-content'})
					data = re.findall('\s*<b><a href="(.+?)".+?</a></b>', data[0].content, re.DOTALL)

					for url in data:
						try:
							try:
								qual = client.request(url)
								quals = re.findall('span class="file-title" id="file-title">(.+?)</span', qual)
								if quals == []:
									raise Exception()

								for q in quals:
									quality, info = source_utils.get_release_quality(q, url)

							except:
								quality = 'SD' ; info = []

							url = client.replaceHTMLCodes(url)
							url = url.encode('utf-8')

							if any(x in url for x in ['.rar', '.zip', '.iso']):
								raise Exception()

							if not 'turbobit' in url:
								continue

							if url in str(sources):
								continue

							sources.append({'source': 'turbobit', 'quality': quality, 'language': 'en', 'url': url,
														'info': info, 'direct': True, 'debridonly': True})
							# log_utils.log('sources = %s' % sources, log_utils.LOGDEBUG)

						except:
							source_utils.scraper_error('ULTRAHDINDIR')
							pass
				except:
					source_utils.scraper_error('ULTRAHDINDIR')
					pass

			# log_utils.log('sources = %s' % sources, log_utils.LOGDEBUG)
			return sources

		except:
			source_utils.scraper_error('ULTRAHDINDIR')
			return sources


	def resolve(self, url):
		return url
