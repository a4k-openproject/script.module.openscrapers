# -*- coding: UTF-8 -*-
# modified by Venom for Openscrapers (4-20-2020)

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.


import re

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 32
		self.language = ['en']
		self.domains = ['coolmoviezone.rocks']
		self.base_link = 'https://coolmoviezone.rocks'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			mtitle = cleantitle.geturl(title)
			url = self.base_link + '/%s-%s' % (mtitle, year)
			return url
		except:
			source_utils.scraper_error('COOLMOVIEZONE')
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			hostDict = hostprDict + hostDict
			r = client.request(url)
			if not r:
				return sources
			match = re.compile('<td align="center"><strong><a href="(.+?)"').findall(r)
			# log_utils.log('match = %s' % match, log_utils.LOGDEBUG)

			for url in match:
				valid, host = source_utils.is_host_valid(url, hostDict)
				if valid:
					quality, info = source_utils.get_release_quality(url, url)
					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
					                'direct': False, 'debridonly': False})
			return sources
		except:
			source_utils.scraper_error('COOLMOVIEZONE')
			return sources


	def resolve(self, url):
		return url