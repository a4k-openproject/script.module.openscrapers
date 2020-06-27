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


try: from urlparse import urljoin
except ImportError: from urllib.parse import urljoin
try: from urllib import quote
except ImportError: from urllib.parse import quote

from openscrapers.modules import source_utils
from openscrapers.modules import cleantitle
from openscrapers.modules import client


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['pl']
		self.domains = ['cda.pl']

		self.base_link = 'https://www.cda.pl/'
		self.search_link = 'video/show/%s?duration=dlugie&section=&quality=720p&section=&s=best&section='
		self.search_link_ep = "video/show/%s?duration=srednie&section=&quality=720p&section=&s=best&section="
		self.anime = False
		self.year = 0

	def contains_word(self, str_to_check, word):
		if str(word).lower() in str(str_to_check).lower():
			return True
		return False

	def contains_all_words(self, str_to_check, words):
		if self.anime:
			words_to_check = str_to_check.split(" ")
			for word in words_to_check:
				try:
					liczba = int(word)
					for word2 in words:
						try:
							liczba2 = int(word2)
							if liczba != liczba2 and liczba2 != self.year and liczba != self.year:
								return False
						except:
							continue
				except:
					continue
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
				url = urljoin(self.base_link, self.search_link)
				url = url % quote(str(title).replace(" ", "_"))

				result = client.request(url)
				result = client.parseDOM(result, 'div', attrs={'class': 'video-clip-wrapper'})
				linki = []
				for item in result:
					try:
						link = str(client.parseDOM(item, 'a', ret='href')[0])
						nazwa = str(client.parseDOM(item, 'a', attrs={'class': 'link-title-visit'})[0])
						name = cleantitle.normalize(cleantitle.getsearch(nazwa))
						name = name.replace("  ", " ")
						title = title.replace("  ", " ")
						words = title.split(" ")
						if self.contains_all_words(name, words) and str(year) in name:
							linki.append(link)
					except:
						continue
				return linki
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		return (tvshowtitle, localtvshowtitle), year

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		anime = source_utils.is_anime('show', 'tvdb', tvdb)
		self.year = int(url[1])
		self.anime = anime
		if anime:
			epNo = " " + source_utils.absoluteNumber(tvdb, episode, season)
		else:
			epNo = ' s' + season.zfill(2) + 'e' + episode.zfill(2)
		return self.search_ep(url[0][0] + epNo, url[0][1] + epNo)

	def search_ep(self, title1, title2):
		try:
			titles = []
			titles.append(cleantitle.normalize(cleantitle.getsearch(title1)))
			titles.append(cleantitle.normalize(cleantitle.getsearch(title2)))

			for title in titles:
				url = urljoin(self.base_link, self.search_link_ep)
				url = url % quote(str(title).replace(" ", "_"))

				result = client.request(url)
				result = client.parseDOM(result, 'div', attrs={'class': 'video-clip-wrapper'})
				linki = []
				for item in result:
					try:
						link = str(client.parseDOM(item, 'a', ret='href')[0])
						nazwa = str(client.parseDOM(item, 'a', attrs={'class': 'link-title-visit'})[0])
						name = cleantitle.normalize(cleantitle.getsearch(nazwa))
						name = name.replace("  ", " ")
						title = title.replace("  ", " ")
						words = title.split(" ")
						if self.contains_all_words(name, words):
							linki.append(link)
					except:
						continue
				return linki
		except:
			return

	def movie(self, imdb, title, localtitle, aliases, year):
		return self.search(title, localtitle, year, True)

	def sources(self, linki, hostDict, hostprDict):
		sources = []
		try:
			for url in linki:
				try:
					if url is None:
						return sources

					url = urljoin(self.base_link, url)
					result = client.request(url)
					title = client.parseDOM(result, 'span', attrs={'style': 'margin-right: 3px;'})[0]
					lang, info = self.get_lang_by_type(title)

					valid, host = source_utils.is_host_valid(url, hostDict)
					if not valid:
						continue

					if "?wersja=1080p" in result:
						sources.append(
							{'source': host, 'quality': '1080p', 'language': lang, 'url': url + "?wersja=1080p",
							 'info': info, 'direct': False, 'debridonly': False})
					if "?wersja=720p" in result:
						sources.append({'source': host, 'quality': '720p', 'language': lang, 'url': url + "?wersja=720p",
						                'info': info, 'direct': False, 'debridonly': False})
					if "?wersja=480p" in result:
						sources.append({'source': host, 'quality': 'SD', 'language': lang, 'url': url + "?wersja=480p",
						                'info': info, 'direct': False, 'debridonly': False})
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

	def resolve(self, url):
		link = str(url).replace("//", "/").replace(":/", "://").split("?")[0]
		return str(link)
