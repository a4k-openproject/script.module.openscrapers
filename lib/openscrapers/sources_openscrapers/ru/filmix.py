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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils
from openscrapers.modules import tvmaze


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['ru']
		self.domains = ['filmix.co', 'filmix.me']
		self.base_link = 'https://filmix.co'
		self.search_link = '/engine/ajax/sphinx_search.php'
		self.search_old = '/search/%s'
		self.player_link = '/api/movies/player_data'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and title != localtitle:
				url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
			return urlencode({'url': url}) if url else None
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
			if not url and tvshowtitle != localtvshowtitle:
				url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
			return urlencode({'url': url, 'tvdb': tvdb}) if url else None
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			data.update({'season': season, 'episode': episode})
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
			season = data.get('season')
			episode = data.get('episode')
			abs_episode = 0
			if season and episode:
				abs_episode = str(tvmaze.tvMaze().episodeAbsoluteNumber(data.get('tvdb'), int(season), int(episode)))
			url = urljoin(self.base_link, url)
			r = client.request(url)
			r = r.decode('cp1251').encode('utf-8')
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'players'}, req='data-player')
			r = [(i.attrs['data-player'], dom_parser.parse_dom(i, 'a', req='href')) for i in r]
			r = [(i[0], i[1][0].attrs['href']) for i in r if i[1]]
			for post_id, play_url in r:
				i = client.request(play_url, referer=url, output='extended')
				headers = i[3]
				headers.update({'Cookie': i[2].get('Set-Cookie')})
				i = client.request(urljoin(self.base_link, self.player_link), post={'post_id': post_id},
				                   headers=headers, referer=i, XHR=True)
				i = json.loads(i).get('message', {}).get('translations', {}).get('flash', {})
				for title, link in i.iteritems():
					try:
						link = self.decode_direct_media_url(link)
						if link.endswith('.txt'):
							link = self.decode_direct_media_url(client.request(link))
							link = json.loads(link).get('playlist', [])
							link = [i.get('playlist', []) for i in link]
							link = [x.get('file') for i in link for x in i if
							        (x.get('season') == season and x.get('serieId') == episode) or (
										        x.get('season') == '0' and x.get('serieId') == abs_episode)][0]
						urls = [(source_utils.label_to_quality(q), self.format_direct_link(link, q)) for q in
						        self.get_qualitys(link)]
						urls = [{'quality': x[0], 'url': x[1]} for x in urls if x[0] in ['SD', '720p']]  # filter premium
						for i in urls:
							sources.append({'source': 'CDN', 'quality': i['quality'], 'info': title, 'language': 'ru',
							                'url': i['url'], 'direct': True, 'debridonly': False})
					except:
						pass
			return sources
		except:
			return sources

	def resolve(self, url):
		return url

	def __search(self, titles, year):
		try:
			url = urljoin(self.base_link, self.search_link)
			t = [cleantitle.get(i) for i in set(titles) if i]
			y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']
			post = {'story': titles[0], 'years_ot': str(int(year) - 1), 'years_do': str(int(year) + 1)}
			r = client.request(url, post=post, XHR=True)
			if len(r) < 1000:
				url = urljoin(self.base_link, self.search_old % quote_plus(titles[0]))
				r = client.request(url)
			r = r.decode('cp1251').encode('utf-8')
			r = dom_parser.parse_dom(r, 'article')
			r = dom_parser.parse_dom(r, 'div', attrs={'class': 'full'})
			r = [(dom_parser.parse_dom(i, 'a', attrs={'itemprop': 'url'}, req='href'),
			      dom_parser.parse_dom(i, 'h3', attrs={'class': 'name'}, req='content'),
			      dom_parser.parse_dom(i, 'div', attrs={'class': 'origin-name'}, req='content'),
			      dom_parser.parse_dom(i, 'div', attrs={'class': 'year'})) for i in r]
			r = [(i[0][0].attrs['href'], i[1][0].attrs['content'], i[2][0].attrs['content'],
			      dom_parser.parse_dom(i[3], 'a', attrs={'itemprop': 'copyrightYear'})) for i in r if
			     i[0] and i[1] and i[2]]
			r = [(i[0], i[1], i[2], i[3][0].content) for i in r if i[3]]
			r = [i[0] for i in r if (cleantitle.get(i[1]) in t or cleantitle.get(i[2]) in t) and i[3] in y][0]
			return source_utils.strip_domain(r)
		except:
			return

	# Credits to evgen_dev #
	def decode_direct_media_url(self, encoded_url):
		import base64
		codec_a = (
		"l", "u", "T", "D", "Q", "H", "0", "3", "G", "1", "f", "M", "p", "U", "a", "I", "6", "k", "d", "s", "b", "W",
		"5", "e", "y", "=")
		codec_b = (
		"w", "g", "i", "Z", "c", "R", "z", "v", "x", "n", "N", "2", "8", "J", "X", "t", "9", "V", "7", "4", "B", "m",
		"Y", "o", "L", "h")
		i = 0
		for a in codec_a:
			b = codec_b[i]
			i += 1
			encoded_url = encoded_url.replace(a, '___')
			encoded_url = encoded_url.replace(b, a)
			encoded_url = encoded_url.replace('___', b)
		return base64.b64decode(encoded_url)

	def get_qualitys(self, source_link):
		try:
			avail_quality = re.compile("\[([^\]]+)\]", re.S).findall(source_link)[0]
			return [i for i in avail_quality.split(',') if i]
		except:
			return '0'.split()

	def format_direct_link(self, source_link, q):
		regex = re.compile("\[([^\]]+)\]", re.IGNORECASE)
		return regex.sub(q, source_link)
