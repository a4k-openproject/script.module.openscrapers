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
		self.language = ['en', 'de', 'fr', 'ko', 'pl', 'pt', 'ru']
		self.domains = ['yts.lt', 'yts.am']  # Old yts.ag
		self.base_link = 'https://yts.lt'
		self.search_link = '/browse-movies/%s/all/all/0/latest'
		# self.search_link = '/movie/%s'
		self.min_seeders = 1


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

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['title'].replace('&', 'and')
			hdlr = data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = self.search_link % urllib.quote(query)
			url = urlparse.urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			html = client.request(url)

			try:
				results = client.parseDOM(html, 'div', attrs={'class': 'row'})[2]
			except:
				source_utils.scraper_error('YTS')
				return sources

			items = re.findall('class="browse-movie-bottom">(.+?)</div>\s</div>', results, re.DOTALL)

			if items is None:
				return sources

			for entry in items:
				try:
					try:
						link, name = re.findall('<a href="(.+?)" class="browse-movie-title">(.+?)</a>', entry, re.DOTALL)[0]
						name = client.replaceHTMLCodes(name)
					except:
						continue

					if any(x in link.lower() for x in ['french', 'italian', 'spanish', 'truefrench', 'dublado', 'dubbed']):
						continue

					t = name.split(hdlr)[0].replace('&', 'and')
					if cleantitle.get(t) != cleantitle.get(title):
						continue

					y = entry[-4:]
					if y != hdlr:
						continue

					response = client.request(link)

					try:
						entries = client.parseDOM(response, 'div', attrs={'class': 'modal-torrent'})

						for torrent in entries:
							link, name = re.findall(
								'href="magnet:(.+?)" class="magnet-download download-torrent magnet" title="(.+?)"',
								torrent, re.DOTALL)[0]
							link = 'magnet:%s' % link
							link = str(client.replaceHTMLCodes(link).split('&tr')[0])
							if link in str(sources):
								continue

							quality, info = source_utils.get_release_quality(name, link)

							try:
								size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', torrent)[-1]
								div = 1 if size.endswith(('GB', 'GiB')) else 1024
								size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
								size = '%.2f GB' % size
								info.append(size)
							except:
								pass

							info = ' | '.join(info)

							sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': link,
														'info': info, 'direct': False, 'debridonly': True})
					except:
						source_utils.scraper_error('YTS')
						continue
				except:
					source_utils.scraper_error('YTS')
					continue

			return sources

		except:
			source_utils.scraper_error('YTS')
			return sources


	def resolve(self, url):
		return url