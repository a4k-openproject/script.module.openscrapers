# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.

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
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['123movieshubz.com']
		self.base_link = 'http://www5.123movieshubz.com'
		self.search_link = '/watch/%s-%s-online-123movies.html'
		self.scraper = cfscrape.create_scraper()

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			clean_title = cleantitle.geturl(title)
			url = urlparse.urljoin(self.base_link, (self.search_link % (clean_title, year)))
			return url
		except:
			return

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			aliases.append({'country': 'us', 'title': tvshowtitle})
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
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
			clean_title = cleantitle.geturl(url['tvshowtitle']) + '-s%02d' % int(season)
			url = urlparse.urljoin(self.base_link, (self.search_link % (clean_title, url['year'])))
			r = self.scraper.get(url).content
			r = dom_parser.parse_dom(r, 'div', {'id': 'ip_episode'})
			r = [dom_parser.parse_dom(i, 'a', req=['href']) for i in r if i]
			for i in r[0]:
				if i.content == 'Episode %s' % episode:
					url = i.attrs['href']
			return url
		except:
			return

	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			hostDict = hostprDict + hostDict
			if url is None:
				return sources
			r = self.scraper.get(url).content
			qual = re.findall(">(\w+)<\/p", r)
			for i in qual:
				quality, info = source_utils.get_release_quality(i, i)
			r = dom_parser.parse_dom(r, 'div', {'id': 'servers-list'})
			r = [dom_parser.parse_dom(i, 'a', req=['href']) for i in r if i]
			for i in r[0]:
				url = {'url': i.attrs['href'], 'data-film': i.attrs['data-film'], 'data-server': i.attrs['data-server'],
				       'data-name': i.attrs['data-name']}
				url = urllib.urlencode(url)
				valid, host = source_utils.is_host_valid(i.content, hostDict)
				if source_utils.limit_hosts() is True and host in str(sources):
					continue
				if valid:
					sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url,
					                'direct': False, 'debridonly': False})
			return sources
		except:
			return sources

	def resolve(self, url):
		try:
			urldata = urlparse.parse_qs(url)
			urldata = dict((i, urldata[i][0]) for i in urldata)
			post = {'ipplugins': 1, 'ip_film': urldata['data-film'], 'ip_server': urldata['data-server'],
			        'ip_name': urldata['data-name'], 'fix': "0"}
			self.scraper.headers.update({'Referer': urldata['url'], 'X-Requested-With': 'XMLHttpRequest'})
			p1 = self.scraper.post('http://123movieshubz.com/ip.file/swf/plugins/ipplugins.php', data=post).content
			p1 = json.loads(p1)
			p2 = self.scraper.get('http://123movieshubz.com/ip.file/swf/ipplayer/ipplayer.php?u=%s&s=%s&n=0' % (
			p1['s'], urldata['data-server'])).content
			p2 = json.loads(p2)
			p3 = self.scraper.get(
				'http://123movieshubz.com/ip.file/swf/ipplayer/api.php?hash=%s' % (p2['hash'])).content
			p3 = json.loads(p3)
			n = p3['status']
			if n is False:
				p2 = self.scraper.get('http://123movieshubz.com/ip.file/swf/ipplayer/ipplayer.php?u=%s&s=%s&n=1' % (
				p1['s'], urldata['data-server'])).content
				p2 = json.loads(p2)
			url = p2["data"].replace("\/", "/")
			if not url.startswith('http'):
				url = "https:" + url
			return url
		except:
			return
