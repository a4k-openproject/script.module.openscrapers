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
import requests

try:
	from HTMLParser import HTMLParser
except:
	from html.parser import HTMLParser

from openscrapers.modules import source_utils
from openscrapers.modules import client


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['pl']
		self.domains = ['seriale.co']

		self.base_link = 'http://seriale.co'
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

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		titles = (tvshowtitle, localtvshowtitle)
		return titles, year

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		return self.search_ep(url[0], season, episode, url[1])  # url = titles & year

	def search_ep(self, titles, season, episode, year):
		try:
			for title in titles:
				data = {
					'fid_name': title,
					'sezon': season,
					'odcinek': episode,
					'title': title
				}

				result = requests.post('http://178.19.110.218/forumserialeco/skrypt/szukaj3.php', data=data).content
				result = result.decode('utf-8')
				h = HTMLParser()
				result = h.unescape(result)
				if result:
					return title, season, episode
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			data = {
				'fid_name': url[0],
				'sezon': url[1],
				'odcinek': url[2],
				'title': url[0]
			}

			result = requests.post('http://178.19.110.218/forumserialeco/skrypt/szukaj3.php', data=data).content
			result = result.decode('utf-8')
			h = HTMLParser()
			result = h.unescape(result)
			if result:
				wersja = re.findall("""wersja: <b>(.*?)<\/b>""", result)
				id = re.findall("""url='(.*?)'""", result)
				for item in zip(wersja, id):
					try:
						if item[1]:
							info = self.get_lang_by_type(item[0])
							content = client.request("http://seriale.co/frame.php?src=" + item[1])
							video_link = str(client.parseDOM(content, 'iframe', ret='src')[0])
							valid, host = source_utils.is_host_valid(video_link, hostDict)
							if valid:
								sources.append(
									{'source': host, 'quality': 'SD', 'language': info[0], 'url': video_link,
									 'info': info[1], 'direct': False,
									 'debridonly': False})
							else:
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
