# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.

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

import requests

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import getSum
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['123movieshub.gg', 'seriesonline8.co']
		self.base_link = 'https://www5.123movieshub.gg'
		self.search_link = '/movie/search/%s'

	def matchAlias(self, title, aliases):
		try:
			for alias in aliases:
				if cleantitle.get(title) == cleantitle.get(alias['title']):
					return True
		except:
			return False

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			aliases.append({'country': 'us', 'title': title})
			url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
			url = urllib.urlencode(url)
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			aliases.append({'country': 'us', 'title': tvshowtitle})
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
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

	def searchShow(self, title, season, aliases):
		try:
			title = cleantitle.normalize(title)
			search = '%s Season %01d' % (title, int(season))
			url = urlparse.urljoin(self.base_link, self.search_link % cleantitle.geturl(search))
			r = client.request(url, timeout='10')
			r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
			r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
			r = [(i[0], i[1], re.findall('(.*?)\s+-\s+Season\s+(\d)', i[1])) for i in r]
			r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
			url = [i[0] for i in r if self.matchAlias(i[2][0], aliases) and i[2][1] == season][0]
			url = urlparse.urljoin(self.base_link, '%s/watching.html' % url)
			return url
		except:
			return

	def searchMovie(self, title, year, aliases):
		try:
			title = cleantitle.normalize(title)
			url = urlparse.urljoin(self.base_link, self.search_link % cleantitle.geturl(title))
			r = client.request(url, timeout='10')
			r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
			r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
			results = [(i[0], i[1], re.findall('\((\d{4})', i[1])) for i in r]
			try:
				r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
				url = [i[0] for i in r if self.matchAlias(i[1], aliases) and (year == i[2])][0]
			except:
				url = None
				pass
			if (url is None):
				url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]
			url = urlparse.urljoin(self.base_link, '%s/watching.html' % url)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			aliases = eval(data['aliases'])
			if 'tvshowtitle' in data:
				ep = data['episode']
				url = '%s/film/%s-season-%01d/watching.html?ep=%s' % (
				self.base_link, cleantitle.geturl(data['tvshowtitle']), int(data['season']), ep)
				r = client.request(url, timeout='10', output='geturl')
				if url is None:
					url = self.searchShow(data['tvshowtitle'], data['season'], aliases)
			else:
				url = self.searchMovie(data['title'], data['year'], aliases)
				if url is None:
					url = '%s/film/%s/watching.html?ep=0' % (self.base_link, cleantitle.geturl(data['title']))
			if url is None:
				raise Exception()
			r = client.request(url, timeout='10')
			r = client.parseDOM(r, 'div', attrs={'class': 'les-content'})
			if 'tvshowtitle' in data:
				ep = data['episode']
				links = client.parseDOM(r, 'a', attrs={'episode-data': ep}, ret='player-data')
			else:
				links = client.parseDOM(r, 'a', ret='player-data')
			for link in links:
				link = "https:" + link if not link.startswith('http') else link
				if 'vidcloud' in link:
					r = client.request(link, timeout='10')
					match = getSum.findSum(r)
					for url in match:
						url = "https:" + url if not url.startswith('http') else url
						url = requests.get(url).url if 'api.vidnode' in url else url
						valid, host = source_utils.is_host_valid(url, hostDict)
						if valid:
							quality, info = source_utils.get_release_quality(url, url)
							sources.append(
								{'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url,
								 'direct': False, 'debridonly': False})
				else:
					valid, host = source_utils.is_host_valid(link, hostDict)
					if valid:
						quality, info = source_utils.get_release_quality(link, link)
						sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': link,
						                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		if "google" in url:
			return directstream.googlepass(url)
		elif 'vidcloud' in url:
			r = client.request(url)
			url = re.findall("file: '(.+?)'", r)[0]
			return url
		else:
			return url
