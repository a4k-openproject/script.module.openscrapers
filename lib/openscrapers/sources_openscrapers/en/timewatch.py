# -*- coding: UTF-8 -*-
# modified by Venom for Openscrapers (4-3-2020)

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
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['timetowatch.video']
		self.base_link = 'https://www.timetowatch.video'
		self.search_link = '/?s=%s&3mh1='
		self.scraper = cfscrape.create_scraper()


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			search_id = title.lower()
			url = urlparse.urljoin(self.base_link, self.search_link)
			url = url % (search_id.replace(':', '%3A').replace(',', '%2C').replace('&', '%26').replace("'", '%27').replace(' ', '+').replace('...', ' '))
			search_results = self.scraper.get(url).content
			match = re.compile('<div data-movie-id=.+?href="(.+?)".+?oldtitle="(.+?)".+?rel="tag">(.+?)</a></div>', re.DOTALL).findall(search_results)
			for movie_url, movie_title, movie_year in match:
				clean_title = cleantitle.get(title)
				movie_title = movie_title.replace('&#8230', ' ').replace('&#038', ' ').replace('&#8217', ' ').replace('...', ' ')
				clean_movie_title = cleantitle.get(movie_title)
				if clean_movie_title in clean_title:
					if cleantitle.get(year) in cleantitle.get(movie_year):
						return movie_url
			return
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			html = self.scraper.get(url).content
			links = re.compile('id="linkplayer.+?href="(.+?)"', re.DOTALL).findall(html)
			for link in links:
				valid, host = source_utils.is_host_valid(link, hostDict)
				if valid:
					quality, info = source_utils.get_release_quality(link, link)
					sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': link,
					                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources


	def resolve(self, url):
		return url