# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.

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
from openscrapers.modules import getSum
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['putlockersonline.top']
		self.base_link = 'https://putlockersonline.top'
		self.search_link = '/search_movies?s=%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			mtitle = cleantitle.geturl(title).replace('-', '+')
			theurl = self.base_link + self.search_link % mtitle
			searchPage = getSum.get(theurl)
			results = getSum.findEm(searchPage, '<a href="https://putlockersonline.top/watch(.+?)" title="(.+?)"><b>')
			if results:
				for url, checkit in results:
					url = "https://putlockersonline.top/watch" + url
					zcheck = '%s (%s)' % (title, year)
					if zcheck in checkit:
						return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			hostDict = hostDict + hostprDict
			moviePage = getSum.get(url)
			results = getSum.findEm(moviePage, '<td class="entry2" valign="middle">.+?<a href="(.+?)" target="_blank"')
			if results:
				for url in results:
					valid, host = source_utils.is_host_valid(url, hostDict)
					if valid:
						quality, info = source_utils.get_release_quality(url, url)
						sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
						                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url