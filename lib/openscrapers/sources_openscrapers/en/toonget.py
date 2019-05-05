# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 03-07-2019 by JewBMX in Scrubs.

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


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.genre_filter = ['animation', 'anime']
        self.domains = ['toonget.net']
        self.base_link = 'https://toonget.net'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title)
            url = '%s-%s' % (title, year)
            url = self.base_link + '/' + url
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
        try:
            sources = []
            r = self.scraper.get(url).content
            try:
                match = re.compile('<iframe src="(.+?)"').findall(r)
                for url in match:
                    r = self.scraper.get(url).content
                    if 'playpanda' in url:
                        match = re.compile("url: '(.+?)',").findall(r)
                    else:
                        match = re.compile('file: "(.+?)",').findall(r)
                    for url in match:
                        sources.append(
                            {'source': 'Direct', 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False,
                             'debridonly': False})
            except:
                return
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url
