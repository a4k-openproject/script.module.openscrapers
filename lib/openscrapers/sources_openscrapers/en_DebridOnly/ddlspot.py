# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers

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
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 25
		self.language = ['en']
		self.domains = ['www.ddlspot.com']
		self.base_link = 'http://www.ddlspot.com/'
		self.search_link = 'search/?q=%s&m=1&x=0&y=0'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urlencode(url)
			return url
		except:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
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
		try:
			sources = []

			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			hostDict = hostprDict + hostDict

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = self.search_link % quote_plus(query)
			url = urljoin(self.base_link, url).replace('-', '+')
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			r = client.request(url)
			posts = client.parseDOM(r, "table", attrs={"class": "download"})
			if posts == []:
				return sources

			for post in posts:
				items = zip(client.parseDOM(post, 'a', ret='title'), client.parseDOM(post, 'a', ret='href'))

				for item in items:
					try:
						name = item[0].replace(' ', '.')

						t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
						if cleantitle.get(t) != cleantitle.get(title):
							continue

						if hdlr not in name:
							continue

						if source_utils.remove_lang(name):
							continue

						i = str(item[1])
						i = self.base_link + i
						r = client.request(i)
						u = client.parseDOM(r, "div", attrs={"class": "dl-links"})

						for t in u:
							r = zip(re.compile("a href=.+? dl\W+'(.+?)'\W+").findall(t), re.findall('>.\((.+?Mb)\)', t))

							for link in r:
								url = link[0]

								if any(x in url for x in ['.rar', '.zip', '.iso', '.sample.']):
									continue

								if url in str(sources):
									continue

								quality, info = source_utils.get_release_quality(name, url)

								try:
									dsize, isize = source_utils._size(link[1])
									info.insert(0, isize)
								except:
									dsize = 0
									pass

								info = ' | '.join(info)

								valid, host = source_utils.is_host_valid(url, hostDict)
								if not valid:
									continue

								host = client.replaceHTMLCodes(host)
								try:
									host = host.encode('utf-8')
								except:
									pass

								sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
															'info': info, 'direct': False, 'debridonly': True, 'size': dsize})

					except:
						source_utils.scraper_error('DDLSPOT')
						pass

			return sources
		except:
			source_utils.scraper_error('DDLSPOT')
			return




	def resolve(self, url):
		return url
