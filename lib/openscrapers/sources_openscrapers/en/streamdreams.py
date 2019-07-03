# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 06-08-2019 by JewBMX in Scrubs.
# Created by Tempest

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['streamdreams.org']
        self.base_link = 'https://streamdreams.org'
        self.search_movie = '/movies/%s'
        self.search_tv = '/shows/%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title)
            url = self.base_link + self.search_movie % title
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
            url = self.base_link + self.search_tv % url
            url = url + '?session=%s&episode=%s' % (season, episode)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            hostDict = hostprDict + hostDict
            headers = {'Referer': url}
            r = self.scraper.get(url, headers=headers).content
            u = client.parseDOM(r, "span", attrs={"class": "movie_version_link"})
            for t in u:
                match = client.parseDOM(t, 'a', ret='data-href')
                for url in match:
                    if 'BDRip' in url:
                        quality = '720p'
                    elif 'HD' in url:
                        quality = '720p'
                    else:
                        quality = 'SD'
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if valid:
                        sources.append(
                            {'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False,
                             'debridonly': False})
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
