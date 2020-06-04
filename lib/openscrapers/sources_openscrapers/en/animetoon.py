# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 12-07-2018 by JewBMX in Scrubs.

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
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 35
		self.language = ['en']
		self.genre_filter = ['animation', 'anime']
		self.domains = ['animetoon.org', 'animetoon.tv']
		self.base_link = 'http://www.animetoon.org'
		self.scraper = cfscrape.create_scraper()


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title)
			url = '%s-%s' % (title, year)
			url = self.base_link + '/' + url
			return url
		except:
			source_utils.scraper_error('ANIMETOON')
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except:
			source_utils.scraper_error('ANIMETOON')
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			if season == '1':
				url = self.base_link + '/' + url + '-episode-' + episode
			else:
				url = self.base_link + '/' + url + '-season-' + season + '-episode-' + episode
			return url
		except:
			source_utils.scraper_error('ANIMETOON')
			return


	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			r = self.scraper.get(url).content
			match = re.compile('<div><iframe src="(.+?)"').findall(r)
			for url in match:
				host = url.split('//')[1].replace('www.', '')
				host = host.split('/')[0].split('.')[0].title()
				quality = source_utils.check_url(url)
				r = self.scraper.get(url).content
				if 'http' in url:
					match = re.compile("url: '(.+?)',").findall(r)
				else:
					match = re.compile('file: "(.+?)",').findall(r)
				for url in match:
					sources.append({'source': host, 'quality': quality, 'info': '', 'language': 'en', 'url': url, 'direct': False,
						 'debridonly': False})
		except:
			source_utils.scraper_error('ANIMETOON')
			return
		return sources


	def resolve(self, url):
		return url