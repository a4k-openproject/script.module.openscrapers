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

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils
from openscrapers.modules import tvmaze


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.genre_filter = ['animation', 'anime']
		self.domains = ['anime-base.net']
		self.base_link = 'http://anime-base.net'
		self.search_link = '/suche_ajax.php'
		self.scraper = cfscrape.create_scraper()

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = None
			for title in [tvshowtitle, localtvshowtitle,
			              tvmaze.tvMaze().showLookup('thetvdb', tvdb).get('name')] + source_utils.aliases_to_array(
					aliases):
				if url: break
				url = self.__search(title)
			return urlencode({'url': url}) if url else None
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			episode = tvmaze.tvMaze().episodeAbsoluteNumber(tvdb, int(season), int(episode))
			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			data.update({'episode': episode})
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
			episode = int(data.get('episode', 1))
			r = self.scraper.get(urljoin(self.base_link, url)).content
			r = {'': dom_parser.parse_dom(r, 'div', attrs={'id': 'gerdub'}),
			     'subbed': dom_parser.parse_dom(r, 'div', attrs={'id': 'gersub'})}
			for info, data in r.iteritems():
				data = dom_parser.parse_dom(data, 'tr')
				data = [dom_parser.parse_dom(i, 'a', req='href') for i in data if
				        dom_parser.parse_dom(i, 'a', attrs={'id': str(episode)})]
				data = [(link.attrs['href'], dom_parser.parse_dom(link.content, 'img', req='src')) for i in data for
				        link in i]
				data = [(i[0], i[1][0].attrs['src']) for i in data if i[1]]
				data = [(i[0], re.findall('/(\w+)\.\w+', i[1])) for i in data]
				data = [(i[0], i[1][0]) for i in data if i[1]]
				for link, hoster in data:
					valid, hoster = source_utils.is_host_valid(hoster, hostDict)
					if not valid: continue
					sources.append({'source': hoster, 'quality': 'SD', 'language': 'de', 'url': link, 'info': info,
					                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		try:
			if not url.startswith('http'): url = urljoin(self.base_link, url)
			if self.base_link in url:
				r = self.scraper.get(url).content
				r = dom_parser.parse_dom(r, 'meta', req='content')[0]
				r = r.attrs['content']
				r = re.findall('''url\s*=\s*([^'"]+)''', r, re.I)
				if r:
					url = r[0]
			return url
		except:
			return

	def __search(self, title):
		try:
			t = cleantitle.get(title)
			r = self.scraper.get(urljoin(self.base_link, self.search_link),
			                     post={'suchbegriff': title}).content
			r = dom_parser.parse_dom(r, 'a', attrs={'class': 'ausgabe_1'}, req='href')
			r = [(i.attrs['href'], i.content) for i in r]
			r = [i[0] for i in r if cleantitle.get(i[1]) == t][0]
			return source_utils.strip_domain(r)
		except:
			return
