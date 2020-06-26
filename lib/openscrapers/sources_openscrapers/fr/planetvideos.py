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
import time

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client


class source:
	def __init__(self):
		self.priority = 0
		self.language = ['fr']
		self.domains = ['planetevideos.xyz']
		self.base_link = 'https://www.planetevideos.xyz'
		self.search_link = '/?s=%s'

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

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			url = self.__search(data['tvshowtitle'], season)
			if not url and data['tvshowtitle'] is not data['localtvshowtitle']: url = self.__search(
				data['localtvshowtitle'], season)
			if not url: return

			r = client.request(urljoin(self.base_link, url))

			r = client.parseDOM(r, 'div', attrs={'class': 'keremiya_part'})
			r = re.compile('(<a.+?/a>)', re.DOTALL).findall(''.join(r))
			r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'span')) for i in r]
			r = [(i[0][0], re.findall('(\d+)', i[1][0])) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
			r = [i[0] for i in r if len(i[1]) > 0 and int(i[1][0]) == int(episode)][0]

			url = re.findall('(?://.+?|)(/.+)', r)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []

		try:
			if url is None:
				return sources

			hostDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]
			locDict = [i[0] for i in hostDict]


			r = client.request(urljoin(self.base_link, url))

			r = client.parseDOM(r, 'div', attrs={'class': 'filmicerik'})
			r = client.parseDOM(r, 'p')
			r = [(client.parseDOM(i, 'iframe', ret='src'), client.parseDOM(i, 'b'),
			      client.parseDOM(r, 'span', attrs={'class': 'lg'})) for i in r]
			r = [(i[0], [x.lower().replace('lecteur', '').strip() for x in i[1]], i[2][0]) for i in r if
			     len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
			r = [(i[0], [[y[1] for y in hostDict if y[0] == x][0] for x in i[1] if x in locDict], i[2],
			      re.findall('\((.+?)\)$', i[2])) for i in r]
			r = [(dict(zip(i[0], i[1])), i[3][0] if len(i[2]) > 0 else i[2]) for i in r]

			for links, lang in r:
				for link, host in links.iteritems():
					sources.append(
						{'source': host, 'quality': 'SD', 'language': 'fr', 'info': lang, 'url': link, 'direct': False,
						 'debridonly': False})

			return sources
		except:
			return sources

	def resolve(self, url):
		try:
			k = client.request(url)
			k = re.compile('var k=\"(.+?)\"', re.MULTILINE | re.DOTALL).findall(k)[0]

			time.sleep(5)

			r = client.request('http://www.protect-stream.com/secur2.php', post=urlencode({'k': k}))
			url = client.parseDOM(r, 'a', attrs={'class': 'button'}, ret='href')[0]
			return url
		except:
			return

	def __search(self, title, season):
		try:
			query = self.search_link % (quote_plus(cleantitle.query(title)))
			query = urljoin(self.base_link, query)

			t = cleantitle.get(title)

			r = client.request(query)

			r = client.parseDOM(r, 'div', attrs={'class': 'moviefilm'})
			r = client.parseDOM(r, 'div', attrs={'class': 'movief'})
			r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in r]
			r = [(i[0][0], i[1][0].lower()) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
			r = [(i[0], i[1], re.findall('(.+?)\s+(?:saison)\s+(\d+)', i[1])) for i in r]
			r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
			r = [(i[0], i[1], re.findall('\((.+?)\)$', i[1]), i[2]) for i in r]
			r = [(i[0], i[2][0] if len(i[2]) > 0 else i[1], i[3]) for i in r]
			r = [i[0] for i in r if t == cleantitle.get(i[1]) and int(i[2]) == int(season)][0]

			url = re.findall('(?://.+?|)(/.+)', r)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			return url
		except:
			return
