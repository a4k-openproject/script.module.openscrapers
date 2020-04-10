# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 07-22-2019 by JewBMX in Scrubs.

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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['fr']
		self.domains = ['dadyflix.ws']
		self.base_link = 'https://www.dadyflix.ws'
		self.search_link = '/?s=%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			mtitle = cleantitle.geturl(title).replace('-', '+')
			url = self.base_link + self.search_link % mtitle
			mSearchPage = client.request(url)
			section = client.parseDOM(mSearchPage, "div", attrs={"class": "title"})
			for item in section:
				results = re.compile('<a href="(.+?)">(.+?)</a>.+?<span class="year">(.+?)</span>').findall(item)
				for url, mName, mYear in results:
					if cleantitle.get(title) in cleantitle.get(mName):
						if year in str(mYear):
							return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			self.tvtitle = cleantitle.geturl(tvshowtitle).replace('-', '+')
			url = self.base_link + self.search_link % self.tvtitle
			tvSearchPage = client.request(url)
			results = re.compile('<div class="title".+?href="(.+?)">(.+?)</a>.+?class="year">(.+?)</span>',
			                     re.DOTALL).findall(tvSearchPage)
			for url, tvName, tvYear in results:
				if cleantitle.get(self.tvtitle) in cleantitle.get(tvName):
					if year in str(tvYear):
						return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			pattern = re.compile(r"/series/([\w]+)")
			showName = re.findall(pattern, url)[0]
			tvShowPage = client.request(url)
			finalResults = re.compile('<div class="episodiotitle"><a href="(.+?)">', re.DOTALL).findall(tvShowPage)
			for url in finalResults:
				cURL = self.base_link + '/episode/' + showName + '-saison-' + season + '-episode-' + episode
				if cURL in str(url):
					return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			hostDict = hostDict + hostprDict
			sources = []

			if url is None:
				return sources

			t = client.request(url)
			r = re.compile('data-src-player="(.+?)"').findall(t)

			for url in r:
				valid, host = source_utils.is_host_valid(url, hostDict)
				if valid:

					# if source_utils.limit_hosts() is True and host in str(sources): # function does not exist
						# continue

					quality, info = source_utils.get_release_quality(url, url)

					sources.append({'source': host, 'quality': quality, 'language': 'fr', 'url': url, 'info': info,
					                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
