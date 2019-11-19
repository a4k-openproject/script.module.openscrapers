# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.
# Created by Tempest

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

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['streamdreams.org']
		self.base_link = 'https://streamdreams.org'
		self.search_movie = '/movies/bbb-%s/'
		self.search_tv = '/shows/bbb-%s/'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			mvtitle = cleantitle.geturl(title)
			url = self.base_link + self.search_movie % mvtitle
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			tvtitle = cleantitle.geturl(tvshowtitle)
			url = self.base_link + self.search_tv % tvtitle
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			url = url + '?session=%s&episode=%s' % (season, episode)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			if url is None:
				return sources
			sources = []
			hostDict = hostprDict + hostDict
			headers = {'Referer': url}
			r = self.scraper.get(url, headers=headers).content
			u = client.parseDOM(r, "span", attrs={"class": "movie_version_link"})
			for t in u:
				match = client.parseDOM(t, 'a', ret='data-href')
				for url in match:
					if url in str(sources):
						continue
					valid, host = source_utils.is_host_valid(url, hostDict)
					if valid:
						quality, info = source_utils.get_release_quality(url, url)
						if source_utils.limit_hosts() is True and host in str(sources):
							continue
						sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url,
						                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
