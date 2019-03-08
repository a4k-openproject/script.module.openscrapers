# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    openloadmovie scraper for Exodus forks.
    Nov 9 2018 - Checked
    Oct 10 2018 - Cleaned and Checked

    Updated and refactored by someone.
    Originally created by others.
'''
import re

from openscrapers.modules import cleantitle
from openscrapers.modules import client


# openloadmovie.ws opens to openloadmovie.org always.
# could remove it but o well it can go down first.

class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['openloadmovie.org','openloadmovie.ws']
		self.base_link = 'https://openloadmovie.org'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title)
			url = self.base_link + '/movies/%s-%s' % (title,year)
			return url
		except:
			return
			
	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			r = client.request(url)
			match = re.compile('<iframe class="metaframe rptss" src="(.+?)"').findall(r)
			for url in match: 
				sources.append({'source': 'Openload','quality': 'HD','language': 'en','url': url,'direct': False,'debridonly': False})
		except Exception:
			return
		return sources

	def resolve(self, url):
		return url
