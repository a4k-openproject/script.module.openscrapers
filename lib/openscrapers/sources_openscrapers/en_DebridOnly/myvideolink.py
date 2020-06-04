# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers (updated 5-16-2020)

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
		self.priority = 22
		self.language = ['en']
		self.domains = ['go.myvideolinks.net', 'sag.myvideolinks.net', 'looka.myvideolinks.net', 'kita.myvideolinks.net', 'myvideolinks.69.mu', 'nothingcan.undo.it']
		self.base_link = 'http://myvideolinks.69.mu'
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
			test = client.request(self.base_link)
			new_search = client.parseDOM(test, 'form', ret='action')[0] # to try to combat their constant search link changes

			sources = []

			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			# url = urlparse.urljoin(self.base_link, self.search_link)
			url = urlparse.urljoin(new_search, self.search_link)
			url = url % urllib.quote_plus(query)
			# log_utils.log('url = %s' % url, __name__, log_utils.LOGDEBUG)
			r = client.request(url, timeout='5')
			if not r:
				return sources
			if 'Nothing Found' in r:
				return sources

			r = client.parseDOM(r, 'article')
			r1 = client.parseDOM(r, 'h2')
			# r2 = client.parseDOM(r, 'div', attrs={'class': 'entry-excerpt'})

			if 'tvshowtitle' in data: # fuckers removed file size for episodes
				posts = zip(client.parseDOM(r1, 'a', ret='href'), client.parseDOM(r1, 'a')) # keep for now case they bring size back
			else:
				posts = zip(client.parseDOM(r1, 'a', ret='href'), client.parseDOM(r1, 'a'))

			hostDict = hostprDict + hostDict
			items = []
			for post in posts:
				try:
					base_u = client.request(post[0], timeout='5')
					if 'tvshowtitle' in data:
						regex = '<h4>(' + title + '.+?)</h4>'
						lists = zip(re.findall(regex, base_u), re.findall('<ul>(.+?)</ul>', base_u, re.DOTALL))
						for links in lists:
							u = re.findall('\'(http.+?)\'', links[1]) + re.findall('\"(http.+?)\"', links[1])
							t = links[0].replace('HDTV', '')
							s = 0
							items += [(t, i, s) for i in u]
					else:
						byline = client.parseDOM(base_u, 'div', attrs={'class': 'entry-byline cf'})
						if 'TV SHOWS' in str(byline):
							continue
						list = client.parseDOM(base_u, 'div', attrs={'class': 'entry-content cf'})
						u = client.parseDOM(list, 'ul')[0]
						u = re.findall('\'(http.+?)\'', u) + re.findall('\"(http.+?)\"', u)
						u = [i for i in u if '/embed/' not in i]
						u = [i for i in u if 'youtube' not in i]
						try:
							t = post[1].encode('utf-8')
						except:
							t = post[1]
						s = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', list[0])[0]
						items += [(t, i, s) for i in u]
				except:
					source_utils.scraper_error('MYVIDEOLINK')
					pass

			for item in items:
				try:
					url = item[1]
					url = client.replaceHTMLCodes(url)
					url = url.encode('utf-8')
					if url.endswith(('.rar', '.zip', '.iso', '.part', '.png', '.jpg', '.bmp', '.gif')):
						continue

					valid, host = source_utils.is_host_valid(url, hostDict)
					if not valid:
						continue

					host = client.replaceHTMLCodes(host)
					host = host.encode('utf-8')

					name = item[0]
					name = client.replaceHTMLCodes(name).replace(' ', '.')
					match = source_utils.check_title(title.replace('!', ''), name, hdlr, data['year'])
					if not match:
						continue

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = item[2]
						dsize, isize = source_utils._size(size)
						if isize:
							info.insert(0, isize)
					except:
						dsize = 0
						pass

					fileType = source_utils.getFileType(name)
					info.append(fileType)
					info = ' | '.join(info) if fileType else info[0]

					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
												'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
				except:
					source_utils.scraper_error('MYVIDEOLINK')
					pass
			return sources
		except:
			source_utils.scraper_error('MYVIDEOLINK')
			return sources


	def resolve(self, url):
		return url