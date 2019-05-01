# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 12-03-2018 by JewBMX in Scrubs.

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import base64
import re

from openscrapers.modules import cleantitle, cfscrape


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['0123putlocker.com']
		self.base_link = 'http://0123putlocker.com'
		self.search_link = '/search-movies/%s.html'
		self.scraper = cfscrape.create_scraper()


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle)
			url = url.replace('-','+')
			return url
		except:
			return
 
 
	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url: return
			query = url + '+season+' + season
			find = query.replace('+','-')
			url = self.base_link + self.search_link % query
			r = self.scraper.get(url).content
			match = re.compile('<a href="http://0123putlocker.com/watch/(.+?)-' + find + '.html"').findall(r)
			for url_id in match:
				url = 'http://0123putlocker.com/watch/' + url_id + '-' + find + '.html'
				r = self.scraper.get(url).content
				match = re.compile('<a class="episode episode_series_link" href="(.+?)">' + episode + '</a>').findall(r)
				for url in match:
					return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			r = self.scraper.get(url).content
			try:
				match = re.compile('<p class="server_version"><img src="http://0123putlocker.com/themes/movies/img/icon/server/(.+?).png" width="16" height="16" /> <a href="(.+?)">').findall(r)
				for host, url in match: 
					if host == 'internet': pass
					else: sources.append({'source': host,'quality': 'SD','language': 'en','url': url,'direct': False,'debridonly': False}) 
			except:
				return
		except Exception:
			return
		return sources


	def resolve(self, url):
		r = self.scraper.get(url).content
		match = re.compile('decode\("(.+?)"').findall(r)
		for info in match:
			info = base64.b64decode(info)
			match = re.compile('src="(.+?)"').findall(info)
			for url in match:
				return url

