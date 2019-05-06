# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 12-07-2018 by JewBMX in Scrubs.

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
        self.domains = ['animetoon.org', 'animetoon.tv']
        self.base_link = 'http://www.animetoon.org'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = '%s %s' % (title, year)
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
            if url is None:
                return
            if str(season) == '1':
                url = '%s/%s-episode-%s' % (self.base_link, url, episode)
            else:
                url = '%s/%s-season-%s-episode-%s' % (self.base_link, url, season, episode)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            r = self.scraper.get(url).content
            match = re.compile('<div><iframe src="(.+?)"').findall(r)
            for url in match:
                host = url.split('//')[1].replace('www.', '')
                host = host.split('/')[0].split('.')[0].title()
                quality = source_utils.check_sd_url(url)
                r = self.scraper.get(url).content
                if 'http' in url:
                    match = re.compile("url: '(.+?)',").findall(r)
                else:
                    match = re.compile('file: "(.+?)",').findall(r)
                for url in match:
                    sources.append(
                        {'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False,
                         'debridonly': False})
        except:
            return
        return sources

    def resolve(self, url):
        return url
