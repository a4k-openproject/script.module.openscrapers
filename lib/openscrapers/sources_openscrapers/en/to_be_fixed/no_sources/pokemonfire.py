# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 03-17-2019 by JewBMX in Scrubs.

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.genre_filter = ['animation', 'anime']
        self.domains = ['pokemonfire.com']
        self.base_link = 'https://www.pokemonfire.com'
        self.movie_link = '/movies/%s'
        self.tv_link = '/episodes/%s-season-%s-episode-%s/'
        self.scraper = cfscrape.create_scraper(0)

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            ctitle = cleantitle.geturl(title)
            url = self.base_link + self.movie_link % (ctitle)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = cleantitle.geturl(tvshowtitle)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            url = self.base_link + self.tv_link % (url, season, episode)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = self.scraper.get(url).content
            try:
                match = re.compile('<iframe class="metaframe rptss" src="https\://veohb\.net/(.+?)"').findall(r)
                for url in match:
                    url = 'https://veohb.net/' + url
                    info = source_utils.check_url(url)
                    quality = source_utils.check_url(url)
                    sources.append({'source': 'veohb', 'quality': quality, 'language': 'en', 'info': info, 'url': url,
                                    'direct': False, 'debridonly': False})
            except:
                return
        except Exception:
            return
        return sources

    def resolve(self, url):
        r = self.scraper.get(url).content
        match = re.compile('<source src="(.+?)"').findall(r)
        for url in match:
            return url
