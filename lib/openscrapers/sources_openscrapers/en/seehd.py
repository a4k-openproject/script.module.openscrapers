# -*- coding: UTF-8 -*-

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
		self.domains = ['seehd.pl']
		self.base_link = 'http://www.seehd.pl'
		# self.search_link = '/%s-%s-watch-online/' # most movie titles do not have year in link on seehd.pl then do have year
		self.movie_link = '/%s-watch-online/'
		self.episode_link = '/%s-%s/'
		self.scraper = cfscrape.create_scraper()


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title)
			url = self.base_link + self.movie_link % (title)
			return url
		except:
			source_utils.scraper_error('SEEHD')
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			return url
		except:
			source_utils.scraper_error('SEEHD')
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			title = url
			season = '%01d' % int(season)
			episode = '%01d' % int(episode)
			se = 'season-%s-episode-%s' % (season, episode)
			url = self.base_link + self.episode_link % (title, se)
			return url
		except:
			source_utils.scraper_error('SEEHD')
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			hostDict = hostprDict + hostDict
			r = self.scraper.get(url).content

			match = re.compile('<iframe.+?src="(.+?)://(.+?)/(.+?)"').findall(r)
			for http, host, url in match:
				host = host.replace('www.', '')
				url = '%s://%s/%s' % (http, host, url)
				valid, host = source_utils.is_host_valid(url, hostDict)
				if valid:
					sources.append({'source': host, 'quality': '720p', 'info': '', 'language': 'en', 'url': url, 'direct': False,
					                'debridonly': False})
			return sources
		except Exception:
			source_utils.scraper_error('SEEHD')
			return sources


	def resolve(self, url):
		return url