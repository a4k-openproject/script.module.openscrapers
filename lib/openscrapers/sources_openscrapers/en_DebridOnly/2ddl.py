# -*- coding: utf-8 -*-

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


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['twoddl.net', '2ddl.vg']
		self.base_link = 'https://2ddl.vg'
		self.search_link = '/?s=%s'
		self.scraper = cfscrape.create_scraper()


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
			if url is None:
				return
			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urllib.urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []

			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			hostDict = hostprDict + hostDict

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = self.search_link % urllib.quote_plus(query)
			url = urlparse.urljoin(self.base_link, url).replace('-', '+')
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			r = client.request(url)
			# r = self.scraper.get(url).content

			if r is None and 'tvshowtitle' in data:
				season = re.search('S(.*?)E', hdlr)
				season = season.group(1)
				url = title
				# r = self.scraper.get(url).content
				r = client.request(url)


			for loopCount in range(0,2):
				if loopCount == 1 or (r is None and 'tvshowtitle' in data):
					r = self.scraper.get(url).content
					# r = client.request(url)
				posts = client.parseDOM(r, "div", attrs={"class": "postpage_movie_download"})

				items = []
				for post in posts:
					try:
						u = client.parseDOM(post, 'a', ret='href')

						for i in u:
							name = str(i)
							items.append(name)
					except:
						pass
				if len(items) > 0:
					break

			for item in items:
				try:
					i = str(item)
					# r = self.scraper.get(i).content
					r = client.request(i)
					if r is None:
						continue

					tit = client.parseDOM(r, 'meta', attrs={'property': 'og:title'}, ret='content')[0]
					t = tit.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
					if cleantitle.get(t) != cleantitle.get(title):
						continue

					if hdlr not in tit:
						continue

					u = client.parseDOM(r, "div", attrs={"class": "multilink_lnks"})

					for t in u:

						r = client.parseDOM(t, 'a', ret='href')

						for url in r:
							if 'www.share-online.biz' in url:
								continue

							if url in str(sources):
								continue

							quality, info = source_utils.get_release_quality(url, url)

							valid, host = source_utils.is_host_valid(url, hostDict)

							if valid:
								sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True})
				except:
					source_utils.scraper_error('2DDL')
					pass

			return sources

		except:
			source_utils.scraper_error('2DDL')
			return sources


	def resolve(self, url):
		return url
