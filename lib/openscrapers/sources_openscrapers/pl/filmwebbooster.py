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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils

try:
	from HTMLParser import HTMLParser
except:
	from html.parser import HTMLParser


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['pl']
		self.domains = ['filmwebbooster.pl']

		self.base_link = "http://www.filmweb.pl"
		self.search_film = "/films/search?q=%s"
		self.search_serial = "/serials/search?q=%s"

	def movie(self, imdb, title, localtitle, aliases, year):
		return self.search(title, localtitle, year)

	def contains_word(self, str_to_check, word):
		return re.search(r'\b' + word + r'\b', str_to_check, re.IGNORECASE)

	def contains_all_wors(self, str_to_check, words):
		for word in words:
			if not self.contains_word(str_to_check, word):
				return False
		return True

	def search(self, title, localtitle, year):
		try:
			searchtitles = (str(localtitle), str(title))
			for searchtitle in searchtitles:

				response = requests.get(self.base_link + self.search_film % searchtitle)
				result = response.content
				h = HTMLParser()
				result = h.unescape(result)
				result = client.parseDOM(result, 'ul', attrs={'class': 'resultsList hits'})
				items = client.parseDOM(result, 'li')
				items = [x for x in items if not str(x).startswith("<a href")]
				orgtitles = []
				for content in items:
					try:
						orgtitle = str(
							client.parseDOM(content, 'div', attrs={'class': 'filmPreview__originalTitle'})[0])
					except:
						orgtitle = "0"
						pass
					orgtitles.append(orgtitle)
				ids = client.parseDOM(items, 'data', ret='data-id')
				titles = client.parseDOM(result, 'data', ret='data-title')
				years = client.parseDOM(result, 'span', attrs={'class': 'filmPreview__year'})

				for item in zip(titles, ids, years, orgtitles):
					f_title = str(item[0])
					f_id = str(item[1])
					f_year = str(item[2])
					f_orgtitle = str(item[3])
					teststring = cleantitle.normalize(cleantitle.getsearch(searchtitle))
					words = cleantitle.normalize(cleantitle.getsearch(f_title)).split(" ")
					if self.contains_all_wors(teststring, words) and year == f_year:
						return (f_title, f_id, f_year, f_orgtitle, "FILM")
		except:
			return

	def search_ep(self, titles, season, episode, year):
		try:
			searchtitles = titles
			for searchtitle in searchtitles:

				response = requests.get(self.base_link + self.search_serial % searchtitle)
				result = response.content
				h = HTMLParser()
				result = h.unescape(result)
				result = client.parseDOM(result, 'ul', attrs={'class': 'resultsList hits'})
				items = client.parseDOM(result, 'li')
				items = [x for x in items if not str(x).startswith("<a href")]
				orgtitles = []
				for content in items:
					try:
						orgtitle = str(
							client.parseDOM(content, 'div', attrs={'class': 'filmPreview__originalTitle'})[0])
					except:
						orgtitle = "0"
						pass
					orgtitles.append(orgtitle)
				ids = client.parseDOM(items, 'data', ret='data-id')
				titles = client.parseDOM(result, 'data', ret='data-title')
				years = client.parseDOM(result, 'span', attrs={'class': 'filmPreview__year'})

				for item in zip(titles, ids, years, orgtitles):
					f_title = str(item[0])
					f_id = str(item[1])
					f_year = str(item[2])
					f_orgtitle = str(item[3])
					teststring = cleantitle.normalize(cleantitle.getsearch(searchtitle))
					words = cleantitle.normalize(cleantitle.getsearch(f_title)).split(" ")
					if self.contains_all_wors(teststring, words) and year == f_year:
						return (f_title, f_id, f_year, f_orgtitle, "SERIAL", season, episode)
		except:
			return

	def get_lang_by_type(self, lang_type):
		if lang_type == 'Dubbing PL':
			return 'pl', 'Dubbing'
		elif lang_type == 'Dubbing':
			return 'pl', 'Dubbing'
		elif lang_type == 'Napisy PL':
			return 'pl', 'Napisy'
		elif lang_type == 'Napisy':
			return 'pl', 'Napisy'
		elif lang_type == 'Lektor PL':
			return 'pl', 'Lektor'
		elif lang_type == 'Lektor':
			return 'pl', 'Lektor'
		elif lang_type == 'LEKTOR_AMATOR':
			return 'pl', 'Lektor'
		elif lang_type == 'POLSKI':
			return 'pl', None
		return 'en', None

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		if localtvshowtitle == "Vikings":
			localtvshowtitle = "Wikingowie"
		titles = (tvshowtitle, localtvshowtitle)
		return titles, year

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		return self.search_ep(url[0], season, episode, url[1])  # url = titles & year

	def sources(self, url, hostDict, hostprDict):

		sources = []
		try:
			if url is None:
				return sources

			typ = url[4]

			headers = {
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0",
				"http.content_type": "application/x-www-form-urlencoded; charset=UTF-8"
			}
			data = ''
			if typ == "SERIAL":
				title = url[0]
				id = url[1]
				year = url[2]
				orgtitle = url[3]
				sezon = url[5]
				epizod = url[6]
				if orgtitle != "0":
					data = {"id": int(id),
					        "type": typ,
					        "title": title,
					        "year": int(year),
					        "sezon": str(sezon),
					        "odcinek": str(epizod),
					        "site": "filmdb",
					        "browser": "chrome"
					        }
				else:
					data = {"id": int(id),
					        "type": typ,
					        "title": title,
					        "originalTitle": str(orgtitle),
					        "year": int(year),
					        "sezon": str(sezon),
					        "odcinek": str(epizod),
					        "site": "filmdb",
					        "browser": "chrome"
					        }
			if typ == "FILM":
				title = url[0]
				id = url[1]
				year = url[2]
				orgtitle = url[3]
				if orgtitle != "0":
					data = {"id": int(id),
					        "type": typ,
					        "title": str(title),
					        "originalTitle": str(orgtitle),
					        "year": int(year),
					        "site": "filmdb",
					        "browser": "chrome"
					        }
				else:
					data = {"id": int(id),
					        "type": typ,
					        "title": str(title),
					        "year": int(year),
					        "site": "filmdb",
					        "browser": "chrome"
					        }
			data = {"json": json.dumps(data, ensure_ascii=False)}
			response = requests.post("http://fboost.pl/api/api.php", data=data, headers=headers)
			content = json.loads(response.content)
			for code in zip(content[u'link'], content[u'wersja']):
				wersja = str(code[1])
				lang, info = self.get_lang_by_type(wersja)
				test = requests.post("http://fboost.pl/api/player.php?src=%s" % code[0]).content
				link = re.search("""iframe src="(.*)" style""", test)
				link = link.group(1)
				if len(link) < 2:
					continue
				if "cda.pl" in link:
					try:
						response = requests.get(link).content
						test = client.parseDOM(response, 'div', attrs={'class': 'wrapqualitybtn'})
						urls = client.parseDOM(test, 'a', ret='href')
						for url in urls:
							valid, host = source_utils.is_host_valid(url, hostDict)
							q = source_utils.check_url(url)
							sources.append({'source': host, 'quality': q, 'language': lang, 'url': url, 'info': info,
							                'direct': False, 'debridonly': False})
						continue
					except:
						pass
				if "rapidvideo.com" in link:
					try:
						response = requests.get(link).content
						test = re.findall("""(https:\/\/www.rapidvideo.com\/e\/.*)">""", response)
						numGroups = len(test)
						for i in range(1, numGroups):
							url = test[i]
							valid, host = source_utils.is_host_valid(url, hostDict)
							q = source_utils.check_url(url)
							sources.append({'source': host, 'quality': q, 'language': lang, 'url': url, 'info': info,
							                'direct': False, 'debridonly': False})
						continue
					except:
						pass
				valid, host = source_utils.is_host_valid(link, hostDict)
				q = source_utils.check_url(link)
				sources.append(
					{'source': host, 'quality': q, 'language': lang, 'url': link, 'info': info, 'direct': False,
					 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
