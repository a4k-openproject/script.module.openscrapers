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
from openscrapers.modules import tvmaze


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['ko']
		self.domains = ['dramafire.asia', 'dramacoolfire.com']
		self.base_link = 'http://dramacoolfire.com'
		self.search_link = '/?s=%s&x=0&y=0'

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
			episode = tvmaze.tvMaze().episodeAbsoluteNumber(tvdb, int(season), int(episode))
			url = self.__search([localtvshowtitle] + aliases, year, episode)
			if not url and tvshowtitle != localtvshowtitle:
				url = self.__search([tvshowtitle] + aliases, year, episode)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			if not url:
				return sources
			r = client.request(urljoin(self.base_link, url))
			r = dom_parser.parse_dom(r, 'div', attrs={'id': 'entries'})
			links = re.findall('''(?:link|file)["']?\s*:\s*["'](.+?)["']''', ''.join([i.content for i in r]))
			links += [l.attrs['src'] for i in r for l in dom_parser.parse_dom(i, 'iframe', req='src')]
			links += [l.attrs['src'] for i in r for l in dom_parser.parse_dom(i, 'source', req='src')]
			for i in links:
				try:
					i = re.sub('\[.+?\]|\[/.+?\]', '', i)
					i = client.replaceHTMLCodes(i)
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

	def __search(self, titles, year, episode='0'):
		try:
			title = titles[0]
			if int(episode) > 0: title += ' episode %s' % episode
			t = [cleantitle.get(i) for i in set(titles) if i]
			y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']
			r = client.request(
				urljoin(self.base_link, self.search_link) % quote_plus(cleantitle.query(title)))
			r = dom_parser.parse_dom(r, 'div', attrs={'id': 'entries'})
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'post'})
			r = dom_parser.parse_dom(r, 'h3', attrs={'class': 'title'})
			r = dom_parser.parse_dom(r, 'a', req='href')
			r = [(i.attrs['href'], i.content.lower()) for i in r if i]
			r = [(i[0], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
			r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
			r = [(i[0], i[1], i[2], re.findall('(.+?)\s+(?:episode)\s+(\d+)', i[1])) for i in r]
			r = [(i[0], i[3][0][0] if len(i[3]) > 0 else i[1], i[2], i[3][0][1] if len(i[3]) > 0 else '0') for i in r]
			r = [(i[0], i[1].replace(' hd', ''), i[2], '1' if int(episode) > 0 and i[3] == '0' else i[3]) for i in r]
			r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
			r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y and int(i[3]) == int(episode)][0]
			return source_utils.strip_domain(r)
		except:
			return
