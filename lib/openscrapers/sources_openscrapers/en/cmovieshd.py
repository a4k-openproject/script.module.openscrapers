# -*- coding: utf-8 -*-

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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['cmovieshd.net']
		self.base_link = 'https://cmovieshd.net'
		self.search_link = '/search/?q=%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title).replace('-', '+')
			u = self.base_link + self.search_link % title
			u = client.request(u)
			i = client.parseDOM(u, "div", attrs={"class": "movies-list"})
			for r in i:
				r = re.compile('<a href="(.+?)"').findall(r)
				for url in r:
					title = cleantitle.geturl(title).replace("+", "-")
					if not title in url:
						continue
					return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			url = url + 'watch/'
			r = client.request(url)
			qual = re.compile('class="quality">(.+?)<').findall(r)
			for i in qual:
				quality, info = source_utils.get_release_quality(i, i)
			r = client.parseDOM(r, "div", attrs={"id": "list-eps"})
			for i in r:
				t = re.compile('<a href="(.+?)"').findall(i)
				for url in t:
					t = client.request(url)
					t = client.parseDOM(t, "div", attrs={"id": "content-embed"})
					for u in t:
						i = re.findall('src="(.+?)"', u)[0].replace('load_player.html?e=', 'episode/embed/')
						i = client.request(i).replace("\\", "")
						u = re.findall('"(https.+?)"', i)
						for url in u:
							valid, host = source_utils.is_host_valid(url, hostDict)
							sources.append(
								{'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url,
								 'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
