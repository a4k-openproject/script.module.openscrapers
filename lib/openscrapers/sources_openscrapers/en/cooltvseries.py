# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 03-16-2019 by JewBMX in Scrubs.

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re,urllib,urlparse
from openscrapers.modules import client,cleantitle,proxy,source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['cooltvseries.com']
        self.base_link = 'https://cooltvseries.com'
        self.search_link = '/%s/season-%s/'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = cleantitle.geturl(tvshowtitle)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            http = self.base_link + self.search_link % (url,season)
            season = '%02d' % int(season)
            episode = '%02d' % int(episode)
            r = client.request(http)
            match = re.compile('<a href="(.+?)-S'+season+'E'+episode+'-(.+?)">').findall(r)
            for url1,url2 in match:
                url = '%s-S%sE%s-%s' % (url1,season,episode,url2)
                return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = client.request(url)
            try:
                match = re.compile('<li><a href="(.+?)" rel="nofollow">(.+?)<').findall(r)
                for url,check in match: 
                    info = source_utils.check_url(url)
                    quality = source_utils.check_url(url)
                    sources.append({ 'source': 'Direct', 'quality': quality, 'language': 'en', 'info': info, 'url': url, 'direct': False, 'debridonly': False }) 
            except:
                return
        except Exception:
            return
        return sources


    def resolve(self, url):
        return url

