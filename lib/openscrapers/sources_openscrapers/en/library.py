# -*- coding: UTF-8 -*-
#  (updated 4-20-2020)

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

try: from urlparse import parse_qs
except ImportError: from urllib.parse import parse_qs
try: from urllib import urlencode
except ImportError: from urllib.parse import urlencode


from openscrapers.modules import control
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 35
		self.language = ['en', 'de', 'fr', 'ko', 'pl', 'pt', 'ru']
		self.domains = []


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			return urlencode({'imdb': imdb, 'title': title, 'localtitle': localtitle,'year': year})
		except:
			source_utils.scraper_error('library')
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			return urlencode({'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle, 'year': year})
		except:
			source_utils.scraper_error('library')
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			url = parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url.update({'premiered': premiered, 'season': season, 'episode': episode})
			return urlencode(url)
		except:
			source_utils.scraper_error('library')
			return


	def sources(self, url, hostDict, hostprDict):
		sources = []

		try:
			if url is None:
				return sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			content_type = 'episode' if 'tvshowtitle' in data else 'movie'

			years = (data['year'], str(int(data['year'])+1), str(int(data['year'])-1))

			if content_type == 'movie':
				title = cleantitle.get_simple(data['title']).lower()
				localtitle = cleantitle.get_simple(data['localtitle']).lower()
				ids = [data['imdb']]

				r = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties": ["imdbnumber", "title", "originaltitle", "file"]}, "id": 1}' % years)
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']['movies']
				r = [i for i in r if str(i['imdbnumber']) in ids or title in [cleantitle.get_simple(i['title']), cleantitle.get_simple(i['originaltitle'])]]
				if not r:
					return sources
				try:
					file = i['file'].encode('utf-8')
				except:
					file = i['file']
				r = [i for i in r if not file.endswith('.strm')]
				if not r:
					return sources
				r = r[0]
				r = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["streamdetails", "file"], "movieid": %s }, "id": 1}' % str(r['movieid']))
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']['moviedetails']
			elif content_type == 'episode':
				title = cleantitle.get_simple(data['tvshowtitle']).lower()
				localtitle = cleantitle.get_simple(data['localtvshowtitle']).lower()
				season, episode = data['season'], data['episode']

				r = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties": ["imdbnumber", "title"]}, "id": 1}' % years)
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']['tvshows']

				r = [i for i in r if title in (cleantitle.get_simple(i['title']).lower() if not ' (' in i['title'] else cleantitle.get_simple(i['title']).split(' (')[0])][0]

				r = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["file"], "tvshowid": %s }, "id": 1}' % (str(season), str(episode), str(r['tvshowid'])))
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']['episodes']
				if not r:
					return sources
				try:
					file = i['file'].encode('utf-8')
				except:
					file = i['file']
				r = [i for i in r if not file.endswith('.strm')][0]

				r = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"properties": ["streamdetails", "file"], "episodeid": %s }, "id": 1}' % str(r['episodeid']))
				r = unicode(r, 'utf-8', errors='ignore')
				r = json.loads(r)['result']['episodedetails']

			try:
				url = r['file'].encode('utf-8')
			except:
				url = r['file']



			try:
				quality = int(r['streamdetails']['video'][0]['width'])
			except:
				source_utils.scraper_error('library')
				quality = -1

			if quality > 1920: quality = '4K'
			if quality >= 1920: quality = '1080p'
			if 1280 <= quality < 1900: quality = '720p'
			if quality < 1280: quality = 'SD'

			info = []
			try:
				f = control.openFile(url) ; s = f.size() ; f.close()
				dsize = float(s)/1024/1024/1024
				isize = '%.2f GB' % dsize
				info.insert(0, isize)
			except:
				source_utils.scraper_error('library')
				dsize = 0
				pass

			try:
				c = r['streamdetails']['video'][0]['codec']
				if c == 'avc1': c = 'h264'
				info.append(c)
			except:
				source_utils.scraper_error('library')
				pass

			try:
				ac = r['streamdetails']['audio'][0]['codec']
				if ac == 'dca': ac = 'dts'
				if ac == 'dtshd_ma': ac = 'dts-hd ma'
				info.append(ac)
			except:
				source_utils.scraper_error('library')
				pass

			try:
				ach = r['streamdetails']['audio'][0]['channels']
				if ach == 1: ach = 'mono'
				if ach == 2: ach = '2.0'
				if ach == 6: ach = '5.1'
				if ach == 8: ach = '7.1'
				info.append(ach)
			except:
				source_utils.scraper_error('library')
				pass

			info = ' | '.join(info)
			try:
				info = info.encode('utf-8')
			except:
				pass

			sources.append({'source': 'local', 'quality': quality, 'language': 'en', 'url': url,
							'info': info, 'local': True, 'direct': True, 'debridonly': False, 'size': dsize})
			return sources
		except:
			source_utils.scraper_error('library')
			return sources


	def resolve(self, url):
		return url