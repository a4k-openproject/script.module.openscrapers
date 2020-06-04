# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers (updated 5-18-20)

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
import urllib
import urlparse

from openscrapers.modules import cfscrape, client
from openscrapers.modules import cleantitle
from openscrapers.modules import debrid
from openscrapers.modules import source_utils, log_utils


class source:
	def __init__(self):
		self.priority = 26
		self.language = ['en']
		self.domains = ['soapgate.online', 'fmovies.tw', 'ganool.ws']
		self.base_link = 'https://soapgate.online'
		self.search_link = '/search/?q=%s'


	# soapgate(formerly ganool) now does tvshows, re-write
# https://soapgate.online/search/?q=SEAL+Team+-+Season+1
#Episode1  https://soapgate.online/tvseries/seal-team--season-1-hdClNWYK/watch.html
#Episode2  https://soapgate.online/tvseries/seal-team--season-1-hdClNWYK/watch.html?server=2



	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		scraper = cfscrape.create_scraper()
		sources = []
		try:
			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			q = '%s' % cleantitle.get_gan_url(data['title'])
			url = self.base_link + self.search_link % q
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			r = scraper.get(url).content
			v = re.compile('<a href="(.+?)" class="ml-mask jt" title="View(.+?)">\s+<span class=".+?">(.+?)</span>').findall(r)
			# log_utils.log('v = %s' % v, log_utils.LOGDEBUG)
			t = '%s (%s)' % (data['title'], data['year'])

			for url, name, qual in v:
				if t not in name:
					continue
				item = client.request(url)
				item = client.parseDOM(item, 'div', attrs={'class': 'mvici-left'})[0]
				details = re.compile('<strong>Movie Source.*\s*.*/Person">(.*)</').findall(item)[0]
				# log_utils.log('details = %s' % details, log_utils.LOGDEBUG)

				name = re.sub('[^A-Za-z0-9]+', '.', name).lstrip('.')
				# log_utils.log('name = %s' % name, log_utils.LOGDEBUG)
				if source_utils.remove_lang(name):
					continue

				key = url.split('-hd')[1]
				r = scraper.get('https://soapgate.online/moviedownload.php?q=' + key).content
				r = re.compile('<a rel=".+?" href="(.+?)" target=".+?">').findall(r)

				for url in r:
					if any(x in url for x in ['.rar', '.zip', '.iso']):
						continue

					quality, info = source_utils.get_release_quality(qual)

					try:
						size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', item)[0]
						dsize, isize = source_utils._size(size)
						info.insert(0, isize)
					except:
						dsize = 0
						pass

					fileType = source_utils.getFileType(details)
					info.append(fileType)
					info = ' | '.join(info) if fileType else info[0]

					# log_utils.log('info = %s' % info, log_utils.LOGDEBUG)

					valid, host = source_utils.is_host_valid(url, hostDict)
					if not valid:
						continue

					sources.append({'source': host, 'quality': quality, 'info': info, 'language': 'en', 'url': url, 'direct': False,
										'debridonly': True, 'size': dsize})
			return sources
		except:
			source_utils.scraper_error('GANOOL')
			return sources

	def resolve(self, url):
		return url