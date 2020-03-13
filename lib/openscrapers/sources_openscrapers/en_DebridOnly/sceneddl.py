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
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['sceneddl.me']
		self.base_link = 'http://www.sceneddl.me'
		self.search_link = '/?s=%s'


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

			if r is None and 'tvshowtitle' in data:
				season = re.search('S(.*?)E', hdlr)
				season = season.group(1)
				url = title
				r = client.request(url)

			for loopCount in range(0, 2):
				if loopCount == 1 or (r is None and 'tvshowtitle' in data):
					r = client.request(url)

				# test = zip(re.findall('<h2 class="entry-title"><a href="(.*?)" rel="bookmark">(.*?)<', r, re.DOTALL), re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB|gb|mb))', r, re.DOTALL))
				# log_utils.log('test = %s' % test, log_utils.LOGDEBUG)

				posts = client.parseDOM(r, "h2", attrs={"class": "entry-title"})

				items = []
				for post in posts:
					try:
						name = client.parseDOM(post, "a")[0]
						t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
						if cleantitle.get(t) != cleantitle.get(title):
							continue

						if hdlr not in name:
							continue

						# check year for reboot/remake show issues if year is available-crap shoot
						if 'tvshowtitle' in data:
							if re.search(r'([1-3][0-9]{3})', name):
								if not any(value in name for value in [data['year'], str(int(data['year'])+1), str(int(data['year'])-1)]):
									continue

						if source_utils.remove_lang(name):
							return

						u = client.parseDOM(post, 'a', ret='href')

						for i in u:
							link = str(i)
							items.append(link)
					except:
						source_utils.scraper_error('SCENEDDL')
						pass

				if len(items) > 0:
					break

			for item in items:
				try:
					i = str(item)
					r = client.request(i)

					u = client.parseDOM(r, "div", attrs={"class": "entry-content"})

					for t in u:
						r = client.parseDOM(t, 'a', ret='href')

						for url in r:
							if '.rar' in url or 'imdb.com' in url:
								continue

							if url in str(self.sources):
								return

							quality, info = source_utils.get_release_quality(url)

							try:
								size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB|gb|mb))', t)[0]
								dsize, isize = source_utils._size(size)
								info.insert(0, isize)
							except:
								dsize = 0
								pass

							info = ' | '.join(info)

							valid, host = source_utils.is_host_valid(url, hostDict)
							if valid:
								sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})

				except:
					source_utils.scraper_error('SCENEDDL')
					pass

			return sources

		except:
			source_utils.scraper_error('SCENEDDL')
			return sources


	def resolve(self, url):
		return url


