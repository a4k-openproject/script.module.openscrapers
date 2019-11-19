# -*- coding: utf-8 -*-

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
import time
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.base_link = 'https://torrentapi.org'  # -just to satisfy scraper_test
		self.tvsearch = 'https://torrentapi.org/pubapi_v2.php?app_id=Torapi&token={0}&mode=search&search_string={1}&{2}'
		self.msearch = 'https://torrentapi.org/pubapi_v2.php?app_id=Torapi&token={0}&mode=search&search_imdb={1}&{2}'
		self.token = 'https://torrentapi.org/pubapi_v2.php?app_id=Torapi&get_token=get_token'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urllib.urlencode(url)
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []

			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			token = client.request(self.token)
			token = json.loads(token)["token"]

			if 'tvshowtitle' in data:
				search_link = self.tvsearch.format(token, urllib.quote_plus(query), 'format=json_extended')
			else:
				search_link = self.msearch.format(token, data['imdb'], 'format=json_extended')
			# log_utils.log('search_link = %s' % search_link, log_utils.LOGDEBUG)

			time.sleep(2)

			rjson = client.request(search_link, error=True)
			if 'No results found' in rjson:
				return sources

			files = json.loads(rjson)['torrent_results']

			for file in files:
				url = file["download"]
				url = url.split('&tr')[0]

				# altered to allow multi-lingual audio tracks
				if any(x in url.lower() for x in ['french', 'italian', 'truefrench', 'dublado', 'dubbed']):
					continue

				name = file["title"]

				# some shows like "Power" have year and hdlr in name
				t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '')
				if cleantitle.get(t) != cleantitle.get(title).replace('&',
				                                                      'and'):  # torrentapi does not seem to use ampersand symbol in titles
					continue

				if hdlr not in name:
					continue

				quality, info = source_utils.get_release_quality(name, name)

				size = source_utils.convert_size(file["size"])
				info.append(size)
				info = ' | '.join(info)

				sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': url,
				                'info': info, 'direct': False, 'debridonly': True})
			return sources

		except:
			source_utils.scraper_error('TORRENTAPI')
			return sources

	def resolve(self, url):
		return url
