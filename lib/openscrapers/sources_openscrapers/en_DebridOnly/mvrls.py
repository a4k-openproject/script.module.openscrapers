# -*- coding: UTF-8 -*-
# Created by Tempest
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
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 29
		self.language = ['en']
		self.domains = ['mvrls.com']
		self.base_link = 'http://mvrls.com'
		self.search_link = '/search/%s/feed/rss2/'
		# self.search_link = '/?s=%s' # should really switch to site search since rss feed often returns incorect query results vs. site


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
		try:
			sources = []

			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			hostDict = hostprDict + hostDict

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

			html = client.request(url)
			posts = client.parseDOM(html, 'item')

			items = []
			for post in posts:
				try:
					t = client.parseDOM(post, 'title')[0]
					u = client.parseDOM(post, 'enclosure', ret='url')
					#---rss feed does not contain size info-another reason why switching to site search be better
					s = re.search('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', post)
					s = s.groups()[0] if s else '0'
					items += [(t, i, s) for i in u]
				except:
					pass

			for item in items:
				try:
					url = item[1]
					if any(x in url for x in ['.rar', '.zip', '.iso', '.part']):
						continue

					url = client.replaceHTMLCodes(url)
					url = url.encode('utf-8')

					valid, host = source_utils.is_host_valid(url, hostDict)
					if not valid:
						continue

					host = client.replaceHTMLCodes(host)
					host = host.encode('utf-8')

					name = item[0]
					name = client.replaceHTMLCodes(name)

					# some shows like "Power" have year and hdlr in name
					t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
					if cleantitle.get(t) != cleantitle.get(title):
						continue

					if hdlr not in name:
						continue

					quality, info = source_utils.get_release_quality(name, url)

					try:
					#---rss feed does not contain size info-another reason why switching to site search be better
						size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', item[2])[-1]
						dsize, isize = source_utils._size(size)
						info.insert(0, isize)
					except:
						dsize = 0
						pass

					info = ' | '.join(info)

					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
												'info': info, 'direct': False, 'debridonly': True, 'size': dsize})

				except:
					source_utils.scraper_error('MVRLS')
					pass

			return sources
		except:
			source_utils.scraper_error('MVRLS')
			return sources


	def resolve(self, url):
		return url
