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

import json
import sys

import requests

from openscrapers.modules import control
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils

class source:
	def __init__(self):
		self.priority = 35
		self.language = ['en']
		self.domain = 'furk.net/'
		self.base_link = 'https://www.furk.net'
		self.search_link = "/api/plugins/metasearch?api_key=%s&q=%s&cached=yes" \
								"&match=%s&moderated=%s%s&sort=relevance&type=video&offset=0&limit=200"
		self.tfile_link = "/api/file/get?api_key=%s&t_files=1&id=%s"
		self.login_link = "/api/login/login?login=%s&pwd=%s"
		self.files = []

	def get_api(self):

		try:

			user_name = control.setting('furk.user_name')
			user_pass = control.setting('furk.user_pass')
			api_key = control.setting('furk.api')

			if api_key == '':
				if user_name == '' or user_pass == '':
					return

				s = requests.Session()
				link = (self.base_link + self.login_link % (user_name, user_pass))
				p = s.post(link)
				p = json.loads(p.text)

				if p['status'] == 'ok':
					api_key = p['api_key']
					control.setSetting('furk.api', api_key)
				else:
					pass

			return api_key

		except:
			print("Unexpected error in Furk Script: check_api", sys.exc_info()[0])
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(exc_type, exc_tb.tb_lineno)
			pass

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

		api_key = self.get_api()

		if not api_key:
			return

		sources = []

		try:

			content_type = 'episode' if 'tvshowtitle' in url else 'movie'
			match = 'extended'
			moderated = 'no' if content_type == 'episode' else 'yes'
			search_in = ''
		
			if content_type == 'movie':
				title = cleantitle.normalize(url.get('title'))
				year = url.get('year')
				query = '@name+%s+%s+@files+%s+%s' % (title, year, title, year)

			elif content_type == 'episode':
				title = cleantitle.normalize(url.get('tvshowtitle'))
				season = int(url['season'])
				episode = int(url['episode'])
				seasEpList = self._seas_ep_query_list(season, episode)
				query = '@name+%s+@files+%s+|+%s+|+%s+|+%s+|+%s' % (title, seasEpList[0], seasEpList[1], seasEpList[2], seasEpList[3], seasEpList[4])
			

			s = requests.Session()
			link = self.base_link + self.search_link % \
				   (api_key, query, match, moderated, search_in)

			p = s.get(link)
			p = json.loads(p.text)

			if p['status'] != 'ok':
				return

			files = p['files']

			for i in files:
				
				if i['is_ready'] == '1' and i['type'] == 'video':
					
					try:

						source = 'SINGLE'
						if int(i['files_num_video']) > 3:
							source = 'PACK [B](x%02d)[/B]' % int(i['files_num_video'])
						file_name = i['name']
						file_id = i['id']
						file_dl = i['url_dl']
						size = float(i['size']) / 1073741824
						
						if content_type == 'episode':
							url = json.dumps({'content': 'episode', 'file_id': file_id, 'season': season, 'episode': episode})
						else:
							url = json.dumps({'content': 'movie', 'file_id': file_id, 'title': title, 'year': year})

						quality = source_utils.get_release_quality(file_name, file_dl)[0]
						info = source_utils.getFileType(file_name)
						info = '%.2f GB | %s | %s' % (size, info, file_name.replace('.', ' ').upper())
						sources.append({'source': source,
										'quality': quality,
										'language': "en",
										'url': url,
										'info': info,
										'direct': True,
										'debridonly': False})

					except:
						pass

				else:
					continue

			return sources

		except:
			print("Unexpected error in Furk Script: source", sys.exc_info()[0])
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(exc_type, exc_tb.tb_lineno)
			pass

	def resolve(self, url):

		try:
			
			api_key = self.get_api()

			if not api_key:
				return

			url = json.loads(url)

			file_id = url.get('file_id')

			self.content_type = 'movie' if url.get('content') == 'movie' else 'episode'

			if self.content_type == 'episode': self.filtering_list = self._seas_ep_resolve_list(url.get('season'), url.get('episode'))

			link = (self.base_link + self.tfile_link % (api_key, file_id))
			s = requests.Session()
			p = s.get(link)
			p = json.loads(p.text)

			if p['status'] != 'ok' or p['found_files'] != '1':
				return

			files = p['files'][0]
			files = files['t_files']

			for i in files:
				if 'video' not in i['ct']:
					pass
				else:
					self.files.append(i)

			url = self._manage_pack()

			return url

		except:
			print("Unexpected error in Furk Script: resolve", sys.exc_info()[0])
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(exc_type, exc_tb.tb_lineno)
			pass

	def _manage_pack(self):

		for i in self.files:

			if self.content_type == 'movie':
				if 'is_largest' in i:
					url = i['url_dl']

			else:
				name = cleantitle.get_simple(i['name'])
				if 'furk320' not in name.lower() and 'sample' not in name.lower():
					for x in self.filtering_list:
						if x in name.lower():
							url = i['url_dl']
						else:
							pass
		
		return url

	def _seas_ep_query_list(self, season, episode):
		
		return ['s%02de%02d' % (season, episode),
				'%dx%02d' % (season, episode),
				'%02dx%02d' % (season, episode),
				'"season %d episode %d"' % (season, episode),
				'"season %02d episode %02d"' % (season, episode)]
	
	def _seas_ep_resolve_list(self, season, episode):
		
		return ['s%02de%02d' % (season, episode),
				'%dx%02d' % (season, episode),
				'%02dx%02d' % (season, episode),
				'season%depisode%d' % (season, episode),
				'season%02depisode%02d' % (season, episode)]
