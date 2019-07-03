# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

# -Cleaned and Checked on 05-06-2019 by JewBMX in Scrubs.

import re

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['ffilms.org']
        self.base_link = 'https://ffilms.org'
        self.movie_link = '/%s-%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title)
            url = self.base_link + self.movie_link % (title, year)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        if url is None:
            return sources
        try:
            r = self.scraper.get(url).content
            match = re.compile('src="//ok\.ru/videoembed/(.+?)"').findall(r)
            for vid in match:
                url = 'https://ok.ru/videoembed/' + vid
                sources.append({'source': 'ok', 'quality': 'HD', 'language': 'en', 'url': url, 'direct': False,
                                'debridonly': False})
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url
