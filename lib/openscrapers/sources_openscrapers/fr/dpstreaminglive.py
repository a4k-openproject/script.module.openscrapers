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

try: from urlparse import parse_qs, urlparse
except ImportError: from urllib.parse import parse_qs, urlparse
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['fr']
		self.domains = ['dpstreaming.live']
		self.base_link = 'https://dpstreaming.live/'
		self.key_link = '?'
		self.moviesearch_link = 's=%s'
		self.tvsearch_link = 's=%s'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urlencode(url)
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
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

	def sources(self, url, hostDict, hostprDict):
		try:
			print '-------------------------------    -------------------------------'
			sources = []
			print url
			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			season = data['season'] if 'season' in data else False
			episode = data['episode'] if 'episode' in data else False
			print season, episode
			if season and episode:
				print 'TV'
				self.search_link = 'query=%s&submit=Submit+Query'
				aTitle = data['tvshowtitle']
			else:
				self.search_link = 'query=%s&submit=Submit+Query'
				aTitle = data['title']
			post = self.search_link % (quote_plus(cleantitle.query(aTitle)))
			url = 'https://dpstreaming.live/recherche/'
			t = cleantitle.get(aTitle)
			r = client.request(url, XHR=True, referer=url, post=post)
			r = client.parseDOM(r, 'div', attrs={'class': 'film-k kutu-icerik kat'})
			if season and episode:
				t = t + 'saison0' + season
			r = client.parseDOM(r, 'div', attrs={'class': 'play fa fa-play-circle'})
			r = sorted(set(r))
			r = [(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title')) for i in r]
			r = [(i[0][0], i[1][0].lower()) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
			r = [i[0] for i in r if t == cleantitle.get(i[1])][0]
			# r = sorted(set(r))
			url0 = '%s%s' % ('https://dpstreaming.live', r)
			print url0
			url = client.replaceHTMLCodes(url0)
			url = url0.encode('utf-8')
			r = client.request(url, XHR=True, referer=url)
			r = re.sub('(\n|\t)', '', r)
			langue = re.compile('<b class=\"fa fa-cc\"></b><span>(.+?)</span>', re.MULTILINE | re.DOTALL).findall(r)[0]
			if langue == 'VF':
				langue = 'FR'
			quality2 = re.compile('<div class=\"kalite\">(.+?)</div>', re.MULTILINE | re.DOTALL).findall(r)[0]
			quality2 = re.sub('-', '', quality2)
			if season and episode:
				unLien0a = client.parseDOM(r, 'div', attrs={'class': 'dizi-bolumleri'})[0]
				r = re.compile('Saison\s+0%s\s+\-\s+Episode\s+0%s(.+?)class=\"dropit-trigger\">' % (season, episode),
				               re.MULTILINE | re.DOTALL).findall(unLien0a)[0]
				unLien0b = client.parseDOM(r, 'li', ret='id')
			else:
				r = client.parseDOM(r, 'div', attrs={'class': 'dizi-bolumleri film'})
				unLien0b = client.parseDOM(r, 'span', ret='id')
			counter = 0
			for unLienUrl in unLien0b:
				if 'gf-' in unLienUrl:
					continue
				dataUrl = urlencode({'pid': unLienUrl[1:]})
				dataUrl = client.request(url0, post=dataUrl, XHR=True, referer=url0)
				try:
					url = client.parseDOM(dataUrl, 'iframe', ret='src')[1]
				except:
					url = client.parseDOM(dataUrl, 'iframe', ret='src')[0]
				if url.startswith('//'):
					url = url.replace('//', '', 1)
				host = re.findall('([\w]+[.][\w]+)$', urlparse(url.strip().lower()).netloc)[0]
				if not host in hostDict: continue
				host = client.replaceHTMLCodes(host)
				host = host.encode('utf-8')
				url = url.encode('utf-8')
				if '1080p' in quality2:
					quality = '1080p'
				elif '720p' in quality2 or 'bdrip' in quality2 or 'hdrip' in quality2:
					quality = '720p'
				else:
					quality = 'SD'
				if 'dvdscr' in quality2 or 'r5' in quality2 or 'r6' in quality2:
					quality2 = 'SCR'
				elif 'camrip' in quality2 or 'tsrip' in quality2 or 'hdcam' in quality2 or 'hdts' in quality2 or 'dvdcam' in quality2 or 'dvdts' in quality2 or 'cam' in quality2 or 'telesync' in quality2 or 'ts' in quality2:
					quality2 = 'CAM'
				sources.append({'source': host, 'quality': quality, 'language': langue, 'url': url, 'direct': False,
				                'debridonly': False})
			print sources
			return sources
		except:
			return sources

	def resolve(self, url):
		return url
