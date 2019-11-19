# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.
# Need to add a year check in sometime to make sure there isnt false hits.

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
		self.domains = ['hubmovie.cc', 'hubmoviehd.net']
		self.base_link = 'http://hubmovie.cc'
		self.search_link = '/pages/search2/%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			search_id = cleantitle.getsearch(title)
			search_url = self.base_link + self.search_link % (search_id.replace(':', ' ').replace(' ', '%20'))
			search_results = client.request(search_url)
			match = re.compile('<a href=".(.+?)">', re.DOTALL).findall(search_results)
			for link in match:
				if cleantitle.geturl(title).lower() in link:
					url = self.base_link + link
					return url
			return
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			hostDict = hostDict + hostprDict
			if url is None:
				return sources
			html = client.request(url)
			links = re.compile('<div class="link_go">.+?<a href="(.+?)" target="_blank">', re.DOTALL).findall(html)
			for link in links:
				valid, host = source_utils.is_host_valid(link, hostDict)
				if valid:
					quality, info = source_utils.get_release_quality(link, link)
					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': info,
					                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
