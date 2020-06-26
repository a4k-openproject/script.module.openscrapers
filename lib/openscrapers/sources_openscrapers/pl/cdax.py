# -*- coding: utf-8 -*-
# Covenant

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


try: from urlparse import urljoin
except ImportError: from urllib.parse import urljoin
try: from urllib import quote_plus
except ImportError: from urllib.parse import quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['pl']
		self.domains = ['cdax.online']

		self.base_link = 'https://cda-tv.pl/'
		self.search_link = '/?s=%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		return self.search(localtitle, year, 'movies')

	def search(self, localtitle, year, search_type):
		try:
			simply_name = cleantitle.get(localtitle)

			query = self.search_link % quote_plus(cleantitle.query(localtitle))
			query = urljoin(self.base_link, query)
			result = client.request(query)

			result = client.parseDOM(result, 'div', attrs={'class': 'result-item'})
			for x in result:
				correct_type = client.parseDOM(x, 'span', attrs={'class': search_type})
				correct_year = client.parseDOM(x, 'span', attrs={'class': 'year'})[0] == year
				name = client.parseDOM(x, 'div', attrs={'class': 'title'})[0]
				url = client.parseDOM(name, 'a', ret='href')[0]
				name = cleantitle.get(client.parseDOM(name, 'a')[0])
				if (correct_type and correct_year and name == simply_name):
					return url

		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		return self.search(localtvshowtitle, year, 'tvshows')

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			result = client.request(url)
			seasons = client.parseDOM(result, 'div', attrs={'class': 'se-c'})
			for season_data in seasons:
				season_no = client.parseDOM(season_data, 'div', attrs={'class': 'se-q'})[0]
				season_no = client.parseDOM(season_no, 'span')[0]
				if season_no == season:
					eps = client.parseDOM(season_data, 'li')
					for ep in eps:
						ep_no = client.parseDOM(ep, 'div', attrs={'class': 'numerando'})[0]
						ep_no = ep_no.rpartition(' ')[-1]
						if ep_no == episode:
							return client.parseDOM(ep, 'a', ret='href')[0]
		except:
			return

	def get_lang_by_type(self, lang_type):
		if lang_type == 'LEKTOR PL':
			return 'pl', 'Lektor'
		if lang_type == 'DUBBING PL':
			return 'pl', 'Dubbing'
		if lang_type == 'NAPISY PL':
			return 'pl', 'Napisy'
		if lang_type == 'PL':
			return 'pl', None
		return 'en', None

	def sources(self, url, hostDict, hostprDict):

		sources = []
		try:

			if url is None:
				return sources

			result = client.request(url)
			result = client.parseDOM(result, 'div', attrs={'id': 'downloads'})[0]
			rows = client.parseDOM(result, 'tr')

			for row in rows:
				try:
					cols = client.parseDOM(row, 'td')
					host = client.parseDOM(cols, 'img', ret='src')[0]
					host = host.rpartition('=')[-1]
					link = client.parseDOM(cols, 'a', ret='href')[0]

					valid, host = source_utils.is_host_valid(host, hostDict)
					if not valid:
						continue

					q = 'SD'
					if 'Wysoka' in cols[2]: q = '720p'

					lang, info = self.get_lang_by_type(cols[3])

					sources.append(
						{'source': host, 'quality': q, 'language': lang, 'url': link, 'info': info, 'direct': False,
						 'debridonly': False})
				except:
					pass

			return sources
		except:
			return sources

	def resolve(self, url):
		result = client.request(url)
		result = client.parseDOM(result, 'div', attrs={'class': 'boton reloading'})
		link = client.parseDOM(result, 'a', ret='href')[0]
		return link
