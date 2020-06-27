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
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.domains = ['view4u.stream']  # old  view4u.co
		self.base_link = 'http://view4u.stream'
		self.search_link = '/search/%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases),
			                                                        year)
			return urlencode({'url': url}) if url else None
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle, 'aliases': aliases, 'year': year}
			url = urlencode(url)
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			tvshowtitle = data['tvshowtitle']
			localtvshowtitle = data['localtvshowtitle']
			aliases = source_utils.aliases_to_array(eval(data['aliases']))
			url = self.__search([localtvshowtitle] + aliases, data['year'], season)
			if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + aliases, data['year'],
			                                                                    season)
			if not url: return
			return urlencode({'url': url, 'episode': episode})
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return
			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			url = urljoin(self.base_link, data.get('url', ''))
			episode = data.get('episode')
			r = client.request(url)
			r = r.replace('\n', ' ')
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'fullstory'})
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'row'})
			if episode:
				r = dom_parser.parse_dom(r, 'select', attrs={'id': 'series'})
				r = dom_parser.parse_dom(r, 'option', req='value')
				r = [(i.attrs['value'], i.content) for i in r]
				r = [(i[0], re.findall('\s+(\d+)\s+episode', i[1], re.IGNORECASE)) for i in r]
				r = [i[0].strip() for i in r if i[1] and episode in i[1]]
			else:
				r = dom_parser.parse_dom(r, 'div', attrs={'class': 'inner'})
				r = dom_parser.parse_dom(r, 'a', req='href')
				r = [i.attrs['href'].strip() for i in r]
			for link in r:
				valid, host = source_utils.is_host_valid(link, hostDict)
				if not valid: continue
				sources.append({'source': host, 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False,
				                'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __search(self, titles, year, season='0'):
		try:
			query = self.search_link % quote_plus(cleantitle.query(titles[0]))
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i]
			y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']
			r = client.request(query)
			r = dom_parser.parse_dom(r, 'article', attrs={'class': 'shortstory'})
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 's_info'})
			r = dom_parser.parse_dom(r, 'h2')
			r = dom_parser.parse_dom(r, 'a', req='href')
			r = [(i.attrs['href'], i.content.lower()) for i in r if i]
			r = [(i[0], re.sub('<.+?>|</.+?>', '', i[1]), re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
			r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
			r = [(i[0], i[1], i[2], re.findall('(.+?)(\d+)\s+(?:staf+el|s)', i[1])) for i in r]
			r = [(i[0], i[3][0][0] if len(i[3]) > 0 else i[1], i[2], i[3][0][1] if len(i[3]) > 0 else '0') for i in r]
			r = [(i[0], i[1], i[2], '1' if int(season) > 0 and i[3] == '0' else i[3]) for i in r]
			r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
			r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y and int(i[3]) == int(season)][0]
			return source_utils.strip_domain(r)
		except:
			return
