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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.domains = ['movie2k.ag']
		self.base_link = 'https://www.movie2k.ag/'
		self.search_link = '?c=movie&m=filter&keyword=%s'
		self.get_link = 'http://www.vodlocker.to/embed/movieStreams?lang=2&e=&id=%s&links=%s&cat=movie'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
			if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			query = urljoin(self.base_link, url)
			r = client.request(query)
			r = dom_parser.parse_dom(r, 'div', attrs={'id': 'player'})
			r = dom_parser.parse_dom(r, 'iframe', req='src')
			r = client.request(r[0][0]['src'])
			r = dom_parser.parse_dom(r, 'a', attrs={'class': 'play_container'}, req='href')
			r = client.request(r[0][0]['href'])
			url = self.get_link % (
			re.search('(?<=var id = \")(.*?)(?=\")', r).group(), re.search('(?<=var links = \")(.*?)(?=\")', r).group())
			r = client.request(url)
			r = dom_parser.parse_dom(r, 'ul', attrs={'id': 'articleList'})
			r = dom_parser.parse_dom(r, 'a')
			for i in r:
				if 'http' in i[0]['href']:
					link = i[0]['href']
				elif 'http' in i[0]['onclick']:
					link = re.search('http(.*?)(?=\")', i[0]['onclick']).group()
				else:
					return sources
				valid, hoster = source_utils.is_host_valid(link, hostDict)
				if not valid: continue
				sources.append({'source': hoster, 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False,
				                'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __search(self, titles):
		try:
			query = self.search_link % (quote_plus(cleantitle.query(titles[0])))
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i]
			r = client.request(query)
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'nag'})
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'item-video'})
			r = dom_parser.parse_dom(r, 'h2', attrs={'class': 'entry-title'})
			r = dom_parser.parse_dom(r, 'a', req='href')
			for i in r:
				title = i[1]
				if re.search('\*(?:.*?)\*', title) is not None:
					title = re.sub('\*(?:.*?)\*', '', title)
				title = cleantitle.get(title)
				if title in t:
					return source_utils.strip_domain(i[0]['href'])
				else:
					return
		except:
			return
