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

try: from urlparse import urlparse, urljoin
except ImportError: from urllib.parse import urlparse, urljoin
try: from urllib import quote_plus
except ImportError: from urllib.parse import quote_plus

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.domains = ['iload.to']
		self.base_link = 'https://iload.to'
		self.search_link_mv = '/suche/%s/Filme'
		self.search_link_tv = '/suche/%s/Serien'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search(self.search_link_mv, imdb, [localtitle] + source_utils.aliases_to_array(aliases))
			if not url and title != localtitle: url = self.__search(self.search_link_mv, imdb,
			                                                        [title] + source_utils.aliases_to_array(aliases))
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = self.__search(self.search_link_tv, imdb, [localtvshowtitle] + source_utils.aliases_to_array(aliases))
			if not url and tvshowtitle != localtvshowtitle: url = self.__search(self.search_link_tv, imdb, [
				tvshowtitle] + source_utils.aliases_to_array(aliases))
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			query = urljoin(self.base_link, url)
			r = self.scraper.get(query).content
			r = dom_parser.parse_dom(r, 'td', attrs={'data-title-name': re.compile('Season %02d' % int(season))})
			r = dom_parser.parse_dom(r, 'a', req='href')[0].attrs['href']
			r = self.scraper.get(urljoin(self.base_link, r)).content
			r = dom_parser.parse_dom(r, 'td', attrs={'data-title-name': re.compile('Episode %02d' % int(episode))})
			r = dom_parser.parse_dom(r, 'a', req='href')[0].attrs['href']
			return source_utils.strip_domain(r)
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			query = urljoin(self.base_link, url)
			r = self.scraper.get(query).content
			r = dom_parser.parse_dom(r, 'div', attrs={'id': 'Module'})
			r = [(r, dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('[^\'"]*xrel_search_query[^\'"]*')},
			                              req='href'))]
			r = [(i[0], i[1][0].attrs['href'] if i[1] else '') for i in r]
			rels = dom_parser.parse_dom(r[0][0], 'a', attrs={'href': re.compile('[^\'"]*ReleaseList[^\'"]*')},
			                            req='href')
			if rels and len(rels) > 1:
				r = []
				for rel in rels:
					relData = self.scraper.get(urljoin(self.base_link, rel.attrs['href'])).content
					relData = dom_parser.parse_dom(relData, 'table', attrs={'class': 'release-list'})
					relData = dom_parser.parse_dom(relData, 'tr', attrs={'class': 'row'})
					relData = [(dom_parser.parse_dom(i, 'td', attrs={'class': re.compile('[^\'"]*list-name[^\'"]*')}),
					            dom_parser.parse_dom(i, 'img', attrs={'class': 'countryflag'}, req='alt'),
					            dom_parser.parse_dom(i, 'td', attrs={'class': 'release-types'})) for i in relData]
					relData = [(i[0][0].content, i[1][0].attrs['alt'].lower(), i[2][0].content) for i in relData if
					           i[0] and i[1] and i[2]]
					relData = [(i[0], i[2]) for i in relData if i[1] == 'deutsch']
					relData = [(i[0], dom_parser.parse_dom(i[1], 'img', attrs={'class': 'release-type-stream'})) for i
					           in relData]
					relData = [i[0] for i in relData if i[1]]
					# relData = dom_parser.parse_dom(relData, 'a', req='href')[:3]
					relData = dom_parser.parse_dom(relData, 'a', req='href')
					for i in relData:
						i = self.scraper.get(urljoin(self.base_link, i.attrs['href'])).content
						i = dom_parser.parse_dom(i, 'div', attrs={'id': 'Module'})
						i = [(i, dom_parser.parse_dom(i, 'a',
						                              attrs={'href': re.compile('[^\'"]*xrel_search_query[^\'"]*')},
						                              req='href'))]
						r += [(x[0], x[1][0].attrs['href'] if x[1] else '') for x in i]
			r = [(dom_parser.parse_dom(i[0], 'div', attrs={'id': 'ModuleReleaseDownloads'}), i[1]) for i in r]
			r = [(dom_parser.parse_dom(i[0][0], 'a', attrs={'class': re.compile('.*-stream.*')}, req='href'), i[1]) for
			     i in r if len(i[0]) > 0]
			for items, rel in r:
				rel = urlparse(rel).query
				rel = urlparse.parse_qs(rel)['xrel_search_query'][0]
				quality, info = source_utils.get_release_quality(rel)
				items = [(i.attrs['href'], i.content) for i in items]
				items = [(i[0], dom_parser.parse_dom(i[1], 'img', req='src')) for i in items]
				items = [(i[0], i[1][0].attrs['src']) for i in items if i[1]]
				items = [(i[0], re.findall('.+/(.+\.\w+)\.\w+', i[1])) for i in items]
				items = [(i[0], i[1][0]) for i in items if i[1]]
				info = ' | '.join(info)
				for link, hoster in items:
					valid, hoster = source_utils.is_host_valid(hoster, hostDict)
					if not valid: continue
					sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': link, 'info': info,
					                'direct': False, 'debridonly': False, 'checkquality': True})
			return sources
		except:
			return sources

	def resolve(self, url):
		try:
			url = self.scraper.get(urljoin(self.base_link, url), output='geturl').content
			return url if self.base_link not in url else None
		except:
			return

	def __search(self, search_link, imdb, titles):
		try:
			query = search_link % (quote_plus(cleantitle.query(titles[0])))
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i]
			r = self.scraper.get(query).content
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'big-list'})
			r = dom_parser.parse_dom(r, 'table', attrs={'class': 'row'})
			r = dom_parser.parse_dom(r, 'td', attrs={'class': 'list-name'})
			r = dom_parser.parse_dom(r, 'a', req='href')
			r = [i.attrs['href'] for i in r if i and cleantitle.get(i.content) in t][0]
			url = source_utils.strip_domain(r)
			r = self.scraper.get(urljoin(self.base_link, url)).content
			r = dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('.*/tt\d+.*')}, req='href')
			r = [re.findall('.+?(tt\d+).*?', i.attrs['href']) for i in r]
			r = [i[0] for i in r if i]
			return url if imdb in r else None
		except:
			return
