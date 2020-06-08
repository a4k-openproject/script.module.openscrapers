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

import requests

try:
	from HTMLParser import HTMLParser
except:
	from html.parser import HTMLParser

from openscrapers.modules import source_utils
from openscrapers.modules import cleantitle
from openscrapers.modules import client


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['pl']
		self.domains = ['horrortube.pl']

		self.base_link = 'https://horrortube.pl'
		self.search_link = 'https://horrortube.pl/wyszukiwarka?phrase='
		self.session = requests.Session()

	def contains_word(self, str_to_check, word):
		if str(word).lower() in str(str_to_check).lower():
			return True
		return False

	def contains_all_words(self, str_to_check, words):
		for word in words:
			if not self.contains_word(str_to_check, word):
				return False
		return True

	def search(self, title, localtitle, year, is_movie_search):
		try:
			titles = []
			titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
			titles.append(cleantitle.normalize(cleantitle.getsearch(localtitle)))

			for title in titles:
				url = self.search_link + str(title)
				result = self.session.get(url).content
				result = result.decode('utf-8')
				h = HTMLParser()
				result = h.unescape(result)
				result = client.parseDOM(result, 'div', attrs={'class': 'col-sm-4'})

				for item in result:
					try:
						link = str(client.parseDOM(item, 'a', ret='href')[0])
						if link.startswith('//'):
							link = "https:" + link
						nazwa = str(client.parseDOM(item, 'a', ret='title')[0])
						name = cleantitle.normalize(cleantitle.getsearch(nazwa))
						name = name.replace("  ", " ")
						title = title.replace("  ", " ")
						words = title.split(" ")
						if self.contains_all_words(name, words) and str(year) in link:
							return link
					except:
						continue
		except:
			return

	def movie(self, imdb, title, localtitle, aliases, year):
		return self.search(title, localtitle, year, True)

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			result = self.session.get(url).content
			result = result.decode('utf-8')
			h = HTMLParser()
			result = h.unescape(result)
			result = client.parseDOM(result, 'table', attrs={'class': 'table table-bordered'})
			result = client.parseDOM(result, 'tr')
			for item in result:
				try:
					tabela = client.parseDOM(item, 'td')
					info = self.get_lang_by_type(tabela[1])
					quality = tabela[2]
					if 'wysoka' in quality.lower():
						quality = '720p'
					else:
						quality = 'SD'
					try:
						video_link = str(client.parseDOM(tabela[0], 'a', ret='href')[0])
						valid, host = source_utils.is_host_valid(video_link, hostDict)
						sources.append(
							{'source': host, 'quality': quality, 'language': info[0], 'url': video_link,
							 'info': info[1], 'direct': False,
							 'debridonly': False})
					except:
						continue
				except:
					continue
			return sources
		except:
			return sources

	def get_lang_by_type(self, lang_type):
		if "dubbing" in lang_type.lower():
			if "kino" in lang_type.lower():
				return 'pl', 'Dubbing Kino'
			return 'pl', 'Dubbing'
		elif 'lektor pl' in lang_type.lower():
			return 'pl', 'Lektor'
		elif 'lektor' in lang_type.lower():
			return 'pl', 'Lektor'
		elif 'napisy pl' in lang_type.lower():
			return 'pl', 'Napisy'
		elif 'napisy' in lang_type.lower():
			return 'pl', 'Napisy'
		elif 'POLSKI' in lang_type.lower():
			return 'pl', None
		elif 'pl' in lang_type.lower():
			return 'pl', None
		return 'en', None

	def resolve(self, url):
		return str(url)
