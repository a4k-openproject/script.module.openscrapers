# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 03-17-2019 by JewBMX in Scrubs.

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re,urllib,urlparse
from openscrapers.modules import client,cleantitle,source_utils,proxy


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watchseries.fi', 'watchseries.si'] # old  watchseries.sk
        self.base_link = 'http://watchseries.si'
        self.search_link = '/series/%s/season/%s/episode/%s/'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = cleantitle.geturl(tvshowtitle)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            url = self.base_link + self.search_link % (url,season,episode)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = client.request(url)
            try:
                match = re.compile('href="(.+?)" rel="noindex\,nofollow">Watch This Link</a>').findall(r)
                for url in match: 
                    r = client.request(url)
                    match = re.compile('<a href="(.+?)://(.+?)/(.+?)"><button class="wpb\_button  wpb\_btn\-primary wpb\_regularsize"> Click Here To Play</button> </a>').findall(r)
                    for http,host,url in match: 
                        url = '%s://%s/%s' % (http,host,url)
                        info = source_utils.check_url(url)
                        quality = source_utils.check_url(url)
                        valid, host = source_utils.is_host_valid(host, hostDict)
                        if valid:
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url, 'direct': False, 'debridonly': False}) 
            except:
                return
        except Exception:
            return
        return sources


    def resolve(self, url):
        return url

