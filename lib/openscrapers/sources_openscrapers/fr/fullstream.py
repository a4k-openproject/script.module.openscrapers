# -*- coding: utf-8 -*-
# covenant

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


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['fr']
		self.domains = ['fs-stream.com', 'full-stream.co', 'full-stream.nu']
		self.base_link = 'http://fs-stream.com'
		self.search_link = 'index.php'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases),
			                                                        year)
			if url: return urlencode({'url': url})
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
			year = data['year']

			url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year, season)
			if not url and tvshowtitle != localtvshowtitle: url = self.__search(
				[tvshowtitle] + source_utils.aliases_to_array(aliases), year, season)

			if url: return urlencode({'url': source_utils.strip_domain(url), 'episode': episode})
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []

		try:
			if not url:
				return sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			url = data['url']
			episode = data.get('episode')

			r = client.request(urljoin(self.base_link, url))

			if episode:
				rel = dom_parser.parse_dom(r, 'a',
				                           attrs={'class': 'fstab', 'title': re.compile('Episode %s$' % episode)},
				                           req='data-rel')
				rel = [dom_parser.parse_dom(r, 'div', attrs={'id': i.attrs['data-rel']}) for i in rel]
				rel = [i[0].content for i in rel if i]
				r = ' '.join(rel)

			r = dom_parser.parse_dom(r, 'div', attrs={'class': re.compile('s?elink')})
			r = dom_parser.parse_dom(r, 'a', req='href')
			r = [i.attrs['href'] for i in r]

			for h_url in r:
				valid, hoster = source_utils.is_host_valid(h_url, hostDict)
				if not valid: continue

				sources.append({'source': hoster, 'quality': 'SD', 'language': 'fr', 'url': h_url, 'direct': False,
				                'debridonly': False})

			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __search(self, titles, year, season='0'):
		try:
			query = urljoin(self.base_link, self.search_link)

			t = [cleantitle.get(i) for i in set(titles) if i]
			y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

			r = client.request(query, post={'do': 'search', 'subaction': 'search', 'search_start': 0, 'full_search': 0,
			                                'result_from': 1, 'story': cleantitle.query(titles[0])})

			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'fullstream'})
			r = [(dom_parser.parse_dom(i, 'h3', attrs={'class': 'mov-title'}),
			      dom_parser.parse_dom(i, 'div', attrs={'class': 'fullmask'})) for i in r]
			r = [(dom_parser.parse_dom(i[0], 'a', req='href'),
			      dom_parser.parse_dom(i[1], 'a', attrs={'href': re.compile('.*/year/\d+')})) for i in r]
			r = [(i[0][0].attrs['href'], i[0][0].content, i[1][0].content if i[1] else '0') for i in r if i[0]]
			r = [(i[0], i[1], i[2], re.findall('(.+?)\s+(?:\s*-\s*saison)\s+(\d+)', i[1], re.I)) for i in r]
			r = [(i[0], i[3][0][0] if len(i[3]) > 0 else i[1], i[2], i[3][0][1] if len(i[3]) > 0 else '0') for i in r]
			r = [(i[0], i[1], i[2], '1' if int(season) > 0 and i[3] == '0' else i[3]) for i in r]
			r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
			r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y and int(i[3]) == int(season)][0]

			return source_utils.strip_domain(r)
		except:
			return
