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

try: from urlparse import urljoin
except ImportError: from urllib.parse import urljoin
try: from urllib import quote_plus
except ImportError: from urllib.parse import quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['ko']
		self.domains = ['dramacool.video', 'dramacool9.io']  # Old  dramacool.su
		self.base_link = 'https://www4.dramacool.video'
		self.search_link = '/search?keyword=%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
			if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))
			return self.__get_episode_link(url)
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases))
			if not url and tvshowtitle != localtvshowtitle: url = self.__search(
				[tvshowtitle] + source_utils.aliases_to_array(aliases))
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		return self.__get_episode_link(url, episode)

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			url = urljoin(self.base_link, url)
			r = client.request(url)
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'watch_video'})
			r = [i.attrs['data-src'] for i in dom_parser.parse_dom(r, 'iframe', req='data-src')]
			for i in r:
				try:
					if 'k-vid' in i:
						i = client.request(i, referer=url)
						i = dom_parser.parse_dom(i, 'div', attrs={'class': 'videocontent'})
						gvid = dom_parser.parse_dom(i, 'source', req='src')
						gvid = [(g.attrs['src'], g.attrs['label'] if 'label' in g.attrs else 'SD') for g in gvid]
						gvid = [(x[0], source_utils.label_to_quality(x[1])) for x in gvid if x[0] != 'auto']
						for u, q in gvid:
							try:
								tag = directstream.googletag(u)
								if tag:
									sources.append(
										{'source': 'gvideo', 'quality': tag[0].get('quality', 'SD'), 'language': 'ko',
										 'url': u, 'direct': True, 'debridonly': False})
								else:
									sources.append(
										{'source': 'CDN', 'quality': q, 'language': 'ko', 'url': u, 'direct': True,
										 'debridonly': False})
							except:
								pass
						i = dom_parser.parse_dom(i, 'iframe', attrs={'id': 'embedvideo'}, req='src')[0].attrs['src']
					valid, host = source_utils.is_host_valid(i, hostDict)
					if not valid: continue
					sources.append({'source': host, 'quality': 'SD', 'language': 'ko', 'url': i, 'direct': False,
					                'debridonly': False})
				except:
					pass
			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __search(self, titles):
		try:
			query = self.search_link % quote_plus(cleantitle.query(titles[0]))
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i]
			r = client.request(query, XHR=True)
			r = json.loads(r)
			r = [(i.get('url'), i.get('name')) for i in r]
			r = [(i[0]) for i in r if cleantitle.get(i[1]) in t][0]
			return source_utils.strip_domain(r)
		except:
			return

	def __get_episode_link(self, url, episode='1'):
		try:
			if not url:
				return
			url = urljoin(self.base_link, url)
			r = client.request(url)
			r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'all-episode'})
			r = dom_parser.parse_dom(r, 'li')
			r = dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('.*-episode-%s\.\w+.*?' % episode)}, req='href')[
				0].attrs['href']
			return source_utils.strip_domain(r)
		except:
			return
