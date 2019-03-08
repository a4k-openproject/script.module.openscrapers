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

import re
import urllib
import urlparse
import itertools
import HTMLParser

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['lichtspielhaus.stream']
        self.base_link = 'http://lichtspielhaus.stream'
        self.search_link = '/?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases))
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            s = '-%sx%s/' % (season, episode)

            url = url.rstrip('/')
            url = '/episode' + url + s

            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            query = urlparse.urljoin(self.base_link, url)
            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'TpRwCont'})
            r = dom_parser.parse_dom(r, 'main')

            options1 = dom_parser.parse_dom(r, 'li', attrs={'class': 'STPb'})
            options2 = dom_parser.parse_dom(r, 'div', attrs={'class': 'TPlayerTb'})

            for o1,o2 in itertools.izip(options1,options2):
                if 'trailer' in o1[1].lower():
                    continue
                elif '1080p' in o1[1].lower():
                    quality = '1080p'
                elif '720p' in o1[1].lower():
                    quality = 'HD'
                else:
                    quality = 'SD'

                s = '(?<=src=\")(.*?)(?=\")'
                if re.match(s, o2[1]) is not None:
                    url = re.search(s, o2[1]).group()
                else:
                    h = HTMLParser.HTMLParser()
                    h = h.unescape(o2[1])
                    url = re.search(s, h).group()

                valid, hoster = source_utils.is_host_valid(url, hostDict)
                if not valid: continue

                sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': url, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'MovieList'})
            r = dom_parser.parse_dom(r, 'li', attrs={'class': 'TPostMv'})
            r = dom_parser.parse_dom(r, 'a')

            for i in r:
                title = dom_parser.parse_dom(i, 'h2', attrs={'class': 'Title'})
                title = cleantitle.get(title[0][1])
                if title in t:
                    return source_utils.strip_domain(i[0]['href'])
        except:
            return
