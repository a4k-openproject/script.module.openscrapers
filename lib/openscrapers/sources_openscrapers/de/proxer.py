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

import json
import re

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from openscrapers.modules import anilist
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils
from openscrapers.modules import tvmaze


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.genre_filter = ['animation', 'anime']
		self.domains = ['proxer.me']
		self.base_link = 'http://proxer.me'
		self.search_link = '/search?s=search&name=%s&sprache=alle&typ=%s&format=raw'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			alt_title = anilist.getAlternativTitle(title)
			aliases = source_utils.aliases_to_array(aliases)
			url = self.__search([alt_title] + aliases, year, 'movie')
			if not url and localtitle != alt_title: url = self.__search([localtitle] + aliases, year, 'movie')
			if not url and title != localtitle: url = self.__search([title] + aliases, year, 'movie')
			return urlencode({'url': url, 'episode': '1'}) if url else None
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			alt_title = anilist.getAlternativTitle(tvshowtitle)
			aliases = source_utils.aliases_to_array(aliases)
			url = self.__search([alt_title] + aliases, year, 'animeseries')
			if not url and localtvshowtitle != alt_title: url = self.__search([localtvshowtitle] + aliases, year,
			                                                                  'animeseries')
			if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + aliases, year,
			                                                                    'animeseries')
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			return urlencode(
				{'url': url, 'episode': tvmaze.tvMaze().episodeAbsoluteNumber(tvdb, int(season), int(episode))})
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			for item_id, episode, content_type in self.__get_episode(data.get('url'), data.get('episode')):
				stream_link = urljoin(self.base_link, '/watch/%s/%s/%s' % (item_id, episode, content_type))
				info = 'subbed' if content_type.endswith('sub') else ''
				r = client.request(stream_link)
				r = dom_parser.parse_dom(r, 'script')
				r = ' '.join([i.content for i in r if i.content])
				r = json.loads(re.findall('var\s*streams\s*=\s*(\[.*?\])\s*;', r)[0])
				r = [(i.get('replace'), i.get('code')) for i in r]
				r = [(i[0].replace('#', i[1])) for i in r if i[0] and i[1]]
				for stream_link in r:
					if stream_link.startswith('/'): stream_link = 'http:%s' % stream_link
					if self.domains[0] in stream_link:
						stream_link = client.request(stream_link,
						                             cookie=urlencode({'proxerstream_player': 'flash'}))
						i = [(match[0], match[1]) for match in re.findall(
							'''["']?\s*file\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)(?:[^}>\]]+)["']?\s*width\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)''',
							stream_link, re.DOTALL)]
						i = [(x[0].replace('\/', '/'), source_utils.label_to_quality(x[1])) for x in i]
						for url, quality in i:
							sources.append(
								{'source': 'cdn', 'quality': quality, 'language': 'de', 'url': url, 'info': info,
								 'direct': True, 'debridonly': False})
					else:
						valid, host = source_utils.is_host_valid(stream_link, hostDict)
						if not valid: continue
						sources.append(
							{'source': host, 'quality': 'SD', 'language': 'de', 'url': stream_link, 'info': info,
							 'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __get_episode(self, url, episode='1'):
		try:
			if not url:
				return []
			item_id = re.findall('info/(\d+)', url)[0]
			url = urljoin(self.base_link, '/info/%s/list?format=json' % item_id)
			r = client.request(url)
			r = json.loads(r).get('data', [])
			return [(item_id, episode, i.get('typ')) for i in r if
			        int(i.get('no', '0')) == int(episode) and 'ger' in i.get('typ')]
		except:
			return []

	def __search(self, titles, year, content_type):
		try:
			query = self.search_link % (quote_plus(cleantitle.query(titles[0])), content_type)
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i]
			y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']
			r = client.request(query)
			r = dom_parser.parse_dom(r, 'div', attrs={'id': 'search'})
			r = dom_parser.parse_dom(r, 'table')
			r = dom_parser.parse_dom(r, 'tr', attrs={'class': re.compile('entry\d+')})
			r = [(dom_parser.parse_dom(i, 'a'), dom_parser.parse_dom(i, 'img', attrs={'class': 'flag', 'alt': 'de'}))
			     for i in r]
			r = [i[0] for i in r if i[0] and i[1]]
			r = [(i[0].attrs['href'], i[0].content) for i in r]
			r = [(i[0], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
			r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
			r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
			r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]
			return source_utils.strip_domain(r)
		except:
			return
