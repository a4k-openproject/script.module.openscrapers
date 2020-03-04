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

import re

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import more_sources
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['cartoonhd.to']
		self.base_link = 'https://www.cartoonhd.to'
		self.search_link = '/?s=%s'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			searchName = cleantitle.getsearch(title)
			searchURL = self.base_link + self.search_link % (searchName.replace(':', ' ').replace(' ', '+'))
			searchPage = self.scraper.get(searchURL).content
			results = re.compile('<a href="(.+?)">(.+?)</a>.+?<span class="year">(.+?)</span>', re.DOTALL).findall(
				searchPage)
			for url, zName, zYear in results:
				if cleantitle.geturl(title).lower() in cleantitle.geturl(zName).lower():
					if year in str(zYear):
						url = url + "?watching"
						return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			tvshowtitle = url
			url = self.base_link + '/episodes/%s-season-%s-episode-%s/?watching' % (tvshowtitle, season, episode)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			hostDict = hostDict + hostprDict
			sourcePage = self.scraper.get(url).content
			links = re.compile('<iframe.+?src="(.+?)"', re.DOTALL).findall(sourcePage)
			for link in links:
				if "gomostream.com" in link:
					for source in more_sources.more_gomo(link, hostDict):
						sources.append(source)
				else:
					quality, info = source_utils.get_release_quality(link, link)
					valid, host = source_utils.is_host_valid(link, hostDict)
					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': info,
					                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
