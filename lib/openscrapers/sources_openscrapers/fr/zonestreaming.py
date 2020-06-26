# -*- coding: utf-8 -*-
# covenant

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

try: from urlparse import parse_qs, urlparse
except ImportError: from urllib.parse import parse_qs, urlparse
try: from urllib import urlencode
except ImportError: from urllib.parse import urlencode
from openscrapers.modules import cleantitle
from openscrapers.modules import client


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['fr']
		self.domains = ['www.zone-streaming.fr']
		self.base_link = 'http://www.zone-streaming.fr'
		self.key_link = '?'
		self.search_link = 's=%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'localtitle': localtitle, 'year': year}
			url = urlencode(url)
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle,
			       'year': year}
			url = urlencode(url)
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return

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

			print url

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['title']
			year = data['year'] if 'year' in data else data['year']
			season = data['season'] if 'season' in data else False
			episode = data['episode'] if 'episode' in data else False
			localtitle = data['localtitle'] if 'localtitle' in data else False

			if season and episode:
				localtitle = data['localtvshowtitle'] if 'localtvshowtitle' in data else False

			# r = 'http://www.fullmoviz.org/?s=deadpool'
			# r = client.request(r)

			# r = client.parseDOM(r, 'div', attrs={'class': 'post-thumbnail'})
			# r = client.parseDOM(r, 'a', ret='href')
			# r = client.request(r[0])
			# r = client.parseDOM(r, 'div', attrs={'class': 'tab-me-content-wrapper'})
			# r = client.parseDOM(r, 'iframe', ret='src')

			t = cleantitle.get(title)
			tq = cleantitle.query(localtitle)
			tq2 = re.sub(' ', '', cleantitle.query(localtitle).lower())
			tq = re.sub(' ', '%20', tq)
			y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

			query = 'http://www.fullmoviz.org'

			r = client.request('http://www.fullmoviz.org/?s=%s' % tq)
			print 'http://www.fullmoviz.org/?s=%s' % tq
			r = client.parseDOM(r, 'div', attrs={'class': 'post-thumbnail'})
			r0 = client.parseDOM(r, 'a', ret='href')[0]
			r2 = client.parseDOM(r, 'a', ret='title')[0]
			r1 = re.sub('(\([0-9]{4}\)|streaming|\s+)', '', r2)

			# r = sorted(set(r))
			r = [(r0, r1) for i in r]
			# r = [(i[0], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
			# r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
			# r = [(i[0], i[1], i[2], re.findall('(.+?)\s+(?:saison|s)\s+(\d+)', i[1])) for i in r]
			# r = [(i[0], i[3][0][0] if len(i[3]) > 0 else i[1], i[2], i[3][0][1] if len(i[3]) > 0 else '0') for i in r]
			# r = [(i[0], re.sub(' \&\#[0-9]{4,6};', '', i[1]), i[2], i[3]) for i in r]
			r = [i[0] for i in r if tq2 == cleantitle.get(i[1])][0]

			url = re.findall('(?://.+?|)(/.+)', r)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')

			r = client.request('http://www.fullmoviz.org' + url)
			print 'http://www.fullmoviz.org' + url

			r = client.parseDOM(r, 'div', attrs={'class': 'tab-me-content-wrapper'})
			r = client.parseDOM(r, 'iframe', ret='src')

			for i in r:

				url = i

				host = re.findall('([\w]+[.][\w]+)$', urlparse(url.strip().lower()).netloc)[0]
				if not host in hostDict: continue
				host = client.replaceHTMLCodes(host)
				host = host.encode('utf-8')

				sources.append({'source': host, 'quality': 'SD', 'language': 'FR', 'url': url, 'direct': False,
				                'debridonly': False})

			return sources
		except:
			return sources

	def resolve(self, url):
		return url
