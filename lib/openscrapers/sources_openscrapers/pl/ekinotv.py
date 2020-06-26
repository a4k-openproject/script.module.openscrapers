# -*- coding: utf-8 -*-
# FanFilm Addon

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

from openscrapers.modules import cleantitle
from openscrapers.modules import client


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['pl']
		self.domains = ['ekino-tv.pl']

		self.base_link = 'https://ekino-tv.pl'
		self.search_link = '/s/search?q='
		self.resolve_link = '/watch/f/%s/%s'

	def search(self, title, localtitle, year, search_type):
		try:
			url = self.do_search(cleantitle.query(title), title, localtitle, year, search_type)
			if not url:
				url = self.do_search(cleantitle.query(localtitle), title, localtitle, year, search_type)
			return url
		except:
			return

	def do_search(self, search_string, title, localtitle, year, search_type):

		r = client.request("http://ekino-tv.pl/se/search?q=%s" % str.lower(search_string + " HD").replace(" ", "+"))
		r = client.parseDOM(r, 'div', attrs={'class': 'movies-list-item'})
		r = [x.encode('utf-8') for x in r]
		local_simple = cleantitle.get(localtitle)
		title_simple = cleantitle.get(title)
		for row in r:
			row = client.parseDOM(row, 'div', attrs={'class': 'opis-list'})[0]
			title_found = client.parseDOM(row, 'div', attrs={'class': 'title'})[0]
			link = client.parseDOM(title_found, 'a', ret='href')[0]
			if not search_type in link:
				continue

			local_found = client.parseDOM(str(title_found).replace("Å ", "ń"), 'a')[0]
			local_found = local_found.replace('&nbsp;', '')
			local_found = local_found.replace('ENG', '')
			local_found = local_found.replace('CAM', '')
			local_found = local_found.replace('HD', '')
			local_found = local_found.replace('-', '')
			local_found = local_found.replace(' ', '')

			title_found = client.parseDOM(title_found, 'a', attrs={'class': 'blue'})
			if not title_found or not title_found[0]:
				title_found = local_found
			else:
				title_found = title_found[0]

			local_found = local_found.replace('&nbsp;', '')
			title_found = title_found.replace('&nbsp;', '')
			year_found = client.parseDOM(row, 'p', attrs={'class': 'cates'})
			if year_found:
				year_found = year_found[0][:4]
			title_match = cleantitle.get(local_found) == local_simple or cleantitle.get(title_found) == title_simple
			year_match = (not year_found) or year == year_found

			if title_match and year_match:
				return link

	def movie(self, imdb, title, localtitle, aliases, year):
		return self.search(title, localtitle, year, '/movie/')

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		return self.search(tvshowtitle, localtvshowtitle, year, '/serie/')

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		url = urljoin(self.base_link, url)
		r = client.request(url)
		r = client.parseDOM(r, 'div', attrs={'id': 'list-series'})[0]
		p = client.parseDOM(r, 'p')
		index = p.index('Sezon ' + season)
		r = client.parseDOM(r, 'ul')[index]
		r = client.parseDOM(r, 'li')
		for row in r:
			ep_no = client.parseDOM(row, 'div')[0]
			if ep_no == episode:
				return client.parseDOM(row, 'a', ret='href')[0]
		return None

	def get_lang_by_type(self, lang_type):
		if lang_type:
			lang_type = lang_type[0]
			if 'Lektor' in lang_type:
				return 'pl', 'Lektor'
			if 'Dubbing' in lang_type:
				return 'pl', 'Dubbing'
			if 'Napisy' in lang_type:
				return 'pl', 'Napisy'
			if 'PL' in lang_type:
				return 'pl', None
		return 'en', None

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if url is None:
				return sources

			r = client.request(urljoin(self.base_link, url), redirect=False)

			rows = client.parseDOM(r, 'ul', attrs={'class': 'players'})[0]
			rows = client.parseDOM(rows, 'li')
			rows.pop()
			rows2 = client.parseDOM(r, 'div', attrs={'role': 'tabpanel'})

			for i in range(len(rows)):
				row = rows[i]
				row2 = rows2[i]
				link = client.parseDOM(row2, 'a', ret='onClick')[0]
				data = client.parseDOM(row, 'a')[0]
				qual = client.parseDOM(row, 'img ', ret='title')
				lang_type = client.parseDOM(row, 'i ', ret='title')
				q = 'SD'
				if qual and 'Wysoka' in qual[0]:
					q = '720p'
				lang, info = self.get_lang_by_type(lang_type)
				host = data.splitlines()[0].strip()
				sources.append(
					{'source': host, 'quality': q, 'language': lang, 'url': link, 'info': info, 'direct': False,
					 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		try:
			splitted = url.split("'")
			host = splitted[1]
			video_id = splitted[3]
			transl_url = urljoin(self.base_link, self.resolve_link) % (host, video_id)
			result = client.request(transl_url, redirect=False, cookie="prch=true")
			scripts = client.parseDOM(result, 'script')
			for script in scripts:
				if 'var url' in script:
					link = script.split("'")[1]
					if not 'watch' in link:
						return link
					result = client.request(link)
					video_link = client.parseDOM(result, 'iframe ', ret='src')[0]
					return video_link
		except:
			return None
