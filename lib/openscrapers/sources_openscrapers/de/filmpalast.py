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

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.domains = ['filmpalast.to']
		self.base_link = 'http://filmpalast.to'
		self.search_link = '/search/title/%s'
		self.stream_link = 'stream/%s/1'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
			if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle,
			       'aliases': aliases, 'year': year}
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
			title = data['localtvshowtitle']
			title += ' S%02dE%02d' % (int(season), int(episode))
			aliases = source_utils.aliases_to_array(eval(data['aliases']))
			aliases = [i + ' S%02dE%02d' % (int(season), int(episode)) for i in aliases]
			url = self.__search([title] + aliases)
			if not url and data['tvshowtitle'] != data['localtvshowtitle']:
				title = data['tvshowtitle']
				title += ' S%02dE%02d' % (int(season), int(episode))
				url = self.__search([title] + aliases)
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
			quality = dom_parser.parse_dom(r, 'span', attrs={'id': 'release_text'})[0].content.split('&nbsp;')[0]
			quality, info = source_utils.get_release_quality(quality)
			r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'currentStreamLinks'})
			r = [(dom_parser.parse_dom(i, 'p', attrs={'class': 'hostName'}),
			      dom_parser.parse_dom(i, 'a', attrs={'class': 'stream-src'}, req='data-id')) for i in r]
			r = [(re.sub(' hd$', '', i[0][0].content.lower()), [x.attrs['data-id'] for x in i[1]]) for i in r if
			     i[0] and i[1]]
			for hoster, id in r:
				valid, hoster = source_utils.is_host_valid(hoster, hostDict)
				if not valid: continue
				sources.append({'source': hoster, 'quality': quality, 'language': 'de',
				                'info': ' | '.join(info + ['' if len(id) == 1 else 'multi-part']), 'url': id,
				                'direct': False, 'debridonly': False, 'checkquality': True})
			return sources
		except:
			return sources

	def resolve(self, url):
		try:
			h_url = []
			for id in url:
				query = urljoin(self.base_link, self.stream_link % id)
				r = self.scraper.get(query, XHR=True, post=urlencode({'streamID': id})).content
				r = json.loads(r)
				if 'error' in r and r['error'] == '0' and 'url' in r:
					h_url.append(r['url'])
			h_url = h_url[0] if len(h_url) == 1 else 'stack://' + ' , '.join(h_url)
			return h_url
		except:
			return

	def __search(self, titles):
		try:
			query = self.search_link % (quote_plus(titles[0]))
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i]
			r = self.scraper.get(query).content
			r = dom_parser.parse_dom(r, 'article')
			r = dom_parser.parse_dom(r, 'a', attrs={'class': 'rb'}, req='href')
			r = [(i.attrs['href'], i.content) for i in r]
			r = [i[0] for i in r if cleantitle.get(i[1]) in t][0]
			return source_utils.strip_domain(r)
		except:
			return
