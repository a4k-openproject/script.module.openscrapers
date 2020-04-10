# -*- coding: utf-8 -*-
# created by Venom for Openscrapers (4/3/20)-slow server response time

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


from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['best-moviez.ws']
		self.base_link = 'http://www.best-moviez.ws'
		self.search_link = '/?s=%s&submit=Search'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url == None: return
			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urllib.urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		self.sources = []
		try:
			self.scraper = cfscrape.create_scraper()
			# scraper = cfscrape.create_scraper(debug=True) # throws globasl dump error (import issue)

			if url == None:
				return self.sources

			if debrid.status() is False:
				return self.sources

			self.hostDict = hostprDict + hostDict

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			self.title = self.title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
			self.year = data['year']

			query = '%s %s' % (self.title, self.hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			urls = []
			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url)
			urls.append(url)
			# urls.append(url.replace('/?s', '/page/2/?s')) # server is to slow to parse more than one page
			# log_utils.log('urls = %s' % urls, log_utils.LOGDEBUG)

			links = []
			for x in urls:
				r = self.scraper.get(x).content
				list = client.parseDOM(r, "h1", attrs={'class': 'entry-title'})
				for item in list:
					links.append(item)

			threads = []
			for link in links:
				threads.append(workers.Thread(self.get_sources, link))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('BESTMOVIEZ')
			return self.sources


	def get_sources(self, link):
		try:
			item = client.parseDOM(link, "a", ret="href")[0]
			name = client.parseDOM(link, "a")[0]
			t = name.split(self.hdlr)[0].replace(self.year, '').replace('(', '').replace(')', '').replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
			if cleantitle.get(t) != cleantitle.get(self.title):
				return

			if self.hdlr not in name:
				return

			r = self.scraper.get(item).content
			links = client.parseDOM(r, "div", attrs={'class': 'entry-content'})
			links = client.parseDOM(links, "a", ret="href")
			meta = client.parseDOM(r, "meta", ret="content", attrs={'property': 'og:description'})[0]

			for url in links:
				if 'imdb.com' in url:
					continue

				if any(x in url for x in ['.rar', '.zip', '.iso', '.sample', '.html', '.jpg']):
					continue

				quality, info = source_utils.get_release_quality(name, url)

				try:
					size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', meta)[0]
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except:
					dsize = 0
					pass

				info = ' | '.join(info)

				valid, host = source_utils.is_host_valid(url, self.hostDict)
				if not valid:
					continue

				host = client.replaceHTMLCodes(host)
				host = host.encode('utf-8')

				self.sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
								'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
		except:
			source_utils.scraper_error('BESTMOVIEZ')


	def resolve(self, url):
		return url