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

from openscrapers.modules import cleantitle
from openscrapers.modules import client


class source:
	def __init__(self):

		self.priority = 1
		self.language = ['pl']
		self.domains = ['filmdom.fun']
		self.base_link = 'https://filmdom.fun'
		self.search_link = 'https://filmdom.fun/videos/search?q=%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		return self.search(title, localtitle, year)

	def contains_word(self, str_to_check, word):
		if str(word).lower() in str(str_to_check).lower():
			return True
		return False

	def contains_all_words(self, str_to_check, words):
		for word in words:
			if not self.contains_word(str_to_check, word):
				return False
		return True

	def search(self, title, localtitle, year):
		try:
			titles = []
			title2 = title.split('.')[0]
			localtitle2 = localtitle.split('.')[0]
			titles.append(cleantitle.normalize(cleantitle.getsearch(title2)))
			titles.append(cleantitle.normalize(cleantitle.getsearch(localtitle2)))
			titles.append(title2)
			titles.append(localtitle2)

			for title in titles:
				title = title.replace(" ", "+")
				result = client.request(self.search_link % title)

				result = client.parseDOM(result, 'div', attrs={'class': 'col-xs-4'})
				for item in result:
					try:
						rok = client.parseDOM(item, 'div', attrs={'class': 'col-sm-8'})
						rok_nazwa = client.parseDOM(rok, 'p')[0].lower()
						link = client.parseDOM(item, 'a', ret='href')[0]
						link = self.base_link + link
						words = title.lower().split(" ")
						if self.contains_all_words(rok_nazwa, words) and year in rok_nazwa:
							return link
					except:
						continue
			return
		except:
			return

	def get_lang_by_type(self, lang_type):
		if "dubbing" in lang_type.lower():
			if "kino" in lang_type.lower():
				return 'pl', 'Dubbing Kino'
			return 'pl', 'Dubbing'
		elif 'napisy pl' in lang_type.lower():
			return 'pl', 'Napisy'
		elif 'napisy' in lang_type.lower():
			return 'pl', 'Napisy'
		elif 'lektor pl' in lang_type.lower():
			return 'pl', 'Lektor'
		elif 'lektor' in lang_type.lower():
			return 'pl', 'Lektor'
		elif 'POLSKI' in lang_type.lower():
			return 'pl', None
		elif 'pl' in lang_type.lower():
			return 'pl', None
		return 'en', None

	def sources(self, url, hostDict, hostprDict):

		sources = []
		try:
			if url is None:
				return sources

			result = client.request(url)

			result = client.parseDOM(result, 'table', attrs={'class': 'table table-striped'})
			result = client.parseDOM(result, 'tbody')
			result = client.parseDOM(result, 'tr')
			for item in result:
				try:
					content = client.parseDOM(item, 'td')
					link = client.parseDOM(item, 'a', ret='href')[0]
					host = client.parseDOM(item, 'a')[0]
					lang, info = self.get_lang_by_type(content[1])
					sources.append({'source': host, 'quality': 'SD', 'language': lang, 'url': link, 'info': info,
					                'direct': False, 'debridonly': False})
				except:
					continue
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
