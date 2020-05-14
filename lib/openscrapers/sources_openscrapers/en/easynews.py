# -*- coding: UTF-8 -*-

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

import sys
import re
import json
import base64

import requests

try:
	from urllib import quote # Python 2
except ImportError:
	from urllib.parse import quote # Python 3

from openscrapers.modules import control
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils

SORT = {'s1': 'relevance', 's1d': '-', 's2': 'dsize', 's2d': '-', 's3': 'dtime', 's3d': '-'}
SEARCH_PARAMS = {'st': 'adv', 'sb': 1, 'fex': 'mkv, mp4, avi, mpg, wemb', 'fty[]': 'VIDEO', 'spamf': 1, 'u': '1', 'gx': 1, 'pno': 1, 'sS': 3}
SEARCH_PARAMS.update(SORT)


class source:
	def __init__(self):
		self.priority = 35
		self.language = ['en']
		self.domain = 'easynews.com'
		self.base_link = 'https://members.easynews.com'
		self.search_link = '/2.0/search/solr-search/advanced'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = tvshowtitle
			return url
		except:
			pass

	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			url = {'tvshowtitle': url, 'season': season, 'episode': episode}
			return url
		except:
			pass

	def sources(self, url, hostDict, hostprDict):
		
		auth = self._get_auth()

		if not auth:
			return
		
		sources = []
		
		query = self._query(url)
		
		url, params = self._translate_search(query)
		headers = {'Authorization': auth}
		response = requests.get(url, params=params, headers=headers).text
		results = json.loads(response)
		
		down_url = results.get('downURL')
		dl_farm = results.get('dlFarm')
		dl_port = results.get('dlPort')
		files = results.get('data', [])
		
		for item in files:

			try:

				post_hash, post_title, ext, duration = item['0'], item['10'], item['11'], item['14']
				
				checks = [False] * 5
				if 'alangs' in item and item['alangs'] and 'eng' not in item['alangs']: checks[1] = True
				if re.match('^\d+s', duration) or re.match('^[0-5]m', duration): checks[2] = True
				if 'passwd' in item and item['passwd']: checks[3] = True
				if 'virus' in item and item['virus']: checks[4] = True
				if 'type' in item and item['type'].upper() != 'VIDEO': checks[5] = True
				
				if any(checks):
					continue
				
				stream_url = down_url + quote('/%s/%s/%s%s/%s%s' % (dl_farm, dl_port, post_hash, ext, post_title, ext))
				file_name = post_title
				file_dl = stream_url + '|Authorization=%s' % (quote(auth))
				size = float(int(item['rawSize']))/1073741824
				
				quality = source_utils.get_release_quality(file_name)[0]
				info = source_utils.getFileType(file_name)
				info = '%.2f GB | %s | %s' % (size, info, file_name.replace('.', ' ').upper())
				
				sources.append({'source': 'direct',
								'quality': quality,
								'language': "en",
								'url': file_dl,
								'info': info,
								'direct': True,
								'debridonly': False})

			except:
				print("Unexpected error in Easynews Script: source", sys.exc_info()[0])
				exc_type, exc_obj, exc_tb = sys.exc_info()
				print(exc_type, exc_tb.tb_lineno)
				pass
		
		return sources

	def resolve(self, url):
		return url

	def _get_auth(self):

		auth = None
		
		username = control.setting('easynews.user')
		password = control.setting('easynews.password')
		
		if username == '' or password == '':
			return auth
		
		try:

			# Python 2
			user_info = '%s:%s' % (username, password)
			auth = 'Basic ' + base64.b64encode(user_info)
		
		except:

			# Python 3
			user_info = '%s:%s' % (username, password)
			user_info = user_info.encode('utf-8')
			auth = 'Basic ' + base64.b64encode(user_info).decode('utf-8')
		
		return auth

	def _query(self, url):

		content_type = 'episode' if 'tvshowtitle' in url else 'movie'
		
		if content_type == 'movie':
			title = cleantitle.normalize(url.get('title'))
			year = int(url.get('year'))
			years = '%s,%s,%s' % (str(year - 1), year, str(year + 1))
			query = '"%s" %s' % (title, years)
		
		else:
			title = cleantitle.normalize(url.get('tvshowtitle'))
			season = int(url.get('season'))
			episode = int(url.get('episode'))
			query = '%s S%02dE%02d' % (title,  season, episode)
		
		return query

	def _translate_search(self, query):
		
		params = SEARCH_PARAMS
		params['pby'] = 100
		params['safeO'] = 1
		params['gps'] = params['sbj'] = query
		url = self.base_link + self.search_link
		
		return url, params


