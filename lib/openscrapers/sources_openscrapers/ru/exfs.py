# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 11-23-2018 by JewBMX in Scrubs.
# Only browser checks for active domains.

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
try: from urllib import urlencode
except ImportError: from urllib.parse import urlencode

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils
from openscrapers.sources_openscrapers.ru.lib import moonwalk


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['ru']
		self.domains = ['ex-fs.net']
		self.base_link = 'http://ex-fs.net'
		self.search_link = '/engine/ajax/search.php'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and title != localtitle:
				url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
			return urlencode({'url': url}) if url else None
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and tvshowtitle != localtvshowtitle:
				url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
			return urlencode({'url': url}) if url else None
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			data.update({'season': season, 'episode': episode})
			return urlencode(data)
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			url = data.get('url')
			season = data.get('season')
			episode = data.get('episode')
			url = urljoin(self.base_link, url)
			r = client.request(url)
			r = dom_parser.parse_dom(r, 'iframe', req='src')
			r = [i.attrs['src'] for i in r]
			for link in r:
				try:
					urls = []
					if 'moonwalk.cc' in link or 'ex-fs.net' in link:
						host = 'moonwalk';
						direct = True;
						urls = moonwalk.moonwalk(link, url, season, episode)
					for i in urls:
						sources.append(
							{'source': host, 'quality': i['quality'], 'info': i.get('info', ''), 'language': 'ru',
							 'url': i['url'], 'direct': direct, 'debridonly': False})
				except:
					pass
			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __search(self, titles, year):
		try:
			t = [cleantitle.get(i) for i in set(titles) if i]
			y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']
			r = client.request(urljoin(self.base_link, self.search_link), post={'query': titles[0]}, XHR=True)
			r = dom_parser.parse_dom(r, 'a', req='href')
			r = [(i.attrs['href'], i.content.split('<br')[0]) for i in r]
			r = [(i[0], re.sub('<.+?>|</.+?>', '', i[1])) for i in r]
			r = [(i[0], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
			r = [(i[0], i[2][0][0] if i[2] else i[1], i[2][0][1] if i[2] else '0') for i in r]
			r = [(i[0], re.sub(u'\(с \d+ по \d+ сезон\)', '', i[1]), i[2]) for i in r]
			r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
			r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]
			return source_utils.strip_domain(r)
		except:
			return
