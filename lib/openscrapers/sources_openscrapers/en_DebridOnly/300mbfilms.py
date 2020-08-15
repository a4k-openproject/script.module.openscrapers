# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers

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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 29
		self.language = ['en']
		self.domains = ['300mbfilms.io', '300mbfilms.co']
		self.base_link = 'https://www.300mbfilms.io'
		self.search_link = '/?s=%s'
		# self.search_link = '/search/%s/feed/rss2/'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urlencode(url)
			return url
		except:
			source_utils.scraper_error('300MBFILMS')
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urlencode(url)
			return url
		except:
			source_utils.scraper_error('300MBFILMS')
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
			source_utils.scraper_error('300MBFILMS')
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []

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
			url = urljoin(self.base_link, url)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)
			r = client.request(url)
			posts = client.parseDOM(r, 'h2')

			urls = []
			for item in posts:
				if not item.startswith('<a href'):
					continue

				try:
					name = client.parseDOM(item, "a")[0]
					t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
					if cleantitle.get(t) != cleantitle.get(title):
						continue

					if hdlr not in name:
						continue

					quality, info = source_utils.get_release_quality(name, item[0])

					try:
						size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', item)[0]
						dsize, isize = source_utils._size(size)
						info.insert(0, isize)
					except:
						dsize = 0
						pass

					fileType = source_utils.getFileType(name)
					info.append(fileType)
					info = ' | '.join(info) if fileType else info[0]

					item = client.parseDOM(item, 'a', ret='href')

					url = item

					links = self.links(url)
					if links is None:
						continue

					urls += [(i, quality, info) for i in links]

				except:
					source_utils.scraper_error('300MBFILMS')
					pass

			for item in urls:
				if 'earn-money' in item[0]:
					continue
				if any(x in item[0] for x in ['.rar', '.zip', '.iso']):
					continue
				url = client.replaceHTMLCodes(item[0])
				try:
					url = url.encode('utf-8')
				except:
					pass

				valid, host = source_utils.is_host_valid(url, hostDict)
				if not valid:
					continue

				host = client.replaceHTMLCodes(host)
				try:
					host = host.encode('utf-8')
				except:
					pass

				sources.append({'source': host, 'quality': item[1], 'language': 'en', 'url': url, 'info': item[2], 'direct': False, 'debridonly': True, 'size': dsize})
			return sources

		except:
			source_utils.scraper_error('300MBFILMS')
			return sources


	def links(self, url):
		urls = []
		try:
			if url is None:
				return

			for url in url:
				r = client.request(url)
				r = client.parseDOM(r, 'div', attrs={'class': 'entry'})
				r = client.parseDOM(r, 'a', ret='href')

				if 'money' not in str(r):
					continue

				r1 = [i for i in r if 'money' in i][0]
				r = client.request(r1)
				r = client.parseDOM(r, 'div', attrs={'id': 'post-\d+'})[0]

				if 'enter the password' in r:
					plink= client.parseDOM(r, 'form', ret='action')[0]
					post = {'post_password': '300mbfilms', 'Submit': 'Submit'}
					send_post = client.request(plink, post=post, output='cookie')
					link = client.request(r1, cookie=send_post)
				else:
					link = client.request(r1)
				if '<strong>Single' not in link:
					continue

				link = re.findall('<strong>Single(.+?)</tr', link, re.DOTALL)[0]
				link = client.parseDOM(link, 'a', ret='href')
				link = [(i.split('=')[-1]) for i in link]

				for i in link:
					urls.append(i)

				return urls
		except:
			source_utils.scraper_error('300MBFILMS')
			pass


	def resolve(self, url):
		return url