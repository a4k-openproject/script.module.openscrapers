# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 05-06-2019 by JewBMX in Scrubs.

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
import traceback

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import log_utils
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['1putlocker.io']
		self.base_link = 'https://www15.1putlocker.io'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title)
			url = self.base_link + '/%s/' % title
			return url
		except Exception:
			failure = traceback.format_exc()
			log_utils.log('1putlocker - Exception: \n' + str(failure))
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except Exception:
			failure = traceback.format_exc()
			log_utils.log('1putlocker - Exception: \n' + str(failure))
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			tvshowtitle = url
			url = self.base_link + '/episode/%s-season-%s-episode-%s/' % (tvshowtitle, season, episode)
			return url
		except Exception:
			failure = traceback.format_exc()
			log_utils.log('1putlocker - Exception: \n' + str(failure))
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			r = self.scraper.get(url).content
			try:
				match = re.compile('<iframe src="(.+?)"').findall(r)
				for url in match:
					quality = source_utils.check_url(url)
					valid, host = source_utils.is_host_valid(url, hostDict)
					if valid:
						sources.append(
							{'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False,
							 'debridonly': False})
			except:
				return
		except Exception:
			failure = traceback.format_exc()
			log_utils.log('1putlocker - Exception: \n' + str(failure))
			return
		return sources

	def resolve(self, url):
		return url
