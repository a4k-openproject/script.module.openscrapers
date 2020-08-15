# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers (updated url 8-03-2020)

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

import base64
import json
import re
import time

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote, unquote_plus
except ImportError: from urllib.parse import urlencode, quote, unquote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['cartoonhd.app', 'cartoonhd.com']
		self.base_link = 'https://cartoonhd.app'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			aliases = json.loads(aliases)
			aliases.append({'country': 'us', 'title': title})
			url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
			url = urlencode(url)
			return url
		except:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			aliases = json.loads(aliases)
			aliases.append({'country': 'us', 'title': tvshowtitle})
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
			url = urlencode(url)
			return url
		except:
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			url = parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urlencode(url)
			return url
		except:
			return


	def searchShow(self, title, season, episode, aliases, headers):
		try:
			for alias in aliases:
				url = '%s/show/%s/season/%01d/episode/%01d' % (self.base_link, cleantitle.geturl(title), int(season), int(episode))
				url = client.request(url, headers=headers, output='geturl', timeout='10')
				if not url is None and url != self.base_link:
					break
			return url
		except:
			source_utils.scraper_error('CARTOONHD')
			return


	def searchMovie(self, title, year, aliases, headers):
		try:
			for alias in aliases:
				url = '%s/film/%s' % (self.base_link, cleantitle.geturl(alias['title']))
				url = client.request(url, headers=headers, output='geturl', timeout='10')
				if not url is None and url != self.base_link:
					break
			if url is None:
				for alias in aliases:
					url = '%s/film/%s-%s' % (self.base_link, cleantitle.geturl(alias['title']), year)
					url = client.request(url, headers=headers, output='geturl', timeout='10')
					if not url is None and url != self.base_link:
						break
			return url
		except:
			source_utils.scraper_error('CARTOONHD')
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			imdb = data['imdb']
			aliases = eval(data['aliases'])
			headers = {}
			if 'tvshowtitle' in data:
				url = self.searchShow(title, int(data['season']), int(data['episode']), aliases, headers)
			else:
				url = self.searchMovie(title, data['year'], aliases, headers)
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)
			r = client.request(url, headers=headers, output='extended', timeout='10')
			if r is None:
				return sources
			if not imdb in r[0]:
				return sources
			cookie = r[4]
			headers = r[3]
			result = r[0]
			try:
				r = re.findall('(https:.*?redirector.*?)[\'\"]', result)
				for i in r:
					sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
			except:
				source_utils.scraper_error('CARTOONHD')
				pass
			try:
				auth = re.findall('__utmx=(.+)', cookie)[0].split(';')[0]
			except:
				auth = 'false'
			auth = 'Bearer %s' % unquote_plus(auth)
			headers['Authorization'] = auth
			headers['Referer'] = url
			u = '/ajax/vsozrflxcw.php'
			self.base_link = client.request(self.base_link, headers=headers, output='geturl')
			u = urljoin(self.base_link, u)
			action = 'getEpisodeEmb' if '/episode/' in url else 'getMovieEmb'
			elid = quote(base64.encodestring(str(int(time.time()))).strip())
			token = re.findall("var\s+tok\s*=\s*'([^']+)", result)[0]
			idEl = re.findall('elid\s*=\s*"([^"]+)', result)[0]
			post = {'action': action, 'idEl': idEl, 'token': token, 'nopop': '', 'elid': elid}
			post = urlencode(post)
			cookie += ';%s=%s' % (idEl, elid)
			headers['Cookie'] = cookie
			r = client.request(u, post=post, headers=headers, cookie=cookie, XHR=True)
			r = str(json.loads(r))
			r = re.findall('\'(http.+?)\'', r) + re.findall('\"(http.+?)\"', r)
			for i in r:
				if 'google' in i:
					quality = 'SD'
					if 'googleapis' in i:
						quality = source_utils.check_url(i)
					elif 'googleusercontent' in i:
						i = directstream.googleproxy(i)
						quality = directstream.googletag(i)[0]['quality']
					sources.append({'source': 'gvideo', 'quality': quality, 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
				elif 'llnwi.net' in i or 'vidcdn.pro' in i:
					quality = source_utils.check_url(i)
					sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
				else:
					valid, hoster = source_utils.is_host_valid(i, hostDict)
					if not valid:
						continue
					sources.append({'source': hoster, 'quality': '720p', 'language': 'en', 'url': i, 'direct': False, 'debridonly': False})
			return sources
		except:
			source_utils.scraper_error('CARTOONHD')
			return sources


	def resolve(self, url):
		if 'google' in url and 'googleapis' not in url:
			return directstream.googlepass(url)
		else:
			return url