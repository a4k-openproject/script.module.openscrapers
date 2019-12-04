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

from openscrapers.modules import cache
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['pirateproxy.live', 'thepiratebay.org', 'thepiratebay.fun', 'thepiratebay.asia', 'tpb.party',
								'thehiddenbay.com', 'piratebay.live', 'thepiratebay.zone'] #-- 'thepiratebayz.org' and 'thepiratebay3.org' seem dead

		self._base_link = None
		# self.search_link = '/s/?q=%s&page=1&&video=on&orderby=99' #-page flip does not work
		self.search_link = '/search/%s/1/99/200' #-direct link can flip pages
		self.min_seeders = 1


	@property
	def base_link(self):
		if not self._base_link:
			self._base_link = cache.get(self.__get_base_url, 120, 'https://%s' % self.domains[0])
		return self._base_link


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

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = self.search_link % urllib.quote(query)
			url = urlparse.urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			html = client.request(url)
			html = html.replace('&nbsp;', ' ')

			try:
				results = client.parseDOM(html, 'table', attrs={'id': 'searchResult'})
			except:
				return sources

			url2 = url.replace('/1/', '/2/')

			html2 = client.request(url2)
			html2 = html2.replace('&nbsp;', ' ')

			try:
				results += client.parseDOM(html2, 'table', attrs={'id': 'searchResult'})
			except:
				return sources

			results = ''.join(results)

			rows = re.findall('<tr(.+?)</tr>', results, re.DOTALL)
			if rows is None:
				return sources

			for entry in rows:
				try:
					try:
						url = 'magnet:%s' % (re.findall('a href="magnet:(.+?)"', entry, re.DOTALL)[0])
						url = str(client.replaceHTMLCodes(url).split('&tr')[0])
					except:
						continue

					if any(x in url.lower() for x in ['french', 'italian', 'spanish', 'truefrench', 'dublado', 'dubbed']):
						continue

					try:
						name = re.findall('class="detLink" title=".+?">(.+?)</a>', entry, re.DOTALL)[0]
						name = client.replaceHTMLCodes(name)

						t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
						if cleantitle.get(t) != cleantitle.get(title):
							continue
					except:
						continue

					if hdlr not in name:
						continue

					try:
						seeders = int(re.findall('<td align="right">(.+?)</td>', entry, re.DOTALL)[0])
					except:
						continue

					if self.min_seeders > seeders:
						continue

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', entry)[-1]
						div = 1 if size.endswith(('GB', 'GiB')) else 1024
						size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
						size = '%.2f GB' % size
						info.append(size)
					except:
						pass

					info = ' | '.join(info)

					sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': url,
												'info': info, 'direct': False, 'debridonly': True})
				except:
					source_utils.scraper_error('PIRATEBAY')
					continue

			return sources

		except:
			source_utils.scraper_error('PIRATEBAY')
			return sources


	def __get_base_url(self, fallback):
		try:
			for domain in self.domains:
				try:
					url = 'https://%s' % domain
					result = client.request(url, limit=1, timeout='10')
					result = re.findall('<input type="submit" title="(.+?)"', result, re.DOTALL)[0]
					if result and 'Pirate Search' in result:
						return url
				except:
					pass
		except:
			pass

		return fallback


	def resolve(self, url):
		return url