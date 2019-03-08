# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: Mr.Blamo

import json
import re
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['netzkino.de']
        self.base_link = 'http://netzkino.de'
        self.conf_link = '/adconf/android-new.php'
        self.search_link = 'http://api.netzkino.de.simplecache.net/capi-2.0a/search?q=%s&d=www&l=de-DE&v=unknown-debugBuild'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), imdb, year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), imdb, year)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            r = client.request(urlparse.urljoin(self.base_link, self.conf_link), XHR=True)
            r = json.loads(r).get('streamer')
            r = client.request(r + '%s.mp4/master.m3u8' % url, XHR=True)

            r = re.findall('RESOLUTION\s*=\s*\d+x(\d+).*?\n(http.*?)(?:\n|$)', r, re.IGNORECASE)
            r = [(source_utils.label_to_quality(i[0]), i[1]) for i in r]

            for quality, link in r:
                sources.append({'source': 'CDN', 'quality': quality, 'language': 'de', 'url': link, 'direct': True, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles, imdb, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query, XHR=True)
            r = json.loads(r)

            r = [(i.get('title'), i.get('custom_fields', {})) for i in r.get('posts', [])]
            r = [(i[0], i[1]) for i in r if i[0] and i[1]]
            r = [(i[0], i[1].get('Streaming', ['']), i[1].get('Jahr', ['0']), i[1].get('IMDb-Link', [''])) for i in r if i]
            r = [(i[0], i[1][0], i[2][0], re.findall('.+?(tt\d+).*?', i[3][0])) for i in r if i[0] and i[1] and i[2] and i[3]]
            r = [i[1] for i in r if imdb in i[3] or (cleantitle.get(i[0]) in t and i[2] in y)][0]

            return source_utils.strip_domain(r)
        except:
            return
