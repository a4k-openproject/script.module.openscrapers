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
import requests

from openscrapers.modules import cleantitle
from openscrapers.modules import directstream
from openscrapers.modules import getSum
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 33
		self.language = ['en']
		self.domains = ['watchserieshd.tv']
		self.base_link = 'https://watchserieshd.tv'
		self.search_link = '/series/%s-season-%s-episode-%s'


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except:
			source_utils.scraper_error('WATCHSERIESHD')
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			tvshowtitle = url
			url = self.base_link + self.search_link % (tvshowtitle, season, episode)
			return url
		except:
			source_utils.scraper_error('WATCHSERIESHD')
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			if url is None:
				return sources
			sources = []
			hostDict = hostprDict + hostDict
			r = getSum.get(url)
			match = getSum.findSum(r)
			for url in match:
				if 'vidcloud' in url:
					result = getSum.get(url)
					match = getSum.findSum(result)
					for link in match:
						link = "https:" + link if not link.startswith('http') else link
						link = requests.get(link).url if 'vidnode' in link else link
						valid, host = source_utils.is_host_valid(link, hostDict)
						if valid:
							quality, info = source_utils.get_release_quality(link, link)
							sources.append(
								{'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': link,
								 'direct': False, 'debridonly': False})
				else:
					valid, host = source_utils.is_host_valid(url, hostDict)
					if valid:
						quality, info = source_utils.get_release_quality(url, url)
						sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url,
						                'direct': False, 'debridonly': False})
			return sources
		except:
			source_utils.scraper_error('WATCHSERIESHD')
			return sources


	def resolve(self, url):
		if "google" in url:
			return directstream.googlepass(url)
		elif 'vidcloud' in url:
			r = getSum.get(url)
			url = re.findall("file: '(.+?)'", r)[0]
			return url
		else:
			return url