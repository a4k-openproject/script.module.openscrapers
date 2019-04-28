# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
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

import re,urllib,urlparse
from openscrapers.modules import cleantitle,client,proxy


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['reddit.com']
		self.base_link = 'https://www.reddit.com/user/nbatman/m/streaming2/search?q=%s&restrict_sr=on'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title)
			title = title.replace('-','+')
			query = '%s+%s' % (title,year)
			url = self.base_link % query
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			r = client.request(url)
			try:
				match = re.compile('class="search-title may-blank" >(.+?)</a>.+?<span class="search-result-icon search-result-icon-external"></span><a href="(.+?)://(.+?)/(.+?)" class="search-link may-blank" >').findall(r)
				for info,http,host,ext in match: 
					if '2160' in info: quality = '4K'
					elif '1080' in info: quality = '1080p'
					elif '720' in info: quality = 'HD'
					elif '480' in info: quality = 'SD'
					else: quality = 'SD'
					url = '%s://%s/%s' % (http,host,ext)
					if 'google' in host: host = 'GDrive'
					if 'Google' in host: host = 'GDrive'
					if 'GOOGLE' in host: host = 'GDrive'
					sources.append({
						'source': host,
						'quality': quality,
						'language': 'en',
						'url': url,
						'info': info,
						'direct': False,
						'debridonly': False
					})
			except:
				return
		except Exception:
			return
		return sources


	def resolve(self, url):
		return url

