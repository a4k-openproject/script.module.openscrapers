# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 10-16-2019 by JewBMX in Scrubs.

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
from openscrapers.modules import client
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['watchseries-tv.cc']
		self.base_link = 'https://watchseries-tv.cc'
		self.search_link = '/search?q=%s'


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			tvshowtitle = cleantitle.geturl(tvshowtitle)
			url = self.base_link + self.search_link % (tvshowtitle.replace(' ', '+').replace('-', '+').replace('++', '+'))
			page = client.request(url)
			items = client.parseDOM(page, 'div', attrs={'class': 'content-left'})
			for item in items:
				match = re.compile('<a href="(.+?)">', re.DOTALL).findall(item)
				for url in match:
					if cleantitle.get(tvshowtitle) in cleantitle.get(url):
						url = self.base_link + url
						return url
			return
		except:
			source_utils.scraper_error('WATCHSERIESTV')
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			page = client.request(url)
			items = client.parseDOM(page, 'div', attrs={'class': 'season-table-row'})
			for item in items:
				try:
					url = re.compile('<a href="(.+?)">', re.DOTALL).findall(item)[0]
				except:
					pass
				sea = client.parseDOM(item, 'div', attrs={'class': 'season-table-season'})[0]
				epi = client.parseDOM(item, 'div', attrs={'class': 'season-table-ep'})[0]
				if cleantitle.get(season) in cleantitle.get(sea) and cleantitle.get(episode) in cleantitle.get(epi):
					url = self.base_link + url
					return url
			return
		except:
			source_utils.scraper_error('WATCHSERIESTV')
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			hostDict = hostprDict + hostDict
			sources = []
			if url == None:
				return sources
			page = client.request(url)
			links = re.compile('<a rel="nofollow" target="blank" href="(.+?)"', re.DOTALL).findall(page)
			for link in links:
				link = "https:" + link if not link.startswith('http') else link
				valid, host = source_utils.is_host_valid(link, hostDict)
				if valid:
					if host in str(sources):
						continue
					quality, info = source_utils.get_release_quality(link, link)
					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': False, 'debridonly': False})
			return sources
		except:
			source_utils.scraper_error('WATCHSERIESTV')
			return sources


	def resolve(self, url):
		return url