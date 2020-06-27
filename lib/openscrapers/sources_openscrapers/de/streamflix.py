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

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.domains = ['scr.cr', 'streamflix.org']
		self.base_link = 'https://scr.cr'
		self.search_link = '/api/searchAutoComplete?locale=de&q=%s'
		self.get_links = '/api/getLinks'
		self.get_episodes = '/api/getEpisode'
		self.out_link = '/de/out/%s/%s'
		# Old and removed  streamflix.to

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			id = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
			if not id and title != localtitle: id = self.__search([title] + source_utils.aliases_to_array(aliases))
			return urlencode({'id': id}) if id else None
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			id = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases))
			if not id and tvshowtitle != localtvshowtitle: id = self.__search(
				[tvshowtitle] + source_utils.aliases_to_array(aliases))
			return urlencode({'id': id}) if id else None
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
			id = data.get('id')
			season = data.get('season')
			episode = data.get('episode')
			if season and episode:
				r = client.request(urljoin(self.base_link, self.get_episodes),
				                   post={'series_id': id, 'mlang': 'de', 'season': season, 'episode': episode})
				r = json.loads(r).get('episode_links', [])
				r = [([i.get('id')], i.get('hostername')) for i in r]
			else:
				data.update({'lang': 'de'})
				r = client.request(urljoin(self.base_link, self.get_links), post=data)
				r = json.loads(r).get('links', [])
				r = [(i.get('ids'), i.get('hoster')) for i in r]
			for link_ids, hoster in r:
				valid, host = source_utils.is_host_valid(hoster, hostDict)
				if not valid: continue
				for link_id in link_ids:
					sources.append(
						{'source': host, 'quality': 'SD', 'language': 'de', 'url': self.out_link % (link_id, hoster),
						 'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		try:
			url = urljoin(self.base_link, url)
			if self.base_link in url:
				url = client.request(url, output='geturl')
			return url
		except:
			return url

	def __search(self, titles):
		try:
			query = self.search_link % quote_plus(cleantitle.query(titles[0]))
			query = urljoin(self.base_link, query)
			t = [cleantitle.get(i) for i in set(titles) if i]
			r = client.request(query)
			r = json.loads(r)
			r = [(i.get('id'), i.get('value')) for i in r]
			r = [i[0] for i in r if cleantitle.get(i[1]) in t][0]
			return r
		except:
			return
