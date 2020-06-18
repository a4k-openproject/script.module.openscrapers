# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.
# vidnode could be improved but resolve redirect works for now.
# modified by Venom (added cfscrape 4-3-2020)

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.


from openscrapers.modules import cleantitle
from openscrapers.modules import getSum
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 39
		self.language = ['en']
		self.domains = ['yesmovieshd.to']
		self.base_link = 'https://yesmovieshd.to'
		self.movie_link = '/film/%s/watching.html?ep=0'
		self.tvshow_link = '/film/%s-season-%s/watching.html?ep=%s'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title).replace('--', '-')
			url = self.base_link + self.movie_link % title
			return url
		except:
			source_utils.scraper_error('YESMOVIESGG')
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = cleantitle.geturl(tvshowtitle).replace('--', '-')
			return url
		except:
			source_utils.scraper_error('YESMOVIESGG')
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if not url:
				return
			tvshowtitle = url
			url = self.base_link + self.tvshow_link % (tvshowtitle, season, episode)
			return url
		except:
			source_utils.scraper_error('YESMOVIESGG')
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			hostDict = hostprDict + hostDict
			r = getSum.get(url,Type='cfscrape')
			qual = getSum.findThat(r, 'class="quality">(.+?)<')[0]
			quality, info = source_utils.get_release_quality(qual, qual)
			match = getSum.findSum(r)
			for url in match:
				if 'vidcloud' in url:
					r = getSum.get(url, Type='cfscrape')
					match = getSum.findSum(r)
					for url in match:
						valid, host = source_utils.is_host_valid(url, hostDict)
						if valid:
							sources.append(
								{'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url,
								 'direct': False, 'debridonly': False})
				else:
					valid, host = source_utils.is_host_valid(url, hostDict)
					if valid:
						sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url,
						                'direct': False, 'debridonly': False})
			return sources
		except:
			source_utils.scraper_error('YESMOVIESGG')
			return sources


	def resolve(self, url):
		if 'api.vidnode.net' in url:
			url = getSum.get(url, Type='redirect')
		return url