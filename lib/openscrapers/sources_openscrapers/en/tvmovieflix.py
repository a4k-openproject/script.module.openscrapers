# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.
# really slow since it uses cfscrape.

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

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['tvmovieflix.com']
		self.base_link = 'http://www.tvmovieflix.com'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			mtitle = cleantitle.geturl(title)
			url = self.base_link + '/movie/%s-%s' % (mtitle, year)
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
			url = self.base_link + '/show/%s/season/%s/episode/%s' % (tvshowtitle, season, episode)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			hostDict = hostDict + hostprDict
			r = self.scraper.get(url).content
			match = re.compile(
				'<a href="http://www.tvmovieflix.com/report-.+?/(.+?)" target="_blank"><span class="a">Report Broken</span></a></li>',
				re.DOTALL | re.M).findall(r)
			for link in match:
				if "/show/" in url:
					surl = "http://www.tvmovieflix.com/e/" + link
				else:
					surl = "http://www.tvmovieflix.com/m/" + link
				i = self.scraper.get(surl).content
				match = re.compile('<IFRAME.+?SRC="(.+?)"', re.DOTALL | re.IGNORECASE).findall(i)
				for link in match:
					if "realtalksociety.com" in link:
						r = requests.get(link).content
						match = re.compile('<source src="(.+?)" type="video/mp4">', re.DOTALL | re.IGNORECASE).findall(
							r)
						for url in match:
							valid, host = source_utils.is_host_valid(url, hostDict)
							quality, info = source_utils.get_release_quality(url, url)
							sources.append(
								{'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url,
								 'direct': True, 'debridonly': False})
					else:
						valid, host = source_utils.is_host_valid(link, hostDict)
						quality, info = source_utils.get_release_quality(link, link)
						sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': link,
						                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
