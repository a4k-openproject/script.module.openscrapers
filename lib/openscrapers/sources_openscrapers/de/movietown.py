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

try: from urlparse import urljoin
except ImportError: from urllib.parse import urljoin
try: from urllib import quote_plus
except ImportError: from urllib.parse import quote_plus

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.domains = ['movietown.org']
		self.base_link = 'https://movietown.org'
		self.search_link = '/search?q=%s'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases),
			                                                        year)
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and tvshowtitle != localtvshowtitle: url = self.__search(
				[tvshowtitle] + source_utils.aliases_to_array(aliases), year)
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			s = '/seasons/%s/episodes/%s' % (season, episode)
			url = url.rstrip('/')
			url = url + s
			url = urljoin(self.base_link, url)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			query = urljoin(self.base_link, url)
			r = self.scraper.get(query).content
			r = dom_parser.parse_dom(r, 'div', attrs={'id': 'ko-bind'})
			r = dom_parser.parse_dom(r, 'table', attrs={'class': 'links-table'})
			r = dom_parser.parse_dom(r, 'tbody')
			r = dom_parser.parse_dom(r, 'tr')
			for i in r:
				if re.search('(?<=<td>)(HD)(?=</td>)', i[1]):
					quality = '720p'
				else:
					quality = 'SD'
				x = dom_parser.parse_dom(i, 'td', attrs={'class': 'name'}, req='data-bind')
				hoster = re.search("(?<=>).*$", x[0][1])
				hoster = hoster.group().lower()
				url = re.search("http(.*?)(?=')", x[0][0]['data-bind'])
				url = url.group()
				valid, hoster = source_utils.is_host_valid(hoster, hostDict)
				if not valid: continue
				sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': url, 'direct': False,
				                'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __search(self, titles, year):
		try:
			query = self.search_link % (quote_plus(cleantitle.query(titles[0] + ' ' + year)))
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i]
			r = self.scraper.get(query).content
			r = dom_parser.parse_dom(r, 'figure', attrs={'class': 'pretty-figure'})
			r = dom_parser.parse_dom(r, 'figcaption')
			for i in r:
				title = client.replaceHTMLCodes(i[0]['title'])
				title = cleantitle.get(title)
				if title in t:
					x = dom_parser.parse_dom(i, 'a', req='href')
					return source_utils.strip_domain(x[0][0]['href'])
			return
		except:
			return
