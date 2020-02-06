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

from openscrapers.modules import cleantitle
from openscrapers.modules import dom_parser
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['tvdownload.net']
		self.base_link = 'http://tvdownload.net/'
		self.search_link = '/?s=%s'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			query = cleantitle.geturl(title).replace('-','+') + '+' + year
			url2 = urlparse.urljoin(self.base_link, self.search_link % query)
			url = {'imdb': imdb, 'title': title, 'year': year, 'url': url2, 'content': 'movie'}
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
			if url is None: return
			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			tvshowtitle = data['tvshowtitle']
			year = data['year']

			query = '%s+s%02de%02d' % (cleantitle.geturl(tvshowtitle).replace('-','+'), int(season),int(episode))
			url2 = urlparse.urljoin(self.base_link, self.search_link % (query))
			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url = {'imdb': imdb, 'title': title, 'year': year, 'url': url2, 'content': 'episdoe', 'tvshowtitle': tvshowtitle, 'season': season, 'episode': episode, 'premiered': premiered}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		sources = []

		try:
			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			hostDict = hostprDict + hostDict

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			ref_url = url = data['url']
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/72.0'}
			r = client.request(url, headers=_headers)
			posts = client.parseDOM(r, 'h2', attrs={'class': 'title'})
			posts = zip(client.parseDOM(posts, 'a', ret='title'), client.parseDOM(posts, 'a', ret='href'))

			if posts == []:
				return sources

			for item in posts:
				try:
					name = item[0].replace(' ', '.')
					url = item[1]
					r = client.request(url, headers=_headers)
					list = client.parseDOM(r, 'div', attrs={'id': 'content'})

					if 'tvshowtitle' in data:
						regex = '(<strong>(.*?)</strong><br />\s?[A-Z,0-9]*?\s\|\s([A-Z,0-9,\s]*)\|\s((\d+\.\d+|\d*)\s?(?:GB|GiB|Gb|MB|MiB|Mb))?</p>(?:\s<p><a href=\".*?\" .*?_blank\">.*?</a></p>)+)'
					else:
						regex = '(<strong>Release Name:</strong>\s*(.*?)<br />\s?<strong>Size:</strong>\s?((\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+)\s(?:GB|GiB|Gb|MB|MiB|Mb))?<br />(.*\s)*)'

					for match in re.finditer(regex, list[0].encode('ascii', errors='ignore').decode('ascii', errors='ignore').replace('&nbsp;', ' ')):
						name = str(match.group(2))
						t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and')
						if cleantitle.get(t) != cleantitle.get(title):
							continue

						if hdlr not in name:
							continue

						if source_utils.remove_lang(name):
							continue

						# audio = str(match.group(3))

						if 'tvshowtitle' in data:
							size = str(match.group(4))
						else:
							size = str(match.group(3))

						links = client.parseDOM(match.group(1), 'a', attrs={'class': 'autohyperlink'}, ret='href')

						for url in links:
							try:
								if any(x in url for x in ['.rar', '.zip', '.iso', '.sample.']):
									continue

								if url in str(sources):
									continue

								valid, host = source_utils.is_host_valid(url, hostDict)
								if not valid:
									continue

								host = client.replaceHTMLCodes(host)
								host = host.encode('utf-8')

								quality, info = source_utils.get_release_quality(name, url)

								try:
									div = 1 if size.endswith(('GB', 'GiB', 'Gb')) else 1024
									size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
									size = '%.2f GB' % size
									info.insert(0, size)
								except:
									pass

								info = ' | '.join(info)

								sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True})
							except:
								source_utils.scraper_error('TVDOWNLOADS')
								pass
				except:
					source_utils.scraper_error('TVDOWNLOADS')
					pass

			return sources

		except:
			source_utils.scraper_error('TVDOWNLOADS')
			return sources


	def resolve(self, url):
		return url
