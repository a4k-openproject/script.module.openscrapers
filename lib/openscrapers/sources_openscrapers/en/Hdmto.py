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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 31
		self.language = ['en']
		self.domains = ['hdm.to']
		self.base_link = 'https://hdm.to'
		self.search_link = '/search/%s+%s'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			t = cleantitle.geturl(title).replace('-', '+').replace('++', '+')
			self.title = t
			url = self.base_link + self.search_link % (t, year)
			r = client.request(url)
			u = client.parseDOM(r, "div", attrs={"class": "col-md-2 col-sm-2 mrgb"})
			for i in u:
				link = re.compile('<a href="(.+?)"').findall(i)
				for url in link:
					if not cleantitle.get(title) in cleantitle.get(url):
						continue
					return url
		except:
			source_utils.scraper_error('HDMTO')
			return


	def sources(self, url, hostDict, hostprDict):
		# log_utils.log('url = %s' % url, __name__, log_utils.LOGDEBUG)
		sources = []
		try:
			hostDict = hostDict + hostprDict

			if url is None:
				return sources

			t = client.request(url)

#site has magnets also
			# t = re.sub(r'\n|\t', '', t)
			# torrents = re.compile(r'Torrent:\s*(.*)</span><div').findall(t)[0]
			# tor_list = re.findall(r'href="(.+?)">(.+?)</a', torrents)
			# name = re.compile('<h2 class="movieTitle">(.+?)</h2>').findall(t)[0]
			# name = re.sub('[^A-Za-z0-9]+', '.', name).lstrip('.')

			# for torrent, qual in tor_list:
				# hash = torrent.split('download/')[1]
				# url = 'magnet:%s' % hash
				# url = 'magnet:?xt=urn:btih:%s&dn=Avengers.Endgame.%s' % (hash, qual)
				# quality, info = source_utils.get_release_quality(name, url)

				# if qual == '3D':
					# quality = '1080p'
				# dsize = 0

				# info = ' | '.join(info)

				# sources.append({'source': 'torrent', 'seeders': 1, 'hash': hash, 'name': name + '.' + quality, 'quality': quality,
											# 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})

			r = re.compile('<iframe.+?src="(.+?)"').findall(t)

			for url in r:
				url = url.replace(" ", "+")
				if 'youtube' in url:
					continue
				url = url.split('//1o.to/')[1]
				url = 'https://hls.1o.to/vod/%s/playlist.m3u8' % url
				sources.append({'source': 'direct', 'quality': '720p', 'info': '', 'language': 'en', 'url': url, 'direct': True,
				                'debridonly': False})
			return sources
		except:
			source_utils.scraper_error('HDMTO')
			return sources


	def resolve(self, url):
		return url