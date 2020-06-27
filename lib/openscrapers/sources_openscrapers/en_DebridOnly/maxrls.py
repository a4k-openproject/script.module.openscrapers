# -*- coding: UTF-8 -*-
# modified by Venom for Openscrapers  (added cfscrape 4-3-2020)

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

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 28
		self.language = ['en']
		self.domains = ['max-rls.com']
		self.base_link = 'http://max-rls.com'
		self.search_link = '/?s=%s&submit=Find'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urlencode(url)
			return url
		except:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urlencode(url)
			return url
		except:
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			url = parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			self.scraper = cfscrape.create_scraper(delay=5)

			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			hostDict = hostprDict + hostDict

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = self.search_link % quote_plus(query)
			url = urljoin(self.base_link, url).replace('%3A+', '+')
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			r = self.scraper.get(url).content

			if r is None and 'tvshowtitle' in data:
				season = re.search('S(.*?)E', hdlr)
				season = season.group(1)
				url = title
				r = self.scraper.get(url).content

			for loopCount in range(0, 2):
				if loopCount == 1 or (r is None and 'tvshowtitle' in data):
					r = self.scraper.get(url).content
				posts = client.parseDOM(r, "h2", attrs={"class": "postTitle"})

				items = []
				for post in posts:
					try:
						u = client.parseDOM(post, 'a', ret='href')

						for i in u:
							link = str(i)
							name = link.rsplit('/', 1)[0]
							name = name.rsplit('/', 1)[1].upper()
							if source_utils.remove_lang(name):
								return

							t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
							if cleantitle.get(t) != cleantitle.get(title):
								break

							if hdlr not in name:
								break

							# check year for reboot/remake show issues if year is available-crap shoot
							# if 'tvshowtitle' in data:
								# if re.search(r'([1-3][0-9]{3})', name):
									# if not any(value in name for value in [data['year'], str(int(data['year'])+1), str(int(data['year'])-1)]):
										# break
							items.append(link)

					except:
						source_utils.scraper_error('MAXRLS')
						pass
				if len(items) > 0:
					break

			for item in items:
				try:
					i = str(item)
					r = self.scraper.get(url).content
					u = client.parseDOM(r, "div", attrs={"class": "postContent"})

					for t in u:
						links = zip(re.findall('Download: (.*?)</strong>', t, re.DOTALL), re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB|gb|mb))', t, re.DOTALL))

						for link in links:
							urls = link[0]
							results = re.compile('href="(.+?)"', re.DOTALL).findall(urls)

							for url in results:
								if url in str(self.sources):
									return

								quality, info = source_utils.get_release_quality(url)

								try:
									dsize, isize = source_utils._size(link[1])
									info.insert(0, isize)
								except:
									dsize = 0
									pass

								info = ' | '.join(info)

								valid, host = source_utils.is_host_valid(url, hostDict)
								if not valid:
									continue

								sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})

				except:
					source_utils.scraper_error('MAXRLS')
					pass

			return sources

		except:
			source_utils.scraper_error('MAXRLS')
			return sources


	def resolve(self, url):
		return url