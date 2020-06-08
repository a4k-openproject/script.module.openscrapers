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

import json
import re
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
		self.domains = ['netfilmy.pl', 'kinonet.pl']

		self.base_link = 'https://netfilmy.pl'
		self.search_link = 'https://netfilmy.pl/?s='
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
			titles.append(title)
			titles.append(localtitle)
			for title in titles:
				try:
					url = self.search_link + str(title)
					result = self.session.get(url).content
					result = result.decode('utf-8')
					h = HTMLParser()
					result = h.unescape(result)
					result = client.parseDOM(result, 'div', attrs={'class': 'card-body p-2'})

					for item in result:
						try:
							nazwa = re.findall("""Film online: (.*?)\"""", item)[0]
							try:
								nazwa = re.findall(""">(.*?)<""", nazwa)[0]
							except:
								pass
							name = cleantitle.normalize(cleantitle.getsearch(nazwa))
							rok = re.findall("""Rok wydania filmu online\".*>(.*?)<""", item)[0]
							item = str(item).replace("<span style='color:red'>", "").replace("</span>", "")
							link = re.findall("""href=\"(.*?)\"""", item)[0]
							if link.startswith('//'):
								link = "https:" + link
							name = name.replace("  ", " ")
							title = title.replace("  ", " ")
							words = name.split(" ")
							if self.contains_all_words(title, words) and str(year) in rok:
								return link
						except:
							continue
				except:
					continue
		except:
			return

	def movie(self, imdb, title, localtitle, aliases, year):
		return self.search(title, localtitle, year, True)

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		if localtvshowtitle == "Vikings":
			localtvshowtitle = "Wikingowie"
		titles = (tvshowtitle, localtvshowtitle)
		return titles, year

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		return self.search_ep(url[0], season, episode, url[1])  # url = titles & year

	def search_ep(self, titles, season, episode, year):
		try:
			query = 'S{:02d}E{:02d}'.format(int(season), int(episode))
			for title in titles:
				url = self.search_link + str(title)
				result = self.session.get(url).content
				result = result.decode('utf-8')
				h = HTMLParser()
				result = h.unescape(result)
				result = client.parseDOM(result, 'div', attrs={'class': 'card-body p-2'})

				for item in result:
					nazwa = re.findall("""Film online: (.*?)\"""", item)[0]
					name = cleantitle.normalize(cleantitle.getsearch(nazwa))
					rok = re.findall("""Rok wydania filmu online\".*>(.*?)<""", item)[0]
					item = str(item).replace("<span style='color:red'>", "").replace("</span>", "")
					link = re.findall("""href=\"(.*?)\"""", item)[0]
					if link.startswith('//'):
						link = "https:" + link
					name = name.replace("  ", " ")
					title = title.replace("  ", " ")
					words = title.split(" ")
					if self.contains_all_words(name, words) and str(year) in rok:
						content = requests.get(link.replace('filmy', 'seriale')).content
						content = client.parseDOM(content, 'div', attrs={'class': 'tabela_wiersz mb-1'})
						for odcinek in content:
							if query.lower() in odcinek.lower():
								link = str(client.parseDOM(odcinek, 'a', ret='href')[0])
								return self.base_link + link

		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			# import pydevd
			# pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)
			sources = []
			result = self.session.get(url).content
			result = result.decode('utf-8')
			h = HTMLParser()
			result = h.unescape(result)
			result = client.parseDOM(result, 'div', attrs={'class': 'tabela_wiersz mb-1'})
			for counter, item in enumerate(result, 0):
				try:
					test = client.parseDOM(result, 'span', attrs={'class': 'tabela_text'})
					info = test[(2 + (3 * counter))]
					info = self.get_lang_by_type(info)
					quality = test[(1 + (3 * counter))]
					quality = source_utils.check_url(quality)
					try:
						id = re.findall("""ShowMovie\('(.*?)'\)""", item)[0]
					except:
						id = re.findall("""ShowSer\('(.*?)'\)""", item)[0]
					try:
						host = re.findall("""<\/i> (.*?)<\/span>""", item)[0]
						if 'serial' in url:
							id = id + '/s'
						sources.append(
							{'source': host, 'quality': quality, 'language': info[0], 'url': id, 'info': info[1],
							 'direct': False,
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

	def resolve(self, id):
		id2 = id
		id = str(id).replace("/s", '')
		test = json.loads(self.session.post("https://kinonet.pl/iframe.php", data={'query': id}).content)
		if str(id2).endswith('/s'):
			link = "https://kinonet.pl/embed_s.php?v=" + test[u'0']
		else:
			link = "https://kinonet.pl/embed.php?v=" + test[u'0']
		video_link = str(client.parseDOM(self.session.get(link).content, 'iframe', ret='src')[0])
		return str(video_link)
